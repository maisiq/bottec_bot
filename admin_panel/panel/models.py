from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, URLValidator
from django.db import models
from slugify import slugify


class User(AbstractUser):  # Чтобы проще вносить изменения
    pass


class UserBot(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=128, blank=True, null=True)
    username = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(validators=[MinValueValidator(0)], max_digits=10, decimal_places=2)
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='products',
    )
    image = models.URLField(validators=[URLValidator()])


class Promo(models.Model):
    name = models.CharField(max_length=156)
    text = models.TextField(help_text='Текст промо с MARKDOWN_V2 разметкой')
    cover = models.URLField(validators=[URLValidator()], help_text='Ссылка на изображение')
    text_link = models.CharField(max_length=64, default='Перейти', help_text='Текст для кнопки')
    link = models.URLField(validators=[URLValidator()], help_text='Ссылка для встраивания в кнопку')
    start_time = models.DateTimeField(help_text='Дата и время начала рассылки, UTC')
    last_succeeded_at = models.DateTimeField(blank=True, null=True, help_text='Последнее успешное выполнение, UTC')
    active = models.BooleanField(default=True)
