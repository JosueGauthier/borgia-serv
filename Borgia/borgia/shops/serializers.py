from django.db.models import Avg, Max, Min, Sum, Count, F
from rest_framework import serializers
from modules.models import Category, CategoryProduct, OperatorSaleModule, SelfSaleModule
from sales.models import SaleProduct
from .models import Shop, Product


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'description', 'color', 'image', 'correcting_factor_activated')


class SelfSaleModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfSaleModule
        fields = '__all__'


class OperatorSaleModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorSaleModule
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    manual_price = serializers.FloatField()
    correcting_factor = serializers.FloatField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'unit', 'shop', 'is_manual', 'manual_price',
                  'correcting_factor', 'is_active', 'is_removed', 'product_image')


class CategoryProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id', 'category', 'product', 'quantity')


class ShopStatSerializer(serializers.ModelSerializer):
    total_sale_of_shop = serializers.SerializerMethodField()
    total_sale_amount_of_shop = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'image', 'name', 'total_sale_of_shop',
                  'total_sale_amount_of_shop')

    def get_total_sale_amount_of_shop(self, obj):
        totalsaleamountofshop = SaleProduct.objects.filter(
            sale__shop__id=obj.id).aggregate(Sum('price'))['price__sum']
        return totalsaleamountofshop

    def get_total_sale_of_shop(self, obj):
        totalsaleofshop = SaleProduct.objects.filter(
            sale__shop__id=obj.id).count()
        return totalsaleofshop


class ProductBaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):

        #! id_parent_category
        try:
            id_parent_category = Category.objects.filter(
                products=instance.id).values_list('id')[0][0]
        except:
            id_parent_category = 0

        #!module_id_parent_category
        try:
            module_id_parent_category = Category.objects.filter(products=instance.id).values_list('module_id')[0][0]
        except:
            module_id_parent_category = 0

        #! contentType_parent_category
        try:
            contentType_parent_category = Category.objects.filter(
                products=instance.id).values_list('content_type__model')[0][0]
        except:
            contentType_parent_category = 0

        #! id_categoryproduct_table
        try:
            id_categoryproduct_table = CategoryProduct.objects.filter(
                product=instance.id).values_list('id')[0][0]
        except:
            id_categoryproduct_table = 0

        return {
            'id': instance.id,
            'name': instance.name,
            'unit': instance.unit,
            'shop': instance.shop.id,
            'is_manual': instance.is_manual,
            'manual_price': instance.manual_price,
            'correcting_factor': instance.correcting_factor,
            'is_active': instance.is_active,
            'is_removed': instance.is_removed,
            'product_image': instance.product_image,
            'id_parent_category': id_parent_category,
            'module_id_parent_category': module_id_parent_category,
            'contentType_parent_category': contentType_parent_category,
            'id_categoryproduct_table': id_categoryproduct_table,
        }


class CreateShopSerializer(serializers.Serializer):

    shop_name = serializers.CharField(
        write_only=True
    )

    shop_description = serializers.CharField(
        write_only=True
    )

    shop_image = serializers.CharField(
        write_only=True
    )
    shop_color = serializers.CharField(
        write_only=True,
        required=False
    )
    correcting_factor_activated = serializers.CharField(
        write_only=True,
        required=False
    )

    def validate(self, attrs):

        shop_name = attrs.get('shop_name')
        shop_description = attrs.get('shop_description')
        shop_image = attrs.get('shop_image')
        shop_color = attrs.get('shop_color')
        correcting_factor_activated = attrs.get('correcting_factor_activated')

        attrs['shop'] = [shop_name, shop_description,
                         shop_image, shop_color, correcting_factor_activated]
        return attrs


class UpdateShopSerializer(serializers.Serializer):

    shop_id = serializers.IntegerField(
        write_only=True
    )

    shop_description = serializers.CharField(
        write_only=True,
        required=False
    )

    shop_image = serializers.CharField(
        write_only=True,
        required=False
    )
    
    correcting_factor_activated = serializers.BooleanField(
        write_only=True
    )

    def validate(self, attrs):

        shop_id = attrs.get('shop_id')
        shop_description = attrs.get('shop_description')
        shop_image = attrs.get('shop_image')
        correcting_factor_activated = attrs.get('correcting_factor_activated')

        attrs['shop'] = [shop_id, shop_description,
                         shop_image, correcting_factor_activated]
        return attrs


class DeleteShopSerializer(serializers.Serializer):

    shop_id = serializers.IntegerField(
        write_only=True
    )

    def validate(self, attrs):
        shop_id = attrs.get('shop_id')
        attrs['shop'] = [shop_id]
        return attrs


class CreateProductSerializer(serializers.Serializer):
    """
    :type name: string
    :type is_manual: bool
    :type manual_price: decimal
    :type shop:
    :type is_active: bool
    :type is_removed: bool
    :type unit: string
    :type correcting_factor: decimal
    :type product_image : string
    """

    product_name = serializers.CharField(
        write_only=True
    )

    price_is_manual = serializers.BooleanField(
        write_only=True
    )

    manual_price = serializers.DecimalField(
        write_only=True,
        decimal_places=2,
        max_digits=9,
    )
    shop_id = serializers.IntegerField(
        write_only=True,
    )

    is_active = serializers.BooleanField(
        write_only=True
    )

    product_unit = serializers.CharField(
        write_only=True,
        required=False

    )

    correcting_factor = serializers.DecimalField(
        write_only=True,
        decimal_places=4,
        max_digits=9,
    )

    product_image = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        product_name = attrs.get('product_name')
        price_is_manual = attrs.get('price_is_manual')
        manual_price = attrs.get('manual_price')
        shop_id = attrs.get('shop_id')
        is_active = attrs.get('is_active')
        product_unit = attrs.get('product_unit')
        correcting_factor = attrs.get('correcting_factor')
        product_image = attrs.get('product_image')

        attrs['product'] = [product_name, price_is_manual,
                            manual_price, shop_id, is_active, product_unit, correcting_factor, product_image]
        return attrs


class UpdateProductSerializer(serializers.Serializer):
    """
    :type name: string
    :type is_manual: bool
    :type manual_price: decimal
    :type is_active: bool
    :type unit: string
    :type correcting_factor: decimal
    :type product_image : string

    """

    product_id = serializers.CharField(
        write_only=True
    )

    product_name = serializers.CharField(
        write_only=True, required=False

    )

    price_is_manual = serializers.BooleanField(
        write_only=True, required=False
    )

    manual_price = serializers.DecimalField(
        write_only=True,
        decimal_places=2,
        max_digits=9,
        required=False,
    )

    is_active = serializers.BooleanField(
        write_only=True
    )

    product_unit = serializers.CharField(
        write_only=True,
        required=False,
    )

    correcting_factor = serializers.DecimalField(
        write_only=True,
        decimal_places=4,
        max_digits=9,
        required=False
    )

    product_image = serializers.CharField(
        write_only=True,
        required=False
    )

    def validate(self, attrs):

        product_id = attrs.get('product_id')
        product_name = attrs.get('product_name')
        price_is_manual = attrs.get('price_is_manual')
        manual_price = attrs.get('manual_price')
        is_active = attrs.get('is_active')
        product_unit = attrs.get('product_unit')
        correcting_factor = attrs.get('correcting_factor')
        product_image = attrs.get('product_image')

        attrs['product'] = [product_id, product_name, price_is_manual,
                            manual_price, is_active, product_unit, correcting_factor, product_image]
        return attrs


class DeleteProductSerializer(serializers.Serializer):
    """
    """

    product_id = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        product_id = attrs.get('product_id')
        attrs['product'] = [product_id]
        return attrs
