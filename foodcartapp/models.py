from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    lon = models.FloatField(
        'долгота',
        blank=True,
        null=True,
    )

    lat = models.FloatField(
        'ширата',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(total_price=Sum(F('order_details__price')))


class Order(models.Model):
    firstname = models.CharField(
        'имя',
        blank=False,
        max_length=50,
        db_index=True
    )
    lastname = models.CharField(
        'фамилия',
        blank=True,
        max_length=100,
        db_index=True
    )
    phonenumber = PhoneNumberField(blank=False)
    address = models.CharField(
        'адрес доставки',
        max_length=100,
        blank=False
    )

    objects = OrderQuerySet.as_manager()

    CONFIRMATION = 'Необработанный'
    PROCESSING = 'Приготовление'
    DELIVERY = 'Доставка'
    COMPLETED = 'Завершено'
    ORDER_STATUS = [
        (CONFIRMATION, 'Необработанный'),
        (PROCESSING, 'Приготовление'),
        (DELIVERY, 'Доставка'),
        (COMPLETED, 'Завершено'),
    ]
    order_status = models.CharField(
        'Статус заказа',
        max_length=14,
        choices=ORDER_STATUS,
        default=CONFIRMATION,
        db_index=True
    )

    CASH = 'Наличными'
    CASHLESS = 'Безналичный'
    CASHLESS_ON_THE_SPOT = 'Безналичный на месте'
    PAYMENT_METHOD = [
        (CASH, 'Наличными'),
        (CASHLESS, 'Безналичный'),
        (CASHLESS_ON_THE_SPOT, 'Безналичный на месте'),
    ]
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_METHOD,
        default=CASH,
        db_index=True
    )

    comments = models.TextField(
        'Комментарии',
        max_length=300,
        blank=True,
    )

    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="рестораны",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    lon = models.FloatField(
        'долгота',
        blank=True,
        null=True,
    )

    lat = models.FloatField(
        'ширата',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField('Дата создания заказа',
                                      default=timezone.now,
                                      db_index=True)
    called_at = models.DateTimeField('Дата звонка уточнения заказа',
                                     blank=True,
                                     null=True,
                                     db_index=True)
    delivered_at = models.DateTimeField('Дата доставки заказа',
                                        blank=True,
                                        null=True,
                                        db_index=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class OrderDetails(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='продукты',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    quantity = models.IntegerField('количество',
                                   validators=[MinValueValidator(1),
                                               MaxValueValidator(10)])
    order = models.ForeignKey(
        Order,
        verbose_name='детали заказа',
        related_name='order_details',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'детали заказа'
        verbose_name_plural = 'детали заказов'

    def __str__(self):
        return f'{self.order.__str__()}'


class GeoPosition(models.Model):
    lon = models.FloatField(
        'долгота'
    )

    lat = models.FloatField(
        'ширата'
    )

    address = models.CharField(
        'адрес',
        max_length=50,
        db_index=True
    )

    created_at = models.DateTimeField('Дата создания заказа',
                                      auto_now=True,
                                      db_index=True)

    updated_at = models.DateTimeField('Дата обнавления заказа',
                                      auto_now=True,
                                      db_index=True)

    class Meta:
        verbose_name = 'геопозиция'
        verbose_name_plural = 'геопозиции'

    def __str__(self):
        return f'{self.address}'
