from django.contrib.auth import get_user_model
from django.db import models

from .constants import UNIT_CHOICES

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    amount = models.IntegerField(
        verbose_name='Количество')
    measurement_unit = models.CharField(
        max_length=8, choices=UNIT_CHOICES,
        default='мин', verbose_name='Ед. Измерения'
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=256, unique=True,
        verbose_name='Название'
    )
    color = models.CharField(max_length=16, unique=True, verbose_name='Цвет')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag, related_name='recipes',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        User, related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes',
        verbose_name='Ингредиенты'
    )
    is_favorited = models.BooleanField(
        verbose_name='В избранных',
        default=False
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В корзине',
        default=False
    )
    name = models.CharField(
        max_length=256, verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='media/recipes/images/',
        blank=True, null=True, verbose_name='Картинка'
    )
    text = models.TextField(
        default='', null=True, blank=True,
        verbose_name='Описание'
    )
    cooking_time = models.DurationField(verbose_name='Время приготовления')

    def __str__(self):
        return self.name
