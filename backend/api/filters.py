from django_filters.rest_framework import FilterSet, CharFilter
from django_filters import ModelMultipleChoiceFilter

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
