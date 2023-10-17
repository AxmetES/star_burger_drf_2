from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Order, OrderDetails, ProductCategory, Product, Restaurant, GeoPosition
from star_burger.utils import get_or_create_lon_lat


class OrderDetailsSerializer(ModelSerializer):

    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, write_only=True, allow_null=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products', 'order_status', 'payment_method',
                  'comments', 'status', 'total_price', 'client']
        """id
        status
        payment_method
        total_price
        client
        phonenumber
        .address
        comments"""
    def create(self, validated_data):
        lon, lat = get_or_create_lon_lat(validated_data['address'])
        order, is_created = Order.objects.get_or_create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
            lon=lon,
            lat=lat)
        return order


class ProductSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    category = serializers.CharField()

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'special_status', 'description']

    def validate_description(self, value):
        max_length = 200
        return value[:max_length]

    def validate_category(self, value):
        category_name = value
        category = ProductCategory.objects.get(name=category_name)
        if category is None:
            raise serializers.ValidationError("Категория не найдена.")
        return category


class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'contact_phone', 'lon', 'lat']
