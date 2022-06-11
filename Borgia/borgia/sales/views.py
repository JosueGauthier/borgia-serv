from rest_framework.response import Response
import datetime
from operator import itemgetter
from django.db.models import Avg, Max, Min, Sum, Count, F
from django.db.models import F
from rest_framework.decorators import api_view
from .serializers import *
from .models import Sale, SaleProduct
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from time import strftime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import render

from borgia.views import BorgiaFormView, BorgiaView
from sales.forms import SaleListSearchDateForm
from sales.mixins import SaleMixin
from sales.models import Sale
from shops.mixins import ShopMixin


class SaleList(ShopMixin, BorgiaFormView):
    """
    View to list sales.

    The sale are displayed for a shop. A manager of a shop can only see sales
    relatives to his own shop. Association managers can switch to see other shops.

    :note:: only sales are listed here. Sales come from a shop, for other
    types of transactions, please refer to other classes (RechargingList,
    TransfertList and ExceptionnalMovementList).
    """
    permission_required = 'sales.view_sale'
    menu_type = 'shops'
    template_name = 'sales/sale_shop_list.html'
    form_class = SaleListSearchDateForm
    lm_active = 'lm_sale_list'

    query_shop = None
    search = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales_tab_header = []
        seen = set(sales_tab_header)
        page = self.request.POST.get('page', 1)

        try:
            context['sale_list'] = Sale.objects.filter(
                shop=self.shop).order_by('-datetime')
        except AttributeError:
            context['sale_list'] = Sale.objects.all().order_by('-datetime')

        # The sale_list is paginated by passing the filtered QuerySet to Paginator
        paginator = Paginator(self.form_query(context['sale_list']), 50)
        try:
            # The requested page is grabbed
            sales = paginator.page(page)
        except PageNotAnInteger:
            # If the requested page is not an integer
            sales = paginator.page(1)
        except EmptyPage:
            # If the requested page is out of range, the last page is grabbed
            sales = paginator.page(paginator.num_pages)

        context['sale_list'] = sales

        for sale in context['sale_list']:
            if sale.from_shop() not in seen:
                seen.add(sale.from_shop())
                sales_tab_header.append(sale.from_shop())

        context['sales_tab_header'] = sales_tab_header

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
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        if self.query_shop:
            query = query.filter(shop=self.query_shop)

        return query

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']
        try:
            if form.cleaned_data['shop']:
                self.query_shop = form.cleaned_data['shop']
        except KeyError:
            pass

        return self.get(self.request, self.args, self.kwargs)


class SaleRetrieve(SaleMixin, BorgiaView):
    """
    Retrieve a sale.

    A sale comes from a shop, for other type of transaction, please refer to
    other classes (RechargingRetrieve, TransfertRetrieve,
    ExceptionnalMovementRetrieve).
    """
    permission_required = 'sales.view_sale'
    menu_type = 'shops'
    template_name = 'sales/sale_retrieve.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


#! partie API


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sender', 'datetime']


class HistorySaleUserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Sale.objects.all()
        sender = self.request.query_params.get('sender')
        if sender is not None:
            queryset = queryset.filter(sender__username=sender)

        #! To protect server from unwanted action
        """ if sender is None:
            queryset = queryset.filter(sender=0)"""
        serializer = HistorySaleUserSerializer(queryset, many=True)

        return Response(serializer.data)


@api_view(('GET',))
def get_total_sale(request):
    data = []
    data.append(SaleProduct.objects.all().aggregate(Sum('price')))
    data.append(SaleProduct.objects.all().count())
    return Response(data)


@api_view(('GET',))
def get_history_sale(request):
    data = []
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    nombre_de_jour = day_of_year

    for i in range(0, nombre_de_jour):
        start_day = strftime(str((datetime.datetime.strptime(
            "2022-01-01", "%Y-%m-%d") + datetime.timedelta(days=i)).date()))
        end_day = strftime(str((datetime.datetime.strptime(
            "2022-01-01", "%Y-%m-%d") + datetime.timedelta(days=1+i)).date()))
        price_sum = SaleProduct.objects.filter(
            sale__datetime__range=[start_day, end_day]).aggregate(Sum('price'))

        format_day = (datetime.datetime.strptime(
            "2022-01-01", "%Y-%d-%m") + datetime.timedelta(days=i)).date()

        a_day = datetime.datetime.strptime(
            str(format_day), '%Y-%m-%d').strftime('%d-%m')

        data.append({
            "format_day": a_day,
            "start_day": start_day,
            "price_sum": price_sum["price__sum"],
        })

    return Response(data)


@api_view(('GET',))
def get_live_2hours_history_sale(request):
    data = []
    temps_debut = datetime.datetime.now() - datetime.timedelta(hours=2)
    time_step = 30

    for i in range(0, 7200, time_step):
        start_range = strftime(
            str(temps_debut + datetime.timedelta(seconds=i)))
        end_range = strftime(
            str(temps_debut + datetime.timedelta(seconds=(i+time_step))))
        price_sum = SaleProduct.objects.filter(
            sale__datetime__range=[start_range, end_range]).aggregate(Sum('price'))

        
        a= temps_debut + datetime.timedelta(seconds=i)
        
        format_time = a.strftime("%H:%M")


        #datetime.datetime.strptime(str(start_range), '%Y-%m-%d %H:%M:%S').strftime('%H:%M')

        #"time": "2022-06-11 17:49:59.955133",

        data.append({
            "time": format_time,
            "price_sum": price_sum["price__sum"],
        })

    return Response(data)


@api_view(('GET',))
def get_sales_podium(request):

    #user = self.request.user

    data = []
    user_sum = SaleProduct.objects.filter(
        sale__sender__username="73An220").aggregate(Sum('price'))

    data.append(SaleProduct.objects.filter(
        sale__sender__username='73An220').aggregate(Sum('price')))
    data.append(SaleProduct.objects.filter(
        sale__sender__username='73An220').count())

    data.append({"user_sum": user_sum["price__sum"]})

    # with open("/borgia-serv/Borgia/borgia/sales/test.text", "a") as o:
    #    o.write(str(totalsale = Sale.objects.all().aggregate(total_sale=Count('shop'))))
    return Response(data)


@api_view(['GET'])
def all_high_scores(request):
    queryset = User.objects.order_by('-balance')
    serializer = StatPurchaseSerializer(queryset, many=True)
    return Response(serializer.data)


class StatUserPurchase(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(username=username)
        serializer = StatPurchaseSerializer(queryset, many=True)
        return Response(serializer.data)


class RankBestPurchaserViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        serializer = RankUserAllPurchaseSerializer(queryset, many=True)
        sortedList = sorted(serializer.data, key=itemgetter(
            'montant_achats'), reverse=True)[:10]
        return Response(sortedList)


class RankUserShopPurchaseViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = Shop.objects.all()
        id = self.request.query_params.get('id')
        if id is not None:
            queryset = queryset.filter(id=id)
        serializer = ShopUserRankSerializer(queryset, many=True)
        return Response(serializer.data)


class RankUserProductPurchaseViewset(viewsets.ViewSet):
    def list(self, request):
        queryset = Shop.objects.all()
        id = self.request.query_params.get('id')
        if id is not None:
            queryset = queryset.filter(id=id)
        serializer = ShopProductUserRankSerializer(queryset, many=True)
        return Response(serializer.data)
