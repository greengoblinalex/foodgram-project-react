from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

from .constants import (MAX_MEASUREMENT_UNIT_LENGTH, MAX_NAME_LENGTH,
                        MAX_SLUG_LENGTH, UNIT_CHOICES)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название',
        blank=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        choices=UNIT_CHOICES,
        default='ст. л.',
        verbose_name='Ед. Измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'measurement_unit')


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='HEX цвет'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
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
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В корзине',
        default=False
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='media/recipes/images/',
        blank=False, null=True, verbose_name='Картинка'
    )
    text = models.TextField(
        default='', null=True, blank=True,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    favorited_by = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True,
        verbose_name='Избрано пользователями'
    )
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
