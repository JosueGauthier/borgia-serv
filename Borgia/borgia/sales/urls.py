from django.urls import include, path
from sales.views import Saledownload_xlsx, RankUserProductPurchaseViewset, get_live_2hours_history_sale, get_total_sale, SaleList, SaleRetrieve, SaleViewSet, get_history_sale, all_high_scores, StatUserPurchase, HistorySaleUserViewSet, RankBestPurchaserViewset, RankUserShopPurchaseViewset
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'sale', SaleViewSet)
router.register(r'user-history-allsale', HistorySaleUserViewSet,
                basename='user-history-allsale')
router.register(r'stat-user', StatUserPurchase, basename='stat-user')
router.register(r'rank-user', RankBestPurchaserViewset, basename='rank-user')
router.register(r'rank-user-shop', RankUserShopPurchaseViewset,
                basename='rank-user-shop')
router.register(r'rank-user-product', RankUserProductPurchaseViewset,
                basename='rank-user-product')

sales_patterns = [

    path('api-links/sale/', include(router.urls)),
    path('api-links/total/', get_total_sale),
    path('api-links/history/', get_history_sale),
    path('api-links/live-sales/', get_live_2hours_history_sale),
    path('api-links/scores/', all_high_scores),


    path('shops/<int:shop_pk>/sales/', include([
        path('', SaleList.as_view(), name='url_sale_list'),
        path('<int:sale_pk>/', SaleRetrieve.as_view(),
             name='url_sale_retrieve'),
        path('xlsx/download/', Saledownload_xlsx.as_view(),
             name='url_sales_download_xlsx')
    ]))
]
