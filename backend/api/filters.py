from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredient, Recipe, Tag


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

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'tags', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_favorited=True)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_in_shopping_cart=True)
        return queryset
