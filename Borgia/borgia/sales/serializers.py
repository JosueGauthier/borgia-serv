from django.db.models import Sum
from rest_framework import serializers

from .models import *


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ('id', 'datetime', 'sender', 'recipient',
                  'operator', 'module_id', 'shop', 'products')


class SaleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleProduct
        fields = ('id', 'sale', 'product', 'quantity', 'price')
        depth = 1



class SaleStatSerializer(serializers.ModelSerializer):
    total_sale = serializers.SerializerMethodField(read_only=True)
    total_saleQty = serializers.SerializerMethodField(read_only=True)
    user_sales = serializers.SerializerMethodField(read_only=True)

    def get_total_sale(self, obj):
        totalsale = Sale.objects.all().aggregate(Sum('module_id'))
        return totalsale

    def get_user_sales(self, obj):
        totalsale = Sale.objects.filter(
            sender__username="73An220").aggregate(Sum('module_id'))
        #with open("/borgia-serv/Borgia/borgia/sales/test.text", "a") as o:
        #    o.write(str(obj) + "\n")
        return totalsale

    def get_total_saleQty(self, obj):
        return Sale.objects.all().count()

    class Meta:
        model = Sale
        fields = ('id', 'user_sales', 'total_sale', 'total_saleQty', 'datetime',
                  'sender', 'recipient', 'operator', 'module_id', 'shop', 'products')




class StatPurchaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id':instance.id,
            'username':instance.username,            
            'surname': instance.surname,
            'balance': instance.balance,
            'montant_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).aggregate(Sum('price')),
            'qte_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).count(),
            'montant_magasins': [

                {
                    'shop_name': Shop.objects.filter(id=i).values('name'),
                    'qte_user_achats': SaleProduct.objects.filter(sale__sender__username=instance.username, sale__shop=i).aggregate(Sum('price')),

                } for i in range(1, Shop.objects.count())


            ],

        }



class RankSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id':instance.id,
            'username':instance.username,            
            'surname': instance.surname,
            'montant_achats': float(SaleProduct.objects.filter(sale__sender__username=instance.username).aggregate(Sum('price'))['price__sum'] or 0),
            'qte_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).count(),
        }



""" [
    {'id': 1, 'username': 'AE_ENSAM', 'surname': None, 'montant_achats': {'price__sum': None}, 'qte_achats': 0}, 
    {'id': 3, 'username': '73An220', 'surname': 'Khalvin', 'montant_achats': {'price__sum': Decimal('54.90')}, 'qte_achats': 18}, 
    {'id': 4, 'username': '73Kin220', 'surname': 'gum', 'montant_achats': {'price__sum': None}, 'qte_achats': 0}
    
] """