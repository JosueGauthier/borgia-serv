from . import views
from rest_framework import routers
from django.urls import include, path

from shops.views import (ProductBaseViewSet, ProductCreate, ProductDeactivate, ProductList,
                         ProductRemove, ProductRetrieve, ProductUpdate,
                         ProductUpdatePrice, ShopCheckup, ShopCreate, ShopList,
                         ShopUpdate, ShopWorkboard)


router = routers.DefaultRouter()
router.register(r'shops', views.ShopViewSet)
router.register(r'products', views.ProductFromShopViewSet)
router.register(r'shop-stat', views.StatShopViewSet)
router.register(r'productsv2', ProductBaseViewSet,
                basename='productsv2')

shops_patterns = [
    # API

    #*Get method
    path('api-links/shops/', include(router.urls)),
    path('api-links/searchprod/', views.SearchProductView.as_view()),
    path('api-links/searchshop/', views.SearchShopView.as_view()),
    
    #*Post Method
    path('api-links/create-shop/', views.CreateShopView.as_view()),
    path('api-links/update-shop/', views.UpdateShopView.as_view()),
    #path('api-links/delete-shop/', views.DeleteShopView.as_view()),
    
    path('api-links/create-product/', views.CreateProductView.as_view()),

    # SHOPS
    path(
        'shops/',
        include([
            path('', ShopList.as_view(), name='url_shop_list'),
            path('create/', ShopCreate.as_view(), name='url_shop_create'),
            path(
                '<int:shop_pk>/',
                include([
                    path('update/',
                         ShopUpdate.as_view(),
                         name='url_shop_update'),
                    path('checkup/',
                         ShopCheckup.as_view(),
                         name='url_shop_checkup'),
                    path('workboard/',
                         ShopWorkboard.as_view(),
                         name='url_shop_workboard'),

                    # PRODUCTS
                    path(
                        'products/',
                        include([
                            path('',
                                 ProductList.as_view(),
                                 name='url_product_list'),
                            path('create/',
                                 ProductCreate.as_view(),
                                 name='url_product_create'),
                            path(
                                '<int:product_pk>/',
                                include([
                                    path('',
                                         ProductRetrieve.as_view(),
                                         name='url_product_retrieve'),
                                    path('update/',
                                         ProductUpdate.as_view(),
                                         name='url_product_update'),
                                    path('update/price/',
                                         ProductUpdatePrice.as_view(),
                                         name='url_product_update_price'),
                                    path('deactivate/',
                                         ProductDeactivate.as_view(),
                                         name='url_product_deactivate'),
                                    path('remove/',
                                         ProductRemove.as_view(),
                                         name='url_product_remove')
                                ]))
                        ]))
                ]))
        ]))
]
