from django.urls import path

from .views import product_list_api, banners_list_api, register_order, make_product, add_restaurants

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    path('make_product/', make_product),
    path('add_restaurants/', add_restaurants),
]
