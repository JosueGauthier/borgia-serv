from operator import itemgetter
from time import strftime

import datetime
from shops.models import Shop
from users.models import User
from .serializers import (
    HistorySaleUserSerializer,
    RankUserAllPurchaseSerializer,
    SaleSerializer,
    ShopProductUserRankSerializer,
    ShopUserRankSerializer,
    StatPurchaseSerializer,
)

from borgia.views import BorgiaFormView, BorgiaView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.shortcuts import HttpResponse, render
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sales.forms import SaleListSearchDateForm
from sales.mixins import SaleMixin
from sales.models import Sale
from shops.mixins import ShopMixin

from .models import Sale, SaleProduct


class SaleList(ShopMixin, BorgiaFormView):
    """
    View to list sales.

    The sale are displayed for a shop. A manager of a shop can only see sales
    relatives to his own shop. Association managers can switch to see other shops.

    :note:: only sales are listed here. Sales come from a shop, for other
    types of transactions, please refer to other classes (RechargingList,
    TransfertList and ExceptionnalMovementList).
    """

    permission_required = "sales.view_sale"
    menu_type = "shops"
    template_name = "sales/sale_shop_list.html"
    form_class = SaleListSearchDateForm
    lm_active = "lm_sale_list"

    query_shop = None
    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales_tab_header = []
        seen = set(sales_tab_header)
        page = self.request.POST.get("page", 1)

        try:
            context["sale_list"] = Sale.objects.filter(shop=self.shop).order_by(
                "-datetime"
            )
        except AttributeError:
            context["sale_list"] = Sale.objects.all().order_by("-datetime")

        # The sale_list is paginated by passing the filtered QuerySet to Paginator
        paginator = Paginator(self.form_query(context["sale_list"]), 50)
        try:
            # The requested page is grabbed
            sales = paginator.page(page)
        except PageNotAnInteger:
            # If the requested page is not an integer
            sales = paginator.page(1)
        except EmptyPage:
            # If the requested page is out of range, the last page is grabbed
            sales = paginator.page(paginator.num_pages)

        context["sale_list"] = sales

        for sale in context["sale_list"]:
            if sale.from_shop() not in seen:
                seen.add(sale.from_shop())
                sales_tab_header.append(sale.from_shop())

        context["sales_tab_header"] = sales_tab_header

        return context

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__icontains=self.search)
                | Q(operator__first_name__icontains=self.search)
                | Q(operator__surname__icontains=self.search)
                | Q(operator__username__icontains=self.search)
                | Q(recipient__last_name__icontains=self.search)
                | Q(recipient__first_name__icontains=self.search)
                | Q(recipient__surname__icontains=self.search)
                | Q(recipient__username__icontains=self.search)
                | Q(sender__last_name__icontains=self.search)
                | Q(sender__first_name__icontains=self.search)
                | Q(sender__surname__icontains=self.search)
                | Q(sender__username__icontains=self.search)
            )

        if self.date_begin:
            query = query.filter(datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(datetime__lte=self.date_end)

        if self.query_shop:
            query = query.filter(shop=self.query_shop)

        return query

    def form_valid(self, form):
        if form.cleaned_data["search"]:
            self.search = form.cleaned_data["search"]

        if form.cleaned_data["date_begin"]:
            self.date_begin = form.cleaned_data["date_begin"]

        if form.cleaned_data["date_end"]:
            self.date_end = form.cleaned_data["date_end"]
        try:
            if form.cleaned_data["shop"]:
                self.query_shop = form.cleaned_data["shop"]
        except KeyError:
            pass

        return self.get(self.request, self.args, self.kwargs)


#! replace BorgiaView with BorgiaFormView
class SaleRetrieve(SaleMixin, BorgiaFormView):
    """
    Retrieve a sale.

    A sale comes from a shop, for other type of transaction, please refer to
    other classes (RechargingRetrieve, TransfertRetrieve,
    ExceptionnalMovementRetrieve).
    """

    permission_required = "sales.view_sale"
    menu_type = "shops"
    template_name = "sales/sale_retrieve.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class Saledownload_xlsx(ShopMixin, BorgiaView):
    """
    Download sales (Jquery with SaleListSearchDateForm) from a shop in a xlsx file

    """

    permission_required = "sales.view_sale"
    menu_type = "shops"
    template_name = "sales/sale_shop_list.html"
    form_class = SaleListSearchDateForm

    search = None
    date_begin = None
    date_end = None

    def post(self, request, *args, **kwargs):
        if request.POST["search"] != "":
            self.search = request.POST["search"]

        if request.POST["date_begin"] != "":
            self.date_begin = datetime.datetime.strptime(
                request.POST["date_begin"], "%d/%m/%Y"
            )

        if request.POST["date_end"] != "":
            self.date_end = datetime.datetime.strptime(
                request.POST["date_end"], "%d/%m/%Y"
            )

        wb = Workbook()
        # grab the active worksheet
        ws = wb.active
        ws.title = "sales"
        columns = ["Opérateur", "Acheteur", "Date", "Produits", "Prix"]
        ws.append(columns)
        for col in ["A", "B", "C", "D", "E"]:
            ws.column_dimensions[col].width = 30

        sales_list = Sale.objects.filter(shop=self.shop).order_by("-datetime")
        sales_list = self.form_query(sales_list)
        for s in sales_list:
            operator = s.operator.last_name + " " + s.operator.first_name
            sender = s.sender.last_name + " " + s.sender.first_name
            ws.append(
                [
                    operator,
                    sender,
                    s.datetime.strftime("%c"),
                    s.string_products(),
                    s.amount(),
                ]
            )

        # Return the file
        response = HttpResponse(
            save_virtual_workbook(wb),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            "attachment; filename=sales-" + str(now().date()) + ".xlsx"
        )
        return response

    def form_query(self, query):
        if self.search:
            query = query.filter(
                Q(operator__last_name__icontains=self.search)
                | Q(operator__first_name__icontains=self.search)
                | Q(operator__surname__icontains=self.search)
                | Q(operator__username__icontains=self.search)
                | Q(recipient__last_name__icontains=self.search)
                | Q(recipient__first_name__icontains=self.search)
                | Q(recipient__surname__icontains=self.search)
                | Q(recipient__username__icontains=self.search)
                | Q(sender__last_name__icontains=self.search)
                | Q(sender__first_name__icontains=self.search)
                | Q(sender__surname__icontains=self.search)
            )

        if self.date_begin:
            query = query.filter(datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(datetime__lte=self.date_end)

        return query


#! partie API


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sender", "datetime"]


class HistorySaleUserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(username=username)

        #! To protect server from unwanted action
        if username is None:
            queryset = queryset.filter(username=0)

        serializer = HistorySaleUserSerializer(queryset, many=True)

        try:
            return Response((serializer.data)[0])
        except:
            return Response([])


@api_view(("GET",))
def get_total_sale(request):
    data = []
    data.append(SaleProduct.objects.all().aggregate(Sum("price")))
    data.append(SaleProduct.objects.all().count())

    return Response(data)


@api_view(("GET",))
def get_history_sale(request):
    data = []
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    nombre_de_jour = day_of_year

    for i in range(0, nombre_de_jour):
        start_day = strftime(
            str(
                (
                    datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
                    + datetime.timedelta(days=i)
                ).date()
            )
        )
        end_day = strftime(
            str(
                (
                    datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
                    + datetime.timedelta(days=1 + i)
                ).date()
            )
        )
        price_sum = SaleProduct.objects.filter(
            sale__datetime__range=[start_day, end_day]
        ).aggregate(Sum("price"))

        format_day = (
            datetime.datetime.strptime("2022-01-01", "%Y-%m-%d")
            + datetime.timedelta(days=i)
        ).date()

        a_day = datetime.datetime.strptime(str(format_day), "%Y-%m-%d").strftime(
            "%d-%m"
        )

        data.append(
            {
                "format_day": a_day,
                "start_day": start_day,
                "price_sum": price_sum["price__sum"],
            }
        )

    return Response(data)


@api_view(("GET",))
def get_live_2hours_history_sale(request):
    data = []
    temps_debut = datetime.datetime.now() - datetime.timedelta(hours=2)
    time_step = 30

    for i in range(0, 7200, time_step):
        start_range = strftime(str(temps_debut + datetime.timedelta(seconds=i)))
        end_range = strftime(
            str(temps_debut + datetime.timedelta(seconds=(i + time_step)))
        )
        price_sum = SaleProduct.objects.filter(
            sale__datetime__range=[start_range, end_range]
        ).aggregate(Sum("price"))

        a = temps_debut + datetime.timedelta(seconds=i)

        format_time = a.strftime("%H:%M")

        data.append(
            {
                "time": format_time,
                "price_sum": price_sum["price__sum"],
            }
        )

    return Response(data)


# TODO A modifier ici
@api_view(("GET",))
def get_sales_podium(request):
    data = []
    user_sum = SaleProduct.objects.filter(sale__sender__username="73An220").aggregate(
        Sum("price")
    )

    data.append(
        SaleProduct.objects.filter(sale__sender__username="73An220").aggregate(
            Sum("price")
        )
    )
    data.append(SaleProduct.objects.filter(sale__sender__username="73An220").count())

    data.append({"user_sum": user_sum["price__sum"]})

    return Response(data)


@api_view(["GET"])
def all_high_scores(request):
    queryset = User.objects.order_by("-balance")
    serializer = StatPurchaseSerializer(queryset, many=True)
    return Response(serializer.data)


class StatUserPurchase(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(username=username)
        serializer = StatPurchaseSerializer(queryset, many=True)
        return Response(serializer.data)


class RankBestPurchaserViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        serializer = RankUserAllPurchaseSerializer(queryset, many=True)
        sortedList = sorted(
            serializer.data, key=itemgetter("montant_achats"), reverse=True
        )
        for index, sortedItem in enumerate(sortedList):
            sortedList[index].update(index=index + 1)
        return Response(sortedList)


class RankUserShopPurchaseViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = Shop.objects.all()
        id = self.request.query_params.get("id")
        if id is not None:
            queryset = queryset.filter(id=id)
        serializer = ShopUserRankSerializer(queryset, many=True)
        return Response(serializer.data)


class RankUserProductPurchaseViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = Shop.objects.all()
        id = self.request.query_params.get("id")
        if id is not None:
            queryset = queryset.filter(id=id)
        serializer = ShopProductUserRankSerializer(queryset, many=True)
        return Response(serializer.data)
