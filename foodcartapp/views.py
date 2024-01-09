import json
import os
import re

from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product
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


@transaction.atomic()
@api_view(['POST'])
def register_order(request) -> json:
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.create(serializer.validated_data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_products(request) -> json:
    for product_data in request.data:
        serializer = ProductSerializer(data=product_data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data, product_data['image'])
    response_data = {'message': 'Products saved successfully'}
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_restaurants(request) -> json:
    for restaurant in request.data:
        serializer = RestaurantSerializer(data=restaurant)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
    response_data = {'message': 'Restaurants saved successfully'}
    return Response(response_data, status=status.HTTP_201_CREATED)




