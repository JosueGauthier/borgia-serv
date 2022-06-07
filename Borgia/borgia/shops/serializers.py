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
            'id_categoryproduct_table': CategoryProduct.objects.filter(product=instance.id).values_list('id')[0][0],
        }
