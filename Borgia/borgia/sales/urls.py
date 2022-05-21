from django.urls import include, path
from sales.views import get_total_sale, SaleList, SaleRetrieve,SaleViewSet,get_history_sale,all_high_scores,StatUserPurchase
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'sale', SaleViewSet)
router.register(r'stat-user', StatUserPurchase, basename='stat-user')

sales_patterns = [

    path('api-links/sale/', include(router.urls)),

    path('api-links/total/', get_total_sale),
    path('api-links/history/', get_history_sale),
    #path('api-links/users-sales-podium/', get_sales_podium),
    path('api-links/scores/', all_high_scores),

    

    path('shops/<int:shop_pk>/sales/', include([
        path('', SaleList.as_view(), name='url_sale_list'),
        path('<int:sale_pk>/', SaleRetrieve.as_view(),
             name='url_sale_retrieve')
    ]))
]
