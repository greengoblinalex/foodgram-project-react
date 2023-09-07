from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .constants import UNIT_CHOICES

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=True
    )
    measurement_unit = models.CharField(
        max_length=9, choices=UNIT_CHOICES,
        default='ст. л.', verbose_name='Ед. Измерения'
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
        Ingredient,
        through='RecipeIngredientAmount',
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
        blank=False, null=True, verbose_name='Картинка'
    )
    text = models.TextField(
        default='', null=True, blank=True,
        verbose_name='Описание'
    )
    cooking_time = models.IntegerField(verbose_name='Время приготовления')
    favorited_by = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True,
        verbose_name='Избрано пользователями'
    )
    favorited_count = models.IntegerField(
        verbose_name='Общее число добавлений в избранное', default=0)
    shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart_recipes',
        blank=True,
        verbose_name='В корзине у пользователей'
    )

    def __str__(self):
        return self.name


class RecipeIngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredient_amounts',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredient_amounts',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество')
