from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient, Tag, Recipe
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, TagSerializer, RecipePOSTSerializer, RecipeGETSerializer)
from .permissions import ReadOnly, RecipePermission
from .filters import IngredientFilter, RecipeFilter
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return RecipePOSTSerializer
        return RecipeGETSerializer

    @action(detail=True, methods=['POST'])
    def add_to_favorites(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.add_to_favorites(instance):
            fields = ('id', 'name', 'image', 'cooking_time')
            selected_data = {key: serializer.data[key]
                             for key in fields if key in serializer.data}

            return Response(selected_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Ошибка добавления в избранное'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def remove_from_favorites(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.remove_from_favorites(instance):
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'Ошибка удаления из избранного'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def download_shopping_cart(self, request, pk=None):
        user = request.user
        recipes = user.shopping_cart_recipes.all()

        context = {'recipes': recipes}
        template = get_template('shopping_cart.html')
        content = template.render(context)

        response = HttpResponse(content, content_type='application/pdf')
        HTML(string=content).write_pdf(response)

        return response

    @action(detail=True, methods=['POST'])
    def add_to_shopping_cart(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.add_to_shopping_cart(instance):
            fields = ('id', 'name', 'image', 'cooking_time')
            selected_data = {key: serializer.data[key]
                             for key in fields if key in serializer.data}

            return Response(selected_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Ошибка добавления в список покупок'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def remove_from_shopping_cart(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.remove_from_shopping_cart(instance):
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'Ошибка удаления из списка покупок'}, status=status.HTTP_400_BAD_REQUEST)
