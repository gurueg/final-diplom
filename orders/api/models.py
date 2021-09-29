from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


USER_TYPES_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)

ORDER_STATUS_CHOICES = (
    ('basket', 'В корзине'),
    ('new', 'Новый'),
    ('accepted', 'Принят в обработку'),
    ('ready', 'Собран, ждет отправки'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен')
)


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    email = models.EmailField(verbose_name='Email пользователя', unique=True)
    username = models.CharField(
        verbose_name='Имя Пользователя',
        blank=True,
        max_length=100)
    usertype = models.CharField(
        'Тип пользователя',
        choices=USER_TYPES_CHOICES,
        max_length=50)
    is_activated = models.BooleanField(verbose_name="", default=False)

    def __str__(self):
        return str(self.email)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Contact(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='contacts',
        on_delete=models.CASCADE)
    city = models.CharField(verbose_name='Город', max_length=50)
    street = models.CharField(verbose_name='Улица', max_length=150)
    house = models.CharField(verbose_name='Дом', max_length=30)
    apartment = models.CharField(
        verbose_name='Квартира',
        max_length=10,
        blank=True)
    phone_number = models.CharField(
        verbose_name='Номер телефона пользователя',
        max_length=20)

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'

    class Meta:
        verbose_name = 'Контакты'


class Shop(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Название', max_length=50)
    # filename = models.FileField(
    #   verbose_name='Файл',
    #   upload_to=None,
    #   max_length=100)
    url = models.URLField(verbose_name='Источник данных', max_length=200)
    status = models.BooleanField(
        verbose_name='Работает ли магазин',
        default=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


class Category(models.Model):
    name = models.CharField(verbose_name='Название', max_length=80)
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    name = models.CharField(verbose_name='Название', max_length=50)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ProductModel(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=50)
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        related_name='info',
        on_delete=models.CASCADE)
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='infos',
        on_delete=models.CASCADE)
    price = models.PositiveIntegerField(verbose_name='Цена')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.name}: {self.price}'

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Parameter(models.Model):
    name = models.CharField(verbose_name='Характеристика', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class ModelParameter(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Характеристика',
        related_name='model_parameter',
        on_delete=models.CASCADE)
    product_model = models.ForeignKey(
        ProductModel,
        verbose_name='Модель',
        related_name='parameters',
        on_delete=models.CASCADE)
    value = models.CharField(
        verbose_name='Значение характеристики',
        max_length=150)

    class Meta:
        verbose_name = 'Значение характеристики'
        verbose_name_plural = 'Значения характеристик'
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'product_model'],
                name='unique_parameter_of_model'),
        ]

    def __str__(self):
        return str(self.value)


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Заказчик',
        related_name='orders',
        on_delete=models.CASCADE)
    status = models.CharField(
        verbose_name='Статус заказа',
        choices=ORDER_STATUS_CHOICES,
        max_length=50)
    saved_sum = models.PositiveIntegerField(
        verbose_name='Сумма заказа на момент оплаты',
        default=None,
        blank=True,
        null=True)
    contact = models.ForeignKey(
        Contact,
        verbose_name="Контакт заказчика",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None)

    def __str__(self):
        return str(self.status)

    @property
    def order_sum(self):
        if self.status == 'basket':
            summ = 0
            for item in self.items.all():
                summ += item.parameters.price * item.quantity
        else:
            summ = self.saved_sum
        return summ

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='items',
        on_delete=models.CASCADE)
    parameters = models.ForeignKey(
        ProductModel,
        verbose_name='Характеристики',
        related_name='ordered_items',
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'parameters'],
                name='unique_product_in_order'),
        ]

    def __str__(self):
        return str(self.quantity)
