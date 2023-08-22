from django.urls import path

from .views import product_list_api, banners_list_api, register_order, add_restaurants, add_products

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    path('add_products/', add_products),
    path('add_restaurants/', add_restaurants),
]
