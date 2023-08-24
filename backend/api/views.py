from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet

from recipes.models import Ingredient, Tag, Recipe
from .serializers import CustomUserCreateSerializer, IngredientSerializer, TagSerializer, RecipeSerializer
from .permissions import ReadOnly, IsAuthenticated, IsAuthor, RecipePermission


class CustomUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly]
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]
    pagination_class = PageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    permission_classes = [ReadOnly | RecipePermission]
    pagination_class = PageNumberPagination
