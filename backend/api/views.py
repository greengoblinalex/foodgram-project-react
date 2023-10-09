from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import FileResponse
from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCartRecipe, Tag, User)
from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeFavoritesSerializer, RecipeListSerializer,
                          RecipeShoppingSerializer,
                          SubscriptionCreateDeleteSerializer,
                          SubscriptionListSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action in ['list', 'retrieve', 'me']:
            return CustomUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthorOrReadOnly()]
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthorOrReadOnly]


class RecipeCRUDViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()

        if user.is_authenticated:
            favorited_by_user_subquery = FavoriteRecipe.objects.filter(
                recipe=OuterRef('pk'),
                user=user
            ).values('recipe')

            in_shopping_cart_subquery = ShoppingCartRecipe.objects.filter(
                recipe=OuterRef('pk'),
                user=user
            ).values('recipe')

            queryset = queryset.annotate(
                is_favorited=Exists(favorited_by_user_subquery),
                is_in_shopping_cart=Exists(in_shopping_cart_subquery)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))

        recipes = ShoppingCartRecipe.objects.filter(user=request.user)

        ingredients_dict = {}

        for recipe in recipes:
            for amount in recipe.recipe.recipe_ingredient_amounts.all():
                ingredient_name = amount.ingredient.name
                measurement_unit = amount.ingredient.measurement_unit
                total_amount = amount.amount

                if ingredient_name in ingredients_dict:
                    ingredients_dict[ingredient_name][0] += total_amount
                else:
                    ingredients_dict[ingredient_name] = [
                        total_amount, measurement_unit
                    ]

        buffer = BytesIO()
        c = canvas.Canvas(buffer)

        c.setFont('DejaVuSerif', 12)

        c.drawString(100, 800, 'Список покупок:')
        y_position = 780

        for ingredient_name, data in ingredients_dict.items():
            text = f'{ingredient_name}: {data[0]} {data[1]}'
            c.drawString(100, y_position, text)
            y_position -= 20

        c.save()

        buffer.seek(0)

        response = FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf')
        return response


class RecipeFavoritesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeFavoritesSerializer

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def add_to_favorites(self, request, pk=None):
        data = {
            'recipe': self.get_object().id,
            'user': request.user.id
        }
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        return Response({'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'],
            permission_classes=[IsAuthenticated])
    def remove_from_favorites(self, request, pk=None):
        favorited_recipe = request.user.favorite_recipes.get(
            recipe=self.get_object())

        if favorited_recipe:
            favorited_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка удаления из избранного'},
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeShoppingSerializer

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def add_to_shopping_cart(self, request, pk=None):
        data = {
            'recipe': self.get_object().id,
            'user': request.user.id
        }
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка добавления в список покупок'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'],
            permission_classes=[IsAuthenticated])
    def remove_from_shopping_cart(self, request, pk=None):
        favorited_recipe = request.user.shopping_cart_recipes.get(
            recipe=self.get_object())

        if favorited_recipe:
            favorited_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка удаления из карзины'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'DELETE']:
            return SubscriptionCreateDeleteSerializer
        return SubscriptionListSerializer

    @action(detail=False, methods=['GET'])
    def get_subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscriptions_as_user__subscriber=request.user)

        page = self.paginate_queryset(subscriptions)

        if page is not None:
            recipes_limit = int(self.request.query_params.get('recipes_limit'))
            serializer = SubscriptionListSerializer(
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
        data = {
            'user': self.get_object().id,
            'subscriber': request.user.id
        }
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        return Response({'message': 'Ошибка подписки'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def remove_from_subscriptions(self, request, pk=None):
        subscribe = self.get_object().subscriptions_as_user.get(
            subscriber=request.user)

        if subscribe:
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'message': 'Ошибка удаления из карзины'},
                        status=status.HTTP_400_BAD_REQUEST)
