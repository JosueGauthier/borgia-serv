from time import strftime
import datetime
from rest_framework.decorators import api_view
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


class HistorySaleUserSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):

        a = instance.datetime

        '%Y-%d-%m %H:%M:%S'

        # current dateTime
        #now = datetime.now()

        # convert to string
        #!work
        #date_time_str = a.strftime('%Y-%d-%m %H:%M:%S')

        all_date_time_str = a.strftime('%d %b %y %H:%M')

        #print('DateTime String:', date_time_str)

        #initDateTimeFormat = datetime.datetime.strptime(instance.datetime, '%Y-%m-%dT%H:%M:%S.%f')

        #initDateTimeFormat = strftime(instance.datetime, '%Y-%m-%dT%H:%M:%S.%f')

        #new_date = initDateTimeFormat.strftime('%Y-%m-%d %I:%M %p')

        """ d = datetime.datetime.strptime('2011-06-09', '%Y-%m-%d')
        d.strftime('%b %d,%Y')

        a_datetime=instance.datetime,

        a= datetime.datetime.strptime(a_datetime, '%d. %B %Y %H:%M')

        start_day = strftime(str((datetime.datetime.strptime(
            "2022-01-01", "%Y-%m-%d") + datetime.timedelta(days=i)).date()))

        format_day = (datetime.datetime.strptime(
            "2022-01-01", "%Y-%d-%m") + datetime.timedelta(days=i)).date()


        a_day = datetime.datetime.strptime(str(format_day), '%Y-%m-%d').strftime('%d-%m') """
        return {
            # 'id': instance.id,
            'format_datetime': all_date_time_str,
            # 'datetime': instance.datetime,
            # 'sender': instance.sender.id,
            # 'nb_type_de_prod': SaleProduct.objects.filter(sale__id=instance.id).count(),
            # 'tot_qty_per_sale': SaleProduct.objects.filter(sale__id=instance.id).aggregate(Sum('quantity'))['quantity__sum'],
            'tot_amount_per_sale': SaleProduct.objects.filter(sale__id=instance.id).aggregate(Sum('price'))['price__sum'],
        }


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
            'montant_achats': float(SaleProduct.objects.filter(sale__sender__username=instance.username).aggregate(Sum('price'))['price__sum'] or 0),
            'qte_achats': SaleProduct.objects.filter(sale__sender__username=instance.username).count(),
            'montant_magasins': [

                {
                    'shop_name': str(Shop.objects.filter(id=i).values('name')[0]['name']),
                    'shop_image': str(Shop.objects.filter(id=i).values('image')[0]['image']),
                    'qte_user_achats': SaleProduct.objects.filter(sale__sender__username=instance.username, sale__shop=i).count(),
                    'montant_achats': float(SaleProduct.objects.filter(sale__sender__username=instance.username, sale__shop=i).aggregate(Sum('price'))['price__sum'] or 0),

                } for i in range(1, Shop.objects.count()+1)


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
            'family': instance.family,
            'campus': instance.campus,
            'promotion': instance.year,
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


@api_view(['GET'])
def all_high_scores(request):
    queryset = User.objects.order_by('-balance')
    serializer = StatPurchaseSerializer(queryset, many=True)
    return Response(serializer.data)


def toptenUserView(id):
    queryset = User.objects.all()
    serializer = UserRankByShopSerializer(
        queryset, many=True, context={"shop_id": id})
    sortedList = sorted(serializer.data, key=itemgetter(
        'montant_achats_par_shop'), reverse=True)[:10]
    return sortedList


class ShopUserRankSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'image': instance.image,
            'user_top_ten': toptenUserView(instance.id)
        }
