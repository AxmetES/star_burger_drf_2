from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Order, OrderDetails, ProductCategory, Product, Restaurant, GeoPosition


class OrderDetailsSerializer(ModelSerializer):

    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, write_only=True, allow_null=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(validators=[MinValueValidator(0)],
                                     decimal_places=2,
                                     max_digits=10)
    image = serializers.CharField()
    special_status = serializers.BooleanField(required=False)
    description = serializers.CharField()

    def validate_description(self, value):
        max_length = 200
        print(len(value[:max_length]))
        return value[:max_length]


class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
