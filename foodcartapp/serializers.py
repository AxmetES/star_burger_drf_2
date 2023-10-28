import os

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Order, OrderDetails, ProductCategory, Product, Restaurant, GeoPosition
from star_burger.settings import BASE_DIR
from star_burger.utils import get_or_create_lon_lat


class OrderDetailsSerializer(ModelSerializer):

    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']

    def create(self, validated_data):
        product_data = validated_data.pop('product')
        product_instance, _ = Product.objects.get_or_create(**product_data)
        order_details = OrderDetails.objects.create(product=product_instance, **validated_data)
        return order_details


class OrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, write_only=True, allow_null=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products_data = validated_data.pop('products')

        lon, lat = get_or_create_lon_lat(validated_data['address'])
        order, is_created = Order.objects.get_or_create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
            lon=lon,
            lat=lat)

        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price = product.price * quantity
            OrderDetails.objects.create(order=order, product=product, quantity=quantity, price=price)
        return order


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description']

    def validate_description(self, value):
        if len(value) > 200:
            raise serializers.ValidationError('Длина поля "description" не должна превышать 200 символов.')
        return value

    def create(self, validated_data, image_name):
        category = validated_data['category']
        product, is_created = Product.objects.get_or_create(
            name=validated_data['name'],
            category=category,
            price=validated_data['price'],
            description=validated_data['description'],
        )

        media_dir = os.path.join(BASE_DIR, "media")
        img_file_path = os.path.join(media_dir, image_name)
        product.image = None
        with open(img_file_path, 'rb') as img_file:
            product.image.save(image_name, img_file, save=True)


class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'contact_phone', 'lon', 'lat']

    def create(self, validated_data):
        lon, lat = get_or_create_lon_lat(validated_data['address'])
        restaurant, is_created = Restaurant.objects.get_or_create(
            name=validated_data['name'],
            address=validated_data['address'],
            contact_phone=validated_data['contact_phone'],
            lon=lon,
            lat=lat
        )
        return restaurant
