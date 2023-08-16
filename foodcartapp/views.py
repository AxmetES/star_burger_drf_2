import json
import re

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderDetails


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
    try:
        order_data = request.data
        if validate_phone_number(order_data.get('phonenumber')):
            raise Exception('Incorrect phone number.')

        order = Order(first_name=order_data.get('firstname'),
                      last_name=order_data.get('lastname'),
                      phone_number=order_data.get('phonenumber'),
                      deliver_address=order_data.get('address')
                      )
        order.save()
        if len(order_data.get('products')) < 1:
            raise Exception('list product is empty.')
        for product in order_data.get('products'):
            product_obj = Product.objects.get(id=product['product'])
            order_details = OrderDetails(product=product_obj,
                                         quantity=product['quantity'],
                                         order=order)
            order_details.save()
    except Exception as e:
        print(e)
        return Response({'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response_data = {'message': 'Order saved successfully'}
    return Response(response_data, status=status.HTTP_200_OK)

