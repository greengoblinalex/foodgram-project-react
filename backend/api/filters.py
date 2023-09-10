from django.shortcuts import get_object_or_404
from django_filters.rest_framework import FilterSet, CharFilter
from django_filters import ModelMultipleChoiceFilter

from recipes.models import Ingredient, Recipe, Tag
from .serializers import User


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    is_favorited = CharFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_in_shopping_cart = CharFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    author = CharFilter(
        field_name='author',
        method='filter_by_author'
    )

    class Meta:
        model = Recipe
        fields = []

    def filter_is_favorited(self, queryset, name, value):
        if value == '1':
            user = self.request.user
            favorite_recipe_ids = [
                recipe.id for recipe in user.favorite_recipes.all()]
            return queryset.filter(id__in=favorite_recipe_ids)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            user = self.request.user
            shopping_cart_recipe_ids = [
                recipe.id for recipe in user.shopping_cart_recipes.all()]
            return queryset.filter(id__in=shopping_cart_recipe_ids)
        return queryset

    def filter_by_author(self, queryset, name, value):
        author = get_object_or_404(User, id=value)
        author_recipe_ids = [
            recipe.id for recipe in author.recipes.all()]
        return queryset.filter(id__in=author_recipe_ids)
