import logging
from functools import partial, wraps

from borgia.views import BorgiaFormView, BorgiaView
from configurations.utils import configuration_get
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from modules.forms import (
    ModuleCategoryCreateForm,
    ModuleCategoryCreateNameForm,
    ShopModuleConfigForm,
    ShopModuleSaleForm,
)
from modules.mixins import ShopModuleCategoryMixin, ShopModuleMixin
from modules.models import Category, CategoryProduct, SelfSaleModule
from rest_framework import filters, generics, permissions, status, views, viewsets
from rest_framework.response import Response
from sales.models import Sale, SaleProduct
from shops.models import Product, Shop
from shops.serializers import SearchAllProductSerializer, ShopSerializer
from users.models import User
from users.serializers import LoginSerializer

from .models import Category, CategoryProduct
from .serializers import (
    CatBaseSerializer,
    CategorySerializer,
    CreateCategorySerializer,
    DeleteCategorySerializer,
    OperatorSaleSerializer,
    SelfSaleSerializer,
    UpdateCategorySerializer,
)

logger = logging.getLogger(__name__)


class ShopModuleSaleView(ShopModuleMixin, BorgiaFormView):
    """
    Generic FormView for handling invoice concerning product bases through a
    shop.

    :param self.template_name: template, mandatory.
    :param self.form_class: form class, mandatory.
    :param self.permission_required_selfsale: permission to check for self sale
    :param self.permission_required_operatorsale: permission to check for operator sale
    :type self.template_name: string
    :type self.form_class: Form class object
    :type self.permission_required_selfsale: string
    :type self.permission_required_operatorsale: string
    """

    permission_required_self = "modules.use_selfsalemodule"
    permission_required_operator = "modules.use_operatorsalemodule"
    template_name = "modules/shop_module_sale.html"
    form_class = ShopModuleSaleForm

    def has_permission(self):
        if self.kwargs["module_class"] == "self_sales":
            has_perms = self.has_permission_selfsales()
        else:
            has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            if self.module.state is False:
                raise Http404
            else:
                return True

    def has_permission_selfsales(self):
        """
        Customized permission for self_sale in shops.
        The user still need the use_selfsalemodule permission
        """
        self.add_context_objects()
        return PermissionRequiredMixin.has_permission(self)

    def get_menu_type(self):
        if self.module_class == "self_sales":
            return "members"
        elif self.module_class == "operator_sales":
            return "shops"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["module_class"] = self.module_class
        kwargs["module"] = self.module
        kwargs["balance_threshold_purchase"] = configuration_get(
            "BALANCE_THRESHOLD_PURCHASE"
        )

        if self.module_class == "self_sales":
            kwargs["client"] = self.request.user
        elif self.module_class == "operator_sales":
            kwargs["client"] = None
        else:
            self.handle_unexpected_module_class()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = self.module.categories.all().order_by("order")

        return context

    #! Module de paiement
    def form_valid(self, form):
        """
        Create a sale and like all products via SaleProduct objects.
        """
        if self.module_class == "self_sales":
            client = self.request.user
        elif self.module_class == "operator_sales":
            client = form.cleaned_data["client"]
        else:
            self.handle_unexpected_module_class()

        sale = Sale.objects.create(
            operator=self.request.user,
            sender=client,
            recipient=User.objects.get(pk=1),
            module=self.module,
            shop=self.shop,
        )
        for field in form.cleaned_data:
            if (
                field != "client"
                and form.cleaned_data[field] != ""
                and form.cleaned_data[field] is not None
            ):
                invoice = int(form.cleaned_data[field])
                if invoice > 0:
                    try:
                        category_product = CategoryProduct.objects.get(
                            pk=field.split("-")[0]
                        )
                    except ObjectDoesNotExist:
                        pass
                    else:
                        SaleProduct.objects.create(
                            sale=sale,
                            product=category_product.product,
                            quantity=category_product.quantity * invoice,
                            price=category_product.get_price() * invoice,
                        )
        sale.pay()

        context = self.get_context_data()

        if self.module.logout_post_purchase:
            success_url = reverse("url_logout") + "?next=" + self.get_success_url()
        else:
            success_url = self.get_success_url()
        context["sale"] = sale
        context["delay"] = self.module.delay_post_purchase
        context["success_url"] = success_url

        return sale_shop_module_resume(self.request, context)

    def get_success_url(self):
        return reverse(
            "url_shop_module_sale",
            kwargs={"shop_pk": self.shop.pk, "module_class": self.module_class},
        )


def sale_shop_module_resume(request, context):
    """
    Display shop module resume after a sale
    """
    template_name = "modules/shop_module_sale_resume.html"
    return render(request, template_name, context=context)


class ShopModuleConfigView(ShopModuleMixin, BorgiaView):
    """
    ConfigView for a shopModule.
    """

    permission_required_self = "modules.view_config_selfsalemodule"
    permission_required_operator = "modules.view_config_operatorsalemodule"
    menu_type = "shops"
    template_name = "modules/shop_module_config.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["type"] = "self_sale"
        return render(request, self.template_name, context=context)


class ShopModuleConfigUpdateView(ShopModuleMixin, BorgiaFormView):
    """
    View to manage config of a self shop module.
    """

    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"
    menu_type = "shops"
    template_name = "modules/shop_module_config_update.html"
    form_class = ShopModuleConfigForm

    def get_initial(self):
        initial = super(ShopModuleConfigUpdateView, self).get_initial()
        initial["state"] = self.module.state
        initial["logout_post_purchase"] = self.module.logout_post_purchase
        initial["limit_purchase"] = self.module.limit_purchase
        if self.module.delay_post_purchase:
            initial["infinite_delay_post_purchase"] = False
        else:
            initial["infinite_delay_post_purchase"] = True
        initial["delay_post_purchase"] = self.module.delay_post_purchase
        return initial

    def form_valid(self, form):
        self.module.state = form.cleaned_data["state"]
        self.module.logout_post_purchase = form.cleaned_data["logout_post_purchase"]
        self.module.limit_purchase = form.cleaned_data["limit_purchase"]
        if form.cleaned_data["infinite_delay_post_purchase"] is True:
            self.module.delay_post_purchase = None
        else:
            self.module.delay_post_purchase = form.cleaned_data["delay_post_purchase"]
        self.module.save()
        return super(ShopModuleConfigUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            "url_shop_module_config",
            kwargs={"shop_pk": self.shop.pk, "module_class": self.module_class},
        )


class ShopModuleCategoryCreateView(ShopModuleMixin, BorgiaView):
    """ """

    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"
    menu_type = "shops"
    template_name = "modules/shop_module_category_create.html"

    def __init__(self):
        super().__init__()
        self.shop = None
        self.module_class = None
        self.form_class = None

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            self.form_class = formset_factory(
                wraps(ModuleCategoryCreateForm)(
                    partial(ModuleCategoryCreateForm, shop=self.shop)
                ),
                extra=1,
            )
            return True

    def get(self, request, *args, **kwargs):
        """
        permet d'afficher la page de vente
        """
        context = self.get_context_data(**kwargs)
        context["cat_form"] = self.form_class()
        context["cat_name_form"] = ModuleCategoryCreateNameForm(
            initial={"order": self.module.categories.all().count()}
        )
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """
        Permet de publier la creation d'une nouvelle categorie

        cat_name_form => renvoie une objet Form avec le nom et l'ordre entré
        self.module => Module de vente en libre service du magasin Pi
        """

        cat_name_form = ModuleCategoryCreateNameForm(request.POST)

        if cat_name_form.is_valid():
            category = Category.objects.create(
                name=cat_name_form.cleaned_data["name"],
                order=cat_name_form.cleaned_data["order"],
                module=self.module,
                # shop_id=self.shop.pk,
                category_image=cat_name_form.cleaned_data["category_image"],
            )

        cat_form = self.form_class(request.POST)

        for product_form in cat_form.cleaned_data:
            try:
                product = Product.objects.get(pk=product_form["product"].split("/")[0])
                if product.unit:
                    quantity = int(product_form["quantity"])
                else:
                    quantity = 1
                CategoryProduct.objects.create(
                    category=category, product=product, quantity=quantity
                )
            except ObjectDoesNotExist:
                pass
            except KeyError:
                pass
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Permet de ...

        self.module_class => self_sales
        self.shop.pk => affiche bien la pk du shop en question
        """
        return reverse(
            "url_shop_module_config",
            kwargs={"shop_pk": self.shop.pk, "module_class": self.module_class},
        )


class ShopModuleCategoryUpdateView(ShopModuleCategoryMixin, BorgiaView):
    """ """

    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"
    menu_type = "shops"
    template_name = "modules/shop_module_category_update.html"

    def __init__(self):
        super().__init__()
        self.shop = None
        self.module_class = None
        self.form_class = None

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            self.form_class = formset_factory(
                wraps(ModuleCategoryCreateForm)(
                    partial(ModuleCategoryCreateForm, shop=self.shop)
                ),
                extra=1,
            )
            return True

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        cat_form_data = [
            {
                "product": str(category_product.product.pk)
                + "/"
                + str(category_product.product.get_unit_display()),
                "quantity": category_product.quantity,
            }
            for category_product in self.category.categoryproduct_set.all()
        ]
        context["cat_form"] = self.form_class(initial=cat_form_data)
        context["cat_name_form"] = ModuleCategoryCreateNameForm(
            initial={
                "name": self.category.name,
                "order": self.category.order,
                "category_image": self.category.category_image,
            }
        )
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        cat_name_form = ModuleCategoryCreateNameForm(request.POST)
        if cat_name_form.is_valid():
            self.category.name = cat_name_form.cleaned_data["name"]
            if cat_name_form.cleaned_data["order"] != self.category.order:
                shift_category_orders(
                    self.category, cat_name_form.cleaned_data["order"]
                )
            self.category.save()

        cat_form = self.form_class(request.POST)
        CategoryProduct.objects.filter(category=self.category).delete()
        for product_form in cat_form.cleaned_data:
            try:
                product = Product.objects.get(pk=product_form["product"].split("/")[0])
                if product.unit:
                    quantity = int(product_form["quantity"])
                else:
                    quantity = 1
                CategoryProduct.objects.create(
                    category=self.category, product=product, quantity=quantity
                )
            except ObjectDoesNotExist:
                pass
            except KeyError:
                pass
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "url_shop_module_config",
            kwargs={"shop_pk": self.shop.pk, "module_class": self.module_class},
        )


class ShopModuleCategoryDeleteView(ShopModuleCategoryMixin, BorgiaView):
    """ """

    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"
    menu_type = "shops"
    template_name = "modules/shop_module_category_delete.html"

    def __init__(self):
        super().__init__()
        self.shop = None
        self.module_class = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        CategoryProduct.objects.filter(category=self.category).delete()
        self.category.delete()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "url_shop_module_config",
            kwargs={"shop_pk": self.shop.pk, "module_class": self.module_class},
        )


def shift_category_orders(category, new_order):
    module_id = category.module_id
    content_type_id = category.content_type_id
    order = category.order
    if new_order < order:
        categories = Category.objects.filter(
            content_type_id=content_type_id,
            module_id=module_id,
            order__gte=new_order,
            order__lt=order,
        )
        if categories:
            for cat in categories:
                cat.order += 1
                cat.save()
    elif new_order > order:
        categories = Category.objects.filter(
            content_type_id=content_type_id,
            module_id=module_id,
            order__lte=new_order,
            order__gt=order,
        )
        if categories:
            for cat in categories:
                cat.order -= 1
                cat.save()
    category.order = int(new_order)
    category.save()


# ------------------
#: API part
# ------------------


class CatBaseViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = Category.objects.all()

        name = self.request.query_params.get("name")
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        id = self.request.query_params.get("id")
        if id is not None:
            queryset = queryset.filter(id=id)

        serializer = CatBaseSerializer(queryset, many=True)
        return Response(serializer.data)


# note : Self sale part
def api_create_self_sale_view(saleMap, api_user):
    """
    API permettant d'acheter un produit

    """

    api_operator = api_user
    api_sender = api_operator
    api_recipient = User.objects.get(pk=1)
    api_module = SelfSaleModule.objects.get(pk=saleMap["api_module_pk"])
    api_shop = Shop.objects.get(pk=saleMap["api_shop_pk"])
    api_ordered_quantity = saleMap["api_ordered_quantity"]
    api_category_product_id = saleMap["api_category_product_id"]

    sale = Sale.objects.create(
        operator=api_operator,
        sender=api_sender,
        recipient=api_recipient,
        module=api_module,
        shop=api_shop,
    )

    category_product = CategoryProduct.objects.get(pk=api_category_product_id)

    SaleProduct.objects.create(
        sale=sale,
        product=category_product.product,
        #! category_product.quantity = volume ou poids par item |  ordered quantity
        quantity=category_product.quantity * api_ordered_quantity,
        price=category_product.get_price() * api_ordered_quantity,
    )
    sale.pay()


class SelfSaleView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializerLogin = LoginSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data["user"]
        login(request, user)
        api_user = self.request.user
        serializerSale = SelfSaleSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializerSale.is_valid(raise_exception=True)
        saleMap = serializerSale.validated_data

        api_create_self_sale_view(saleMap, api_user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


# note :  Operator sale
class OperatorSaleView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializerLogin = LoginSerializer(
            data=self.request.data, context={"request": self.request}
        )

        serializerLogin.is_valid(raise_exception=True)

        user = serializerLogin.validated_data["user"]

        login(request, user)

        operator_user = self.request.user

        serializerSale = OperatorSaleSerializer(
            data=self.request.data, context={"request": self.request}
        )

        serializerSale.is_valid(raise_exception=True)

        saleMap = serializerSale.validated_data

        api_create_operator_sale_view(saleMap, operator_user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


def api_create_operator_sale_view(saleMap, operator_user):
    """
    API permettant à un operateur de vendre un produit

    """

    api_operator = operator_user
    api_sender = User.objects.get(pk=saleMap["api_buyer_pk"])
    api_recipient = User.objects.get(pk=1)
    api_module = SelfSaleModule.objects.get(pk=saleMap["api_module_pk"])
    api_shop = Shop.objects.get(pk=saleMap["api_shop_pk"])
    api_ordered_quantity = saleMap["api_ordered_quantity"]
    api_category_product_id = saleMap["api_category_product_id"]

    sale = Sale.objects.create(
        operator=api_operator,
        sender=api_sender,
        recipient=api_recipient,
        module=api_module,
        shop=api_shop,
    )

    category_product = CategoryProduct.objects.get(pk=api_category_product_id)

    SaleProduct.objects.create(
        sale=sale,
        product=category_product.product,
        #! category_product.quantity = volume ou poids par item |  ordered quantity
        quantity=category_product.quantity * api_ordered_quantity,
        price=category_product.get_price() * api_ordered_quantity,
    )
    sale.pay()


# note : Admin Create category


def create_category_api_function(
    shop,
    module_id,
    content_type_id,
    category_name=None,
    category_order=None,
    category_image=None,
    list_products=None,
):
    if category_name and category_order and category_image:
        category = Category.objects.create(
            name=category_name,
            order=category_order,
            module_id=module_id,
            content_type=ContentType.objects.get(id=content_type_id),
            # shop_id=shop.pk,
            category_image=category_image,
        )

    for product in list_products or []:
        # [{'quantity': 11, 'product': '2/unit'}, {'quantity': 2222, 'product': '6/unit'}]
        try:
            product = Product.objects.get(pk=product["product_id"])
            if product.unit:
                quantity = int(product["quantity"])
            else:
                quantity = 1
            CategoryProduct.objects.create(
                category=category, product=product, quantity=quantity
            )
        except ObjectDoesNotExist:
            pass
        except KeyError:
            pass


class CreateCategoryView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)
    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"

    def post(self, request, format=None):
        #! Utilisateur opérateur se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data["user"]

        if (
            user.has_perm(self.permission_required_self) == False
            or user.has_perm(self.permission_required_operator) == False
        ):
            return Response(
                {
                    "Error": "User does not have permission to perform the requested action "
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logout(request)
        login(request, user)

        serializerCreateCategory = CreateCategorySerializer(
            data=self.request.data, context={"request": self.request}
        )

        serializerCreateCategory.is_valid(raise_exception=True)

        createCatMap = serializerCreateCategory.validated_data

        shop = Shop.objects.get(id=createCatMap["shop_id"])

        category_name = createCatMap["name_category"]

        category_order = Category.objects.count()

        category_image = createCatMap["category_image"]

        content_type_id = createCatMap["content_type_id"]

        module_id = createCatMap["module_id"]

        list_products = createCatMap["product_list"]

        create_category_api_function(
            shop,
            module_id,
            content_type_id,
            category_name,
            category_order,
            category_image,
            list_products,
        )

        return Response(None, status=status.HTTP_202_ACCEPTED)


# note : Admin Update category


def update_category_api_function(
    category_id,
    category_name=None,
    category_order=None,
    category_image=None,
    list_products=None,
):
    category = Category.objects.get(id=category_id)

    if category_name:
        category.name = category_name
        category.save()

    if category_image:
        category.category_image = category_image
        category.save()

    if list_products:
        categoryProducts = CategoryProduct.objects.filter(category=category)
        categoryProducts.delete()

        for product in list_products or []:
            try:
                product = Product.objects.get(pk=product["product_id"])
                if product.unit:
                    quantity = int(product["quantity"])
                else:
                    quantity = 1
                CategoryProduct.objects.create(
                    category=category, product=product, quantity=quantity
                )
            except ObjectDoesNotExist:
                pass
            except KeyError:
                pass


class UpdateCategoryView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)
    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"

    def post(self, request, format=None):
        #! Utilisateur opérateur se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data["user"]

        if (
            user.has_perm(self.permission_required_self) == False
            or user.has_perm(self.permission_required_operator) == False
        ):
            return Response(
                {
                    "Error": "User does not have permission to perform the requested action "
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logout(request)
        login(request, user)

        serializerUpdateCategory = UpdateCategorySerializer(
            data=self.request.data, context={"request": self.request}
        )

        serializerUpdateCategory.is_valid(raise_exception=True)

        createCatMap = serializerUpdateCategory.validated_data

        category_id = createCatMap["category_id"]

        if "name_category" in createCatMap:
            category_name = createCatMap["name_category"]
        else:
            category_name = None

        # category_order = Category.objects.count()
        if "category_image" in createCatMap:
            category_image = createCatMap["category_image"]
        else:
            category_image = None

        if "product_list" in createCatMap:
            list_products = createCatMap["product_list"]
        else:
            list_products = None

        update_category_api_function(
            category_id=category_id,
            category_name=category_name,
            category_image=category_image,
            list_products=list_products,
        )

        return Response(None, status=status.HTTP_202_ACCEPTED)


# note : Admin Delete category


def delete_category_api_function(category_id):
    category = Category.objects.get(id=category_id)
    category.delete()


class DeleteCategoryView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)
    permission_required_self = "modules.change_config_selfsalemodule"
    permission_required_operator = "modules.change_config_operatorsalemodule"

    def post(self, request, format=None):
        #! Utilisateur opérateur se log
        serializerLogin = LoginSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializerLogin.is_valid(raise_exception=True)
        user = serializerLogin.validated_data["user"]

        if (
            user.has_perm(self.permission_required_self) == False
            or user.has_perm(self.permission_required_operator) == False
        ):
            return Response(
                {
                    "Error": "User does not have permission to perform the requested action "
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logout(request)
        login(request, user)

        serializerUpdateCategory = DeleteCategorySerializer(
            data=self.request.data, context={"request": self.request}
        )

        serializerUpdateCategory.is_valid(raise_exception=True)

        createCatMap = serializerUpdateCategory.validated_data

        category_id = createCatMap["category_id"]

        delete_category_api_function(category_id=category_id)

        return Response(None, status=status.HTTP_202_ACCEPTED)


# ------------------

# note : New selfsale API GET Method


class CategoryListView(views.APIView):
    def get(self, request, *args, **kwargs):
        shop_id = self.request.query_params.get("shop_id")

        self_sales = SelfSaleModule.objects.filter(shop=shop_id)

        if not self_sales:
            return Response(
                {"message": "Aucune self-sale trouvée pour ce shop_id."}, status=404
            )

        # Get the first self-sale and its id
        self_sale = self_sales.first()
        module_id = self_sale.id

        # Filter categories associated with module_id
        categories = Category.objects.filter(module_id=module_id, content_type_id=20)

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class SelfSaleShopListView(generics.GenericAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get(self, request, *args, **kwargs):
        filteredSelfSaleModules = SelfSaleModule.objects.filter(state=True)
        shop_ids = filteredSelfSaleModules.values_list("shop", flat=True)

        filteredShops = self.filter_queryset(Shop.objects.filter(id__in=shop_ids))

        serializer = ShopSerializer(filteredShops, many=True)
        return Response(serializer.data)


class AllCategoriesListView(generics.GenericAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get(self, request, *args, **kwargs):
        filteredSelfSaleModules = SelfSaleModule.objects.filter(state=True)
        shop_ids = filteredSelfSaleModules.values_list("shop", flat=True)
        filteredShops = Shop.objects.filter(id__in=shop_ids)

        self_sales_modules = SelfSaleModule.objects.filter(shop__in=filteredShops)

        if not self_sales_modules:
            return Response({"message": "Aucuns self-sale trouvé"}, status=404)

        all_categories = []

        for self_sale_module in self_sales_modules:
            module_id = self_sale_module.id
            categories = self.filter_queryset(
                Category.objects.filter(module_id=module_id, content_type_id=20)
            )
            all_categories.extend(categories)

        serializer = CategorySerializer(all_categories, many=True)
        return Response(serializer.data)


class AllProductsInSelfSaleListView(generics.GenericAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get(self, request, *args, **kwargs):
        filteredSelfSaleModules = SelfSaleModule.objects.filter(state=True)
        shop_ids = filteredSelfSaleModules.values_list("shop", flat=True)
        filteredShops = Shop.objects.filter(id__in=shop_ids)

        self_sales_modules = SelfSaleModule.objects.filter(shop__in=filteredShops)

        if not self_sales_modules:
            return Response({"message": "Aucuns self-sale trouvé"}, status=404)

        all_products = []

        for self_sale_module in self_sales_modules:
            module_id = self_sale_module.id
            categories = Category.objects.filter(
                module_id=module_id, content_type_id=20
            )

            for category in categories:
                category_products = self.filter_queryset(category.products.all())

                serializer = SearchAllProductSerializer(
                    category_products,
                    many=True,
                    # Passer la catégorie au contexte
                    context={"category": category},
                )

                all_products.extend(serializer.data)

        return Response(all_products)
