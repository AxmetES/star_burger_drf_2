from geopy import distance
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders_details = []
    orders_menu_items = Order.objects.total_price().prefetch_related('order_details__product__menu_items').all()
    for order in orders_menu_items:
        order_detail = {'id': order.id,
                        'status': order.order_status,
                        'payment_method': order.payment_method,
                        'total_price': order.total_price,
                        'client': f'{order.firstname} {order.lastname}',
                        'phonenumber': order.phonenumber,
                        'address': order.address,
                        'comments': order.comments,
                        'restaurants': set()}
        if order.restaurant:
            range_to_order = distance.distance((order.lat, order.lon), (order.restaurant.lat,
                                                                        order.restaurant.lon)).km
            order_detail['restaurants'].add(f'Готовит {order.restaurant.name} - {round(range_to_order, 3)} km')
            orders_details.append(order_detail)
            continue
        products = order.order_details.all()
        for product in products:
            products = product.product
            menu_items = products.menu_items.all()
            for menu in menu_items:
                restaurant = menu.restaurant
                range_to_order = distance.distance((order.lat, order.lon), (restaurant.lat, restaurant.lon)).km
                order_detail['restaurants'].add(f'{restaurant.name} - {round(range_to_order, 3)} km')
        orders_details.append(order_detail)

    return render(request, template_name='order_items.html', context={
        'order_items': orders_details,
    })
