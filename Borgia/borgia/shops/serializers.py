from django.db.models import Avg, Max, Min, Sum, Count, F
from rest_framework import serializers
from modules.models import Category, CategoryProduct
from sales.models import SaleProduct
from .models import Shop, Product


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'description', 'color', 'image')


class ProductSerializer(serializers.ModelSerializer):
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
            'id_parent_category': Category.objects.filter(products=instance.id).values_list('id')[0][0],
            'module_id_parent_category': Category.objects.filter(products=instance.id).values_list('module_id')[0][0],
            'contentType_parent_category': Category.objects.filter(products=instance.id).values_list('content_type__model')[0][0],
            'id_categoryproduct_table': CategoryProduct.objects.filter(product=instance.id).values_list('id')[0][0],
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

    def validate(self, attrs):

        shop_id = attrs.get('shop_id')
        shop_description = attrs.get('shop_description')
        shop_image = attrs.get('shop_image')

        attrs['shop'] = [shop_id, shop_description,
                         shop_image]
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
    :param name: Display name, mandatory.
    :param is_manual: is the price set manually.
    :param manual_price: price if set manually.
    :param shop: Related shop.
    :param is_active: is the product used.
    :param is_removed: is the product removed.
    :param unit: unit of the product.
    :param correcting_factor: for automatic price.
    :param product_image : image of the product, currently via Cloudinary

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
