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
from rest_framework.response import Response


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sender', 'datetime']


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
        start_day = strftime(str(datetime.datetime.strptime(
            "2022-01-01", "%Y-%m-%d") + datetime.timedelta(days=i)))
        end_day = strftime(str(datetime.datetime.strptime(
            "2022-01-01", "%Y-%m-%d") + datetime.timedelta(days=1+i)))
        price_sum = SaleProduct.objects.filter(
            sale__datetime__range=[start_day, end_day]).aggregate(Sum('price'))
        
        data.append({
            "start_day": start_day,
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
        serializer = RankSerializer(queryset, many=True)
        user_rank_list =[]
        #list serializerDataList = serializer.data


        #newlist = sorted(serializer.data, key=lambda d: d['username']) 
        newlist = sorted(serializer.data, key=itemgetter('qte_achats'), reverse=True)

        with open("/borgia-serv/Borgia/borgia/sales/test.text", "a") as o:
            o.write(str(newlist))
        return Response(serializer.data)


""" [
    {'id': 1, 'username': 'AE_ENSAM', 'surname': None, 'montant_achats': {'price__sum': None}, 'qte_achats': 0}, 
    {'id': 3, 'username': '73An220', 'surname': 'Khalvin', 'montant_achats': {'price__sum': Decimal('54.90')}, 'qte_achats': 18}, 
    {'id': 4, 'username': '73Kin220', 'surname': 'gum', 'montant_achats': {'price__sum': None}, 'qte_achats': 0}
    
] """