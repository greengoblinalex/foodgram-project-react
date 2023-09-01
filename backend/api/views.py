from rest_framework import viewsets, filters
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient, Tag, Recipe
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, TagSerializer, RecipePOSTSerializer, RecipeGETSerializer)
from .permissions import ReadOnly, RecipePermission
from .filters import IngredientFilter
from .utils import CustomPagination


class CustomUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'list':
            return CustomUserSerializer
        return super().get_serializer_class()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ['name']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    permission_classes = [ReadOnly | RecipePermission]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePOSTSerializer
        return RecipeGETSerializer
