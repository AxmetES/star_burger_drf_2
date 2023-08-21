import json
import os
import re

from PIL import Image
from django.http import JsonResponse
from django.templatetags.static import static
from django.core.files import File
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order, OrderDetails, ProductCategory, Restaurant
from .serializers import OrderSerializer, ProductSerializer, RestaurantSerializer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_phone_number(phone_number) -> bool:
    pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
    match = re.search(pattern, phone_number)
    if match:
        pattern = r"^\d{5,15}$"
        if re.match(pattern, phone_number):
            return False
        else:
            return True
    return True


@api_view(['POST'])
def register_order(request) -> json:
    # TODO это лишь заглушка
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order, is_created = Order.objects.get_or_create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'])
    # order.save()
    print(is_created)
    products = serializer.validated_data['products']
    order_details = []
    for product in products:
        product_obj = Product.objects.get(id=product['product'].id)
        order_details = OrderDetails(product=product_obj,
                                     quantity=product['quantity'],
                                     order=order)
        order_details.save()
    response_data = {'message': 'Order saved successfully'}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def make_product(request) -> json:
    products = []
    for product_data in request.data:
        serializer = ProductSerializer(data=product_data)
        serializer.is_valid(raise_exception=True)
        image_name = serializer.validated_data.pop('image')
        category = serializer.validated_data.pop('category')
        category_obj = ProductCategory.objects.get(name=category)

        media_dir = os.path.join(BASE_DIR, "media")
        if image_name:
            img_file_path = os.path.join(media_dir, image_name)
            with open(img_file_path, 'rb') as img_file:
                product = Product(**serializer.validated_data)
                product.image.save(image_name, img_file, save=False)
                product.category = category_obj
                products.append(product)

    Product.objects.bulk_create(products)
    response_data = {'message': 'Products saved successfully'}
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_restaurants(request) -> json:
    restaurants = []
    for restaurant in request.data:
        serializer = RestaurantSerializer(data=restaurant)
        serializer.is_valid(raise_exception=True)
        restaurant = Restaurant(**serializer.validated_data)
        restaurants.append(restaurant)
    Restaurant.objects.bulk_create(restaurants)
    response_data = {'message': 'Restaurants saved successfully'}
    return Response(response_data, status=status.HTTP_201_CREATED)




