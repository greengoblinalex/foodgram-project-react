from django_filters.rest_framework import FilterSet, CharFilter

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
