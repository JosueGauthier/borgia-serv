from rest_framework import generics
from rest_framework import status
from django.contrib.auth import login, logout
from users.models import User
from users.serializers import LoginSerializer
from rest_framework import permissions
from rest_framework import views
from rest_framework.response import Response
from sales.models import Sale
from shops.models import Shop
from rest_framework import filters
from .serializers import *
from .models import Product, Shop
from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend
import datetime
import decimal

from borgia.views import BorgiaFormView, BorgiaView
from configurations.utils import configuration_get
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)

from django.shortcuts import redirect, render
from django.urls import reverse
from modules.models import CategoryProduct


from shops.forms import (ProductCreateForm, ProductListForm, ProductUpdateForm,
                         ProductUpdatePriceForm, ShopCheckupSearchForm,
                         ShopCreateForm, ShopUpdateForm)
from shops.mixins import ProductMixin, ShopMixin
from shops.models import Product, Shop


class ShopCreate(LoginRequiredMixin, PermissionRequiredMixin, BorgiaFormView):
    permission_required = 'shops.add_shop'
    menu_type = 'managers'
    template_name = 'shops/shop_create.html'
    lm_active = 'lm_shop_create'
    form_class = ShopCreateForm

    def __init__(self):
        self.shop = None

    def form_valid(self, form):
        """
        Create the shop instance and relating groups and permissions.
        """
        shop = Shop.objects.create(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            color=form.cleaned_data['color'],
            image=form.cleaned_data['image'],
            correcting_factor_activated=form.cleaned_data['correcting_factor_activated']
        )

        self.shop = shop
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_shop_checkup', kwargs={'shop_pk': self.shop.pk})


class ShopList(LoginRequiredMixin, PermissionRequiredMixin, BorgiaView):
    """
    View that list the shops.
    """
    permission_required = 'shops.view_shop'
    menu_type = 'managers'
    template_name = 'shops/shop_list.html'
    lm_active = 'lm_shop_list'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop_list'] = Shop.objects.all().order_by(
            'name')
        return render(request, self.template_name, context=context)


class ShopUpdate(ShopMixin, BorgiaFormView):
    permission_required = 'shops.change_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_update.html'
    form_class = ShopUpdateForm

    def get_initial(self):
        initial = super().get_initial()
        initial['description'] = self.shop.description
        initial['color'] = self.shop.color
        initial['image'] = self.shop.image
        initial['correcting_factor_activated'] = self.shop.correcting_factor_activated
        return initial

    def form_valid(self, form):
        self.shop.description = form.cleaned_data['description']
        self.shop.color = form.cleaned_data['color']
        self.shop.image = form.cleaned_data['image']
        self.shop.correcting_factor_activated = form.cleaned_data['correcting_factor_activated']
        self.shop.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_shop_checkup', kwargs={'shop_pk': self.shop.pk})


class ShopCheckup(ShopMixin, BorgiaFormView):
    """
    Display data about a shop.

    You can see checkup of your own shop only.
    If you're not a manager of a shop, you need the permission 'view_shop'
    """
    permission_required = 'shops.view_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_checkup.html'
    form_class = ShopCheckupSearchForm
    lm_active = 'lm_shop_checkup'

    date_begin = None
    date_end = None
    products = None
    sales_value = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock'] = self.info_stock()
        context['transaction'] = self.info_transaction()
        context['info'] = self.info_checkup()
        return context

    def get_form_kwargs(self):
        kwargs_form = super().get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']
        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']
        if form.cleaned_data['products']:
            self.products = form.cleaned_data['products']

        return self.get(self.request, self.args, self.kwargs)

    def info_sales(self, q_sales):
        current_month = False
        if self.date_begin is None:
            self.date_begin = datetime.date.today().replace(day=1)

        if self.date_end is None:
            self.date_end = datetime.date.today()

        q_sales = q_sales.filter(datetime__gte=self.date_begin)
        q_sales = q_sales.filter(datetime__lte=self.date_end)

        if self.products:
            q_sales = q_sales.filter(
                products__pk__in=[p.pk for p in self.products])

        if self.sales_value is None:
            self.sales_value = sum(s.amount() for s in q_sales)

        if self.date_begin == datetime.date.today().replace(day=1) and self.date_end == datetime.date.today():
            current_month = True

        return {
            'value': self.sales_value,
            'nb': q_sales.count(),
            'is_current_month': current_month
        }

    def info_stock(self):
        return {}

    def info_transaction(self):
        q_sales = Sale.objects.filter(shop=self.shop)
        info_sales = self.info_sales(q_sales)
        value = info_sales.get('value')
        nb = info_sales.get('nb')
        try:
            mean = round(value / nb, 2)
        except (ZeroDivisionError, decimal.DivisionByZero, decimal.DivisionUndefined):
            mean = 0
        return {
            'value': value,
            'nb': nb,
            'mean': mean
        }

    def info_checkup(self):
        q_sales = Sale.objects.filter(shop=self.shop)
        info_sales = self.info_sales(q_sales)
        sale_value = info_sales.get('value')
        sale_nb = info_sales.get('nb')
        current_month = info_sales.get('is_current_month')

        return {
            'sale': {
                'value': sale_value,
                'nb': sale_nb
            },
            'is_current_month': current_month,
            'date_begin': self.date_begin,
            'date_end': self.date_end
        }

    def get_initial(self):
        initial = super().get_initial()
        initial['date_begin'] = self.date_begin
        initial['date_end'] = self.date_end
        initial['products'] = self.products
        return initial


class ShopWorkboard(ShopMixin, BorgiaView):
    permission_required = 'shops.view_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_workboard.html'
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale_list'] = self.get_sales()
        context['purchase_list'] = self.get_purchases()
        return render(request, self.template_name, context=context)

    def get_sales(self):
        sales = {}
        s_list = Sale.objects.filter(shop=self.shop).order_by('-datetime')
        sales['weeks'] = self.weeklist(
            datetime.datetime.now() - datetime.timedelta(days=30),
            datetime.datetime.now())
        sales['data_weeks'] = self.sale_data_weeks(s_list, sales['weeks'])[0]
        sales['total'] = self.sale_data_weeks(s_list, sales['weeks'])[1]
        sales['all'] = s_list[:7]
        return sales

    # TODO: purchases with stock
    @staticmethod
    def get_purchases():
        purchases = {}
        return purchases

    # TODO: purchases with stock
    @staticmethod
    def purchase_data_weeks(weeks):
        amounts = [0 for _ in range(0, len(weeks))]
        total = 0

        return amounts, total

    @staticmethod
    def sale_data_weeks(weeklist, weeks):
        amounts = [0 for _ in range(0, len(weeks))]
        total = 0
        for obj in weeklist:
            string = (str(obj.datetime.isocalendar()[1])
                      + '-' + str(obj.datetime.year))
            if string in weeks:
                amounts[weeks.index(string)] += obj.amount()
                total += obj.amount()
        return amounts, total

    @staticmethod
    def weeklist(start, end):
        weeklist = []
        for i in range(start.year, end.year+1):
            week_start = 1
            week_end = 52
            if i == start.year:
                week_start = start.isocalendar()[1]
            if i == end.year:
                week_end = end.isocalendar()[1]
            weeklist += [str(j) + '-' + str(i) for j in range(
                week_start, week_end+1)]
        return weeklist


class ProductList(ShopMixin, BorgiaFormView):
    permission_required = 'shops.view_product'
    menu_type = 'shops'
    template_name = 'shops/product_list.html'
    form_class = ProductListForm
    lm_active = 'lm_product_list'

    search = None

    def get_initial(self):
        initial = super().get_initial()
        if self.search:
            initial['search'] = self.search
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.shop.product_set.filter(is_removed=False)
        if self.search:
            query = query.filter(name__icontains=self.search)
        context['product_list'] = query
        return context

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']
        return self.get(self.request, self.args, self.kwargs)


class ProductCreate(ShopMixin, BorgiaFormView):
    permission_required = 'shops.add_product'
    menu_type = 'shops'
    template_name = 'shops/product_create.html'
    form_class = ProductCreateForm
    lm_active = 'lm_product_create'

    def __init__(self):
        super().__init__()
        self.product = None

    def get_initial(self):
        initial = super().get_initial()
        initial['on_quantity'] = False
        return initial

    def form_valid(self, form):
        if form.cleaned_data['on_quantity']:
            product = Product.objects.create(
                name=form.cleaned_data['name'],
                product_image=form.cleaned_data['product_image'],
                shop=self.shop,
                unit=form.cleaned_data['unit'],
                correcting_factor=1
            )
        else:
            product = Product.objects.create(
                name=form.cleaned_data['name'],
                product_image=form.cleaned_data['product_image'],
                shop=self.shop,
                correcting_factor=1
            )
        self.product = product
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve', kwargs={
            'shop_pk': self.shop.pk,
            'product_pk': self.product.pk})


class ProductDeactivate(ProductMixin, BorgiaView):
    """
    Deactivate a product and redirect to the retrieve of the product.
    """
    permission_required = 'shops.delete_product'
    menu_type = 'shops'
    template_name = 'shops/product_deactivate.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set to True or False, activation is reversible.
        if self.product.is_active is True:
            self.product.is_active = False
        else:
            self.product.is_active = True
        self.product.save()

        return redirect(reverse('url_product_retrieve',
                                kwargs={'shop_pk': self.shop.pk,
                                        'product_pk': self.product.pk}))


class ProductRemove(ProductMixin, BorgiaView):
    """
    Remove a product and redirect to the list of products.
    """
    permission_required = 'shops.change_product'
    menu_type = 'shops'
    template_name = 'shops/product_remove.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set always to True, removing is non-reversible.
        self.product.is_removed = True
        self.product.save()

        # Delete all category_product which use the product.
        CategoryProduct.objects.filter(product=self.product).delete()

        return redirect(reverse('url_product_list', kwargs={'shop_pk': self.shop.pk}))


class ProductRetrieve(ProductMixin, BorgiaView):
    """
    Retrieve a Product.

    :param kwargs['shop_pk']: name of the group used.
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.view_product'
    menu_type = 'shops'
    template_name = 'shops/product_retrieve.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class ProductUpdate(ProductMixin, BorgiaFormView):
    """
    Update a product and redirect to the product.

    :param kwargs['shop_pk']: pk of the shop
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.change_product'
    menu_type = 'shops'
    template_name = 'shops/product_update.html'
    form_class = ProductUpdateForm
    model = Product

    def get_initial(self):
        initial = super().get_initial()
        initial['name'] = self.product.name
        initial['product_image'] = self.product.product_image
        return initial

    def form_valid(self, form):
        self.product.name = form.cleaned_data['name']
        self.product.product_image = form.cleaned_data['product_image']
        self.product.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve',
                       kwargs={'shop_pk': self.shop.pk,
                               'product_pk': self.product.pk})


class ProductUpdatePrice(ProductMixin, BorgiaFormView):
    """
    Update the price of a product and redirect to the product.

    :param kwargs['shop_pk']: pk of the shop
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.change_price_product'
    menu_type = 'shops'
    template_name = 'shops/product_update_price.html'
    form_class = ProductUpdatePriceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['margin_profit'] = configuration_get(
            'MARGIN_PROFIT').get_value()
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['is_manual'] = self.product.is_manual
        initial['manual_price'] = self.product.manual_price
        return initial

    def form_valid(self, form):
        self.product.is_manual = form.cleaned_data['is_manual']
        self.product.manual_price = form.cleaned_data['manual_price']
        self.product.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve',
                       kwargs={'shop_pk': self.shop.pk,
                               'product_pk': self.product.pk})


# partie API


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all().order_by('name')
    serializer_class = ShopSerializer


class ProductFromShopViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['shop', 'name']


class SearchProductView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SearchShopView(generics.ListCreateAPIView):
    queryset = Shop.objects.all().order_by('name')
    serializer_class = ShopSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class StatShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopStatSerializer


class ProductBaseViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Product.objects.all()

        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        id = self.request.query_params.get('id')
        if id is not None:
            queryset = queryset.filter(id=id)

        shop = self.request.query_params.get('shop')
        if shop is not None:
            queryset = queryset.filter(shop=shop)

        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(id_parent_category=category)

        serializer = ProductBaseSerializer(queryset, many=True)
        return Response(serializer.data)


def create_shop_api_function(shop_name, shop_description, shop_image, correcting_factor_activated=True, shop_color="#F4FA58"):

    if shop_name and shop_description and shop_color and shop_image and (correcting_factor_activated !=None):
        Shop.objects.create(
            name=shop_name,
            description=shop_description,
            color=shop_color,
            image=shop_image,
            correcting_factor_activated=correcting_factor_activated
        )


class CreateShopView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.add_shop'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        """  f = open("myfile.txt", "a")
        f.write("\n" + str(user)) """

        serializerCreateShop = CreateShopSerializer(
            data=self.request.data, context={'request': self.request})

        serializerCreateShop.is_valid(raise_exception=True)

        shopMap = serializerCreateShop.validated_data

        create_shop_api_function(
            shopMap['shop_name'], shopMap['shop_description'], shopMap['shop_image'])

        return Response(None, status=status.HTTP_202_ACCEPTED)


def update_shop_api_function(shop_id, shop_description=None, shop_image=None, correcting_factor_activated=True, shop_color="#F4FA58"):

    shop = Shop.objects.get(id=shop_id)

    """  f = open("myfile.txt", "a")
    f.write("\n" + str(shop.get_managers())) """

    if shop_description:
        shop.description = shop_description
        shop.save()

    if shop_image:
        shop.image = shop_image
        shop.save()


class UpdateShopView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.change_shop'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        #user = User.models
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        serializerUpdateShop = UpdateShopSerializer(
            data=self.request.data, context={'request': self.request})

        serializerUpdateShop.is_valid(raise_exception=True)

        shopMap = serializerUpdateShop.validated_data

        shop_id = shopMap['shop_id']

        if 'shop_description' in shopMap:
            shop_description = shopMap['shop_description']
        else:
            shop_description = None

        if 'shop_image' in shopMap:
            shop_image = shopMap['shop_image']
        else:
            shop_image = None

        update_shop_api_function(
            shop_id, shop_description, shop_image)

        return Response(None, status=status.HTTP_202_ACCEPTED)

#! Not used check db errrors before


def delete_shop_api_function(shop_id):

    shop = Shop.objects.get(id=shop_id)
    shop.delete()

#! Not used check db errrors before


class DeleteShopView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.delete_shop'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        serializerDeleteShop = DeleteShopSerializer(
            data=self.request.data, context={'request': self.request})

        serializerDeleteShop.is_valid(raise_exception=True)

        shopMap = serializerDeleteShop.validated_data

        shop_id = shopMap['shop_id']

        delete_shop_api_function(shop_id)

        return Response(None, status=status.HTTP_202_ACCEPTED)


def create_product_api_function(product_name, price_is_manual, manual_price, shop_id, is_active, product_unit, correcting_factor, product_image):

    if product_name and (price_is_manual  != None) and shop_id and (is_active != None ) and correcting_factor and product_image and manual_price:

        if product_unit != None:
            Product.objects.create(
                name=product_name,
                product_image=product_image,
                shop=Shop.objects.get(id=shop_id),
                unit=product_unit,  # ! voir pk ne marche pas via API achat et cie
                correcting_factor=correcting_factor,
                is_active=is_active,
                is_removed=False,
                is_manual=price_is_manual,
                manual_price=manual_price
            )
        else:
            Product.objects.create(
                name=product_name,
                product_image=product_image,
                shop=Shop.objects.get(id=shop_id),
                correcting_factor=correcting_factor,
                is_active=is_active,
                is_removed=False,
                is_manual=price_is_manual,
                manual_price=manual_price
            )


class CreateProductView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.add_product'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        serializerCreateProduct = CreateProductSerializer(
            data=self.request.data, context={'request': self.request})

        serializerCreateProduct.is_valid(raise_exception=True)

        productMap = serializerCreateProduct.validated_data

        if 'product_unit' in productMap:
            product_unit = productMap['product_unit']
        else:
            product_unit = None

        create_product_api_function(productMap['product_name'], productMap['price_is_manual'], productMap['manual_price'], productMap['shop_id'],
                                    productMap['is_active'], product_unit, productMap['correcting_factor'], productMap['product_image'])

        return Response(None, status=status.HTTP_202_ACCEPTED)


def update_product_api_function(product_id, product_name=None, price_is_manual=None, manual_price=None, is_active=None, product_unit=None, correcting_factor=None, product_image=None):

    if product_id:

        product = Product.objects.get(id=product_id)

        if product_name != None:
            product.name = product_name

        if price_is_manual != None:
            product.is_manual = price_is_manual

        if product_name != None:
            product.manual_price = manual_price

        if is_active != None:
            product.is_active = is_active

        if product_unit != None:
            product.unit = product_unit

        if correcting_factor != None:
            product.correcting_factor = correcting_factor

        if product_image != None:
            product.product_image = product_image

        product.save()


class UpdateProductView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.change_product'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        serializerUpdateProduct = UpdateProductSerializer(
            data=self.request.data, context={'request': self.request})

        serializerUpdateProduct.is_valid(raise_exception=True)

        productMap = serializerUpdateProduct.validated_data

        if 'product_name' in productMap:
            product_name = productMap['product_name']
        else:
            product_name = None

        if 'price_is_manual' in productMap:
            price_is_manual = productMap['price_is_manual']
        else:
            price_is_manual = None

        if 'manual_price' in productMap:
            manual_price = productMap['manual_price']
        else:
            manual_price = None

        if 'is_active' in productMap:
            is_active = productMap['is_active']
        else:
            is_active = None

        if 'product_unit' in productMap:
            product_unit = productMap['product_unit']
        else:
            product_unit = None

        if 'correcting_factor' in productMap:
            correcting_factor = productMap['correcting_factor']
        else:
            correcting_factor = None

        if 'product_image' in productMap:
            product_image = productMap['product_image']
        else:
            product_image = None

        update_product_api_function(productMap['product_id'], product_name, price_is_manual,
                                    manual_price, is_active, product_unit, correcting_factor, product_image)

        return Response(None, status=status.HTTP_202_ACCEPTED)



def delete_product_api_function(product_id):

    if product_id:

        product = Product.objects.get(id=product_id)
        product.is_removed = True
        product.save()


class DeleteProductView(views.APIView):

    permission_classes = (permissions.AllowAny,)
    permission_required = 'shops.delete_product'

    def post(self, request):
        #! Utilisateur manager se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={'request': self.request})
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data['user']

        if user.has_perm(self.permission_required) == False:
            return Response({"Error": "User does not have permission to perform the requested action"}, status=status.HTTP_401_UNAUTHORIZED)

        logout(request)
        login(request, user)

        serializerDeleteProduct = DeleteProductSerializer(
            data=self.request.data, context={'request': self.request})

        serializerDeleteProduct.is_valid(raise_exception=True)

        productMap = serializerDeleteProduct.validated_data

        delete_product_api_function(productMap['product_id'])

        return Response(None, status=status.HTTP_202_ACCEPTED)