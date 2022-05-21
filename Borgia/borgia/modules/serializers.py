from asyncio.log import logger
from rest_framework import serializers


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


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'module_id', 'products',
                  'order', 'category_image', 'shop_id')


class CategoryProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id', 'category', 'product', 'quantity')

class ProductCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id', 'category', 'product', 'quantity')


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

        #api_operator_pk,

        attrs['sale'] = [ api_module_pk, api_shop_pk,
                         api_ordered_quantity, api_category_product_id]
        return attrs
