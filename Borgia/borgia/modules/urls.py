from django.urls import include, path

from . import views
from rest_framework import routers

from modules.views import (CatBaseViewset, ShopModuleSaleView,
                           ShopModuleCategoryCreateView,
                           ShopModuleCategoryDeleteView,
                           ShopModuleCategoryUpdateView,
                           ShopModuleConfigUpdateView,
                           ShopModuleConfigView)


# Partie API
router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'category-products', views.ProductFromCategoryViewSet)
router.register(r'category-products-model', views.CategoryFromProductViewSet)
router.register(r'categoryv2', CatBaseViewset,
                basename='categoryv2')


modules_patterns = [

    # API
    path('api-links/category/', include(router.urls)),
    path('api-links/self-sale/', views.SelfSaleView.as_view()),
    path('api-links/operator-sale/', views.OperatorSaleView.as_view()),

    path('api-links/create-category/', views.CreateCategoryView.as_view()),

    path('api-links/update-category/', views.UpdateCategoryView.as_view()),
    path('api-links/delete-category/', views.DeleteCategoryView.as_view()),

    path('api-links/searchcategory/', views.SearchCategoryView.as_view()),

    path('shops/<int:shop_pk>/modules/', include([
        path('<str:module_class>/', include([
            path('', ShopModuleSaleView.as_view(), name='url_shop_module_sale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_shop_module_config'),
            path('config/update/', ShopModuleConfigUpdateView.as_view(),
                 name='url_shop_module_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreateView.as_view(),
                     name='url_shop_module_category_create'),
                path('<int:category_pk>/', include([
                    path('update/', ShopModuleCategoryUpdateView.as_view(),
                         name='url_shop_module_category_update'),
                    path('delete/', ShopModuleCategoryDeleteView.as_view(),
                         name='url_shop_module_category_delete')
                ]))
            ]))
        ]))
    ]))
]
