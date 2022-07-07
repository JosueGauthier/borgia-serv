from asyncio.log import logger
from dataclasses import field
from itertools import product
from pyexpat import model
from unicodedata import category
from rest_framework import serializers
from shops.views import ProductBaseViewSet

from shops.serializers import ProductBaseSerializer


from .models import CategoryProduct, Category


from functools import partial, wraps
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from borgia.views import BorgiaFormView, BorgiaView
from configurations.utils import configuration_get
from modules.forms import (ModuleCategoryCreateForm,
                           ModuleCategoryCreateNameForm, ShopModuleConfigForm,
                           ShopModuleSaleForm)
from modules.mixins import ShopModuleCategoryMixin, ShopModuleMixin
from modules.models import Category, CategoryProduct, SelfSaleModule
from sales.models import Sale, SaleProduct
from shops.models import Product, Shop
from users.models import User


from django.contrib.contenttypes.models import ContentType


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ContentType
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'module_id', 'products',
                  'order', 'category_image', 'shop_id', 'content_type')




class CatBaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):

        listofProdId = CategoryProduct.objects.filter(
            category=instance.id).values_list('product_id')
        listOfProducts = []
        listdesID = []

        for i in range(len(listofProdId)):
            listdesID.append(listofProdId[i][0])

        for i in listdesID:
            listOfProducts.append(
                {
                    'id': i,
                    'name': Product.objects.filter(id=i).values_list('name')[0][0],
                    'unit': Product.objects.filter(id=i).values_list('unit')[0][0],
                    'shop': Product.objects.filter(id=i).values_list('shop')[0][0],
                    'is_manual': Product.objects.filter(id=i).values_list('is_manual')[0][0],
                    'manual_price': Product.objects.filter(id=i).values_list('manual_price')[0][0],
                    'correcting_factor': Product.objects.filter(id=i).values_list('correcting_factor')[0][0],
                    'is_active': Product.objects.filter(id=i).values_list('is_active')[0][0],
                    'is_removed': Product.objects.filter(id=i).values_list('is_removed')[0][0],
                    'product_image': Product.objects.filter(id=i).values_list('product_image')[0][0],
                    'id_parent_category': instance.id,
                    'module_id_parent_category': instance.module_id,
                    'id_categoryproduct_table': CategoryProduct.objects.filter(product=i).values_list('id')[0][0]

                }
            )

        return {

            'id': instance.id,
            'name': instance.name,
            'module_id': instance.module_id,
            'category_image': instance.category_image,
            'shop_id': instance.shop_id,
            'content_type': instance.content_type.model,
            'products': listOfProducts,
            


        }


class CategoryProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id', 'category', 'product', 'quantity')


class ProductCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id', 'category', 'product', 'quantity')


#! Self sale
class SelfSaleSerializer(serializers.Serializer):

    """
    This serializer defines  fields for self sales module :
        * api_operator
        * api_sender = api_operator
        * api_recipient
        * api_module
        * api_shop
        * api_ordered_quantity
        * api_category_product_id

    In views It will try to operate the sale method when validated.

        ? api_operator = User.objects.get(pk=7)
        ? api_sender = api_operator
        ? api_recipient = User.objects.get(pk=1)
        ? api_module = SelfSaleModule.objects.get(pk=3)
        ? api_shop =Shop.objects.get(pk=1)
        ? api_ordered_quantity = 3
        ? api_category_product_id= 82
    """

    """ api_operator_pk = serializers.IntegerField(
        label="id user",
        write_only=True
    ) """

    api_module_pk = serializers.IntegerField(
        label="id module",
        write_only=True
    )
    api_shop_pk = serializers.IntegerField(
        label="id shop",
        write_only=True
    )

    api_ordered_quantity = serializers.IntegerField(
        label="order quantity",
        write_only=True
    )

    api_category_product_id = serializers.IntegerField(
        label="id product",
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        #api_operator_pk = attrs.get('api_operator_pk')
        api_module_pk = attrs.get('api_module_pk')
        api_shop_pk = attrs.get('api_shop_pk')
        api_ordered_quantity = attrs.get('api_ordered_quantity')
        api_category_product_id = attrs.get('api_category_product_id')

        # api_operator_pk,

        attrs['sale'] = [api_module_pk, api_shop_pk,
                         api_ordered_quantity, api_category_product_id]
        return attrs


#! Operator sale
class OperatorSaleSerializer(serializers.Serializer):

    api_buyer_pk = serializers.IntegerField(
        write_only=True
    )

    api_module_pk = serializers.IntegerField(
        write_only=True
    )
    api_shop_pk = serializers.IntegerField(
        write_only=True
    )

    api_ordered_quantity = serializers.IntegerField(
        write_only=True
    )

    api_category_product_id = serializers.IntegerField(
        write_only=True
    )

    def validate(self, attrs):

        api_buyer_pk = attrs.get('api_buyer_pk')
        api_module_pk = attrs.get('api_module_pk')
        api_shop_pk = attrs.get('api_shop_pk')
        api_ordered_quantity = attrs.get('api_ordered_quantity')
        api_category_product_id = attrs.get('api_category_product_id')

        attrs['sale'] = [api_buyer_pk, api_module_pk, api_shop_pk,
                         api_ordered_quantity, api_category_product_id]
        return attrs
