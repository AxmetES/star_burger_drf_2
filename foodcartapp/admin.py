from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect

from star_burger import settings
from star_burger.settings import YANDEX_API_KEY
from star_burger.utils import fetch_coordinates
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderDetails


class OrderDetailInline(admin.TabularInline):
    model = OrderDetails
    exec = 0


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'firstname',
        'lastname',
    ]

    list_display = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'order_status',
        'payment_method',
        'comments',
        'restaurant',
        'created_at',
        'called_at',
        'delivered_at'
    ]

    inlines = [
        OrderDetailInline,
    ]

    list_filter = ('restaurant',)

    def response_change(self, request, obj):
        if "_save" in request.POST:
            if obj.address:
                lon, lat = fetch_coordinates(YANDEX_API_KEY, obj.address)
                obj.lon = lon
                obj.lat = lat
                obj.save()
            next_url = request.GET.get('next', None)
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
                return redirect(next_url)
            else:
                return super().response_change(request, obj)
        return super().response_change(request, obj)


@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    search_fields = [
        'product',
        'order',
    ]

    list_display = [
        'product',
        'quantity',
    ]


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
