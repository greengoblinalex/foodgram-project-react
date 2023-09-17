from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.template.loader import get_template
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, User
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from weasyprint import HTML

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthor, ReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeListSerializer, RecipeFavoritesSerializer,
                          RecipeShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [ReadOnly()]
        elif self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [ReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ['name']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]


class RecipeCRUDViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnly | IsAuthor]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            is_favorited_subquery = Recipe.objects.filter(
                pk=OuterRef('pk'), favorited_by=user
            ).exists()
            is_in_shopping_cart_subquery = Recipe.objects.filter(
                pk=OuterRef('pk'), shopping_cart=user
            ).exists()

            queryset = queryset.annotate(
                is_favorited=Exists(is_favorited_subquery),
                is_in_shopping_cart=Exists(is_in_shopping_cart_subquery)
            )

        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.shopping_cart_recipes.all()

        ingredients_dict = {}

        for recipe in recipes:
            for amount in recipe.recipe_ingredient_amounts.all():
                ingredient_name = amount.ingredient.name
                measurement_unit = amount.ingredient.measurement_unit
                total_amount = amount.amount

                if ingredient_name in ingredients_dict:
                    ingredients_dict[ingredient_name][0] += total_amount
                else:
                    ingredients_dict[ingredient_name] = [
                        total_amount, measurement_unit
                    ]

        context = {
            'ingredients_dict': ingredients_dict
        }
        template = get_template('shopping_cart.html')
        content = template.render(context)

        response = HttpResponse(content, content_type='application/pdf')
        HTML(string=content).write_pdf(response)

        return response


class RecipeFavoritesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeFavoritesSerializer

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def add_to_favorites(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.add_to_favorites(instance):
            return Response(serializer, status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка добавления в избранное'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'],
            permission_classes=[IsAuthenticated])
    def remove_from_favorites(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.remove_from_favorites(instance):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка удаления из избранного'},
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeShoppingCartSerializer

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def add_to_shopping_cart(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.add_to_shopping_cart(instance):
            return Response(serializer, status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка добавления в список покупок'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'],
            permission_classes=[IsAuthenticated])
    def remove_from_shopping_cart(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.remove_from_shopping_cart(instance):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка удаления из списка покупок'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @action(detail=False, methods=['GET'])
    def get_subscriptions(self, request):
        user = request.user
        subscriptions = user.subscriptions.all()

        page = self.paginate_queryset(subscriptions)

        if page is not None:
            recipes_limit = int(self.request.query_params.get('recipes_limit'))
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={
                    'request': request,
                    'recipes_limit': recipes_limit
                }
            )
            return self.get_paginated_response(serializer.data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def add_to_subscriptions(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.add_to_subscriptions(instance):
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка подписки'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def remove_from_subscriptions(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.remove_from_subscriptions(instance):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка отписки'},
                        status=status.HTTP_400_BAD_REQUEST)
