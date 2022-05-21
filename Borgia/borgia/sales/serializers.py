from rest_framework.response import Response
from operator import itemgetter
from rest_framework import viewsets
from django.db.models import Sum
from rest_framework import serializers

from users.serializers import UserSerializer

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
        # with open("/borgia-serv/Borgia/borgia/sales/test.text", "a") as o:
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
            'id': instance.id,
            'username': instance.username,
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


class RankUserAllPurchaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'surname': instance.surname,
            'montant_achats': float(SaleProduct.objects.filter(sale__sender__username=instance.username).aggregate(Sum('price'))['price__sum'] or 0),
            'qte_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).count(),
        }


class UserRankByShopSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'surname': instance.surname,
            'montant_achats_par_shop': float(SaleProduct.objects.filter(sale__sender__username=instance.username, sale__shop=self.context.get("shop_id")).aggregate(Sum('price'))['price__sum'] or 0),
        }


class UserRankByShopViewSet(viewsets.ViewSet):
    def list(self, request, id):
        queryset = User.objects.all()
        serializer = UserRankByShopSerializer(
            queryset, many=True, context={"shop_id": id})
        sortedList = sorted(serializer.data, key=itemgetter(
            'montant_achats_par_shop'), reverse=True)[:10]
        return Response(sortedList)

from rest_framework.decorators import api_view

@api_view(['GET'])
def all_high_scores(request):
    queryset = User.objects.order_by('-balance')
    serializer = StatPurchaseSerializer(queryset, many=True)
    return Response(serializer.data)

#@api_view(['GET'])

def toptenUserView(id):
        queryset = User.objects.all()
        serializer = UserRankByShopSerializer(
            queryset, many=True, context={"shop_id": id})
        sortedList = sorted(serializer.data, key=itemgetter(
            'montant_achats_par_shop'), reverse=True)[:10]
        #with open("/borgia-serv/Borgia/borgia/sales/test.text", "a") as o:
        #    o.write(str(sortedList) + "\n")
        return sortedList

class ShopUserRankSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'image': instance.image,
            'user_top_ten': toptenUserView(instance.id)
            # userTopTen(instance.id)
        }


""" def userTopTen(id):

    allUsers = User.objects.all()
    userserializer = UserSerializer
    userTopTenList = []

    queryset = User.objects.all()
    serializer = userserial(queryset, many=True)
    sortedList = sorted(serializer.data, key=itemgetter(
        'montant_achats'), reverse=True)[:10]
    return Response(sortedList)

    #serializer = ShopUserRankSerializer(queryset, many=True)

    [

        {
            'id': Shop.objects.filter(id=i).values('name'),
            'username': Shop.objects.filter(id=i).values('name'),
            'montant_achats': float(SaleProduct.objects.filter(sale__sender__username=instance.username).aggregate(Sum('price'))['price__sum'] or 0),
            'qte_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).count(),

        } for i in range(1, Shop.objects.count())


    ],

    return(userTopTenList)
 """
