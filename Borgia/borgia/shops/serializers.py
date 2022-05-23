"""
?Sérialisation d’objets Django
L’infrastructure de sérialisation de Django fournit un mécanisme pour « traduire » 
les modèles Django en d’autres formats. En général, ces autres formats sont basés 
sur du texte et utilisés pour envoyer des données de Django à travers le réseau, 
mais il est possible qu’un sérialiseur prenne en charge n’importe quel 
format (basé sur du texte ou non).

Remember, serialization is the process of converting a Model to JSON. Using a serializer,
 we can specify what fields should be present in the JSON representation of the model. """

"""La HyperlinkedModelSerializerclasse est similaire à la
 ModelSerializerclasse sauf qu'elle utilise des liens hypertexte 
pour représenter les relations, plutôt que des clés primaires."""




from django.db.models import Avg, Max, Min, Sum, Count, F
from rest_framework import serializers
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


class ShopStatSerializer(serializers.ModelSerializer):
    total_sale_of_shop = serializers.SerializerMethodField()
    total_sale_amount_of_shop = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id','image', 'name', 'total_sale_of_shop',
                  'total_sale_amount_of_shop')

    def get_total_sale_amount_of_shop(self, obj):
        totalsaleamountofshop = SaleProduct.objects.filter(
            sale__shop__id=obj.id).aggregate(Sum('price'))['price__sum']
        return totalsaleamountofshop

    def get_total_sale_of_shop(self, obj):
        totalsaleofshop = SaleProduct.objects.filter(
            sale__shop__id=obj.id).count()
        return totalsaleofshop
