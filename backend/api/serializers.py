import base64
import re
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredientAmount, ShoppingCartRecipe,
                            Subscription, Tag)
from users.constants import USERNAME_PATTERN

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, data):
        if not re.match(USERNAME_PATTERN, data):
            raise serializers.ValidationError(
                'Поле username должно содержать '
                'только буквы, цифры и знаки @/./+/-/_'
            )

        if data.lower() == 'me':
            raise serializers.ValidationError(
                'Недопустимое username: зарезервированное ключевое слово `me`')

        return data


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated and instance.subscriptions_as_user.filter(
                subscriber=user).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        required=False
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.Field):
    def to_internal_value(self, data):
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        decoded_img = base64.b64decode(imgstr)

        file_name = f'{uuid.uuid4()}.{ext}'

        return ContentFile(decoded_img, name=file_name)

    def to_representation(self, value):
        return value.url if value else None


class RecipeListSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='recipe_ingredient_amounts')
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')


class RecipeIngredientAmountCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientAmount
        fields = ('recipe', 'ingredient', 'amount')

    def validate_amount(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Количество должно быть положительным числом.')
        return data

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient')
        recipe_ingredient_amount = RecipeIngredientAmount.objects.create(
            ingredient=ingredient,
            **validated_data
        )
        return recipe_ingredient_amount


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='recipe_ingredient_amounts')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    @staticmethod
    def create_recipe_ingredient_amounts(ingredients, recipe):
        recipe_ingredient_amounts = []

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']

            serializer = RecipeIngredientAmountCreateSerializer(
                data={
                    'ingredient': ingredient_id,
                    'amount': amount,
                    'recipe': recipe.id
                }
            )

            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

            recipe_ingredient_amounts.append(serializer.save())

        return recipe_ingredient_amounts

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient_amounts')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.create_recipe_ingredient_amounts(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient_amounts')

        super().update(instance, validated_data)

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.clear()
        self.create_recipe_ingredient_amounts(ingredients, instance)

        return instance


class RecipeMiniListSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeFavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return RecipeMiniListSerializer(
            instance.recipe, context=self.context).data

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.favorite_recipes.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в избранное.')
        return data


class RecipeShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCartRecipe
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return RecipeMiniListSerializer(
            instance.recipe, context=self.context).data

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.shopping_cart_recipes.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в карзину.')
        return data


class SubscriptionListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def to_representation(self, instance):
        user_data = CustomUserSerializer(
            instance.user, context=self.context).data

        subscription_data = {
            'recipes': self.get_recipes(instance),
            'recipes_count': self.get_recipes_count(instance),
        }

        representation = {**user_data, **subscription_data}

        return representation

    def get_recipes(self, instance):
        recipes_limit = self.context.get('recipes_limit')
        recipes = instance.user.recipes.all().order_by('-id')[:recipes_limit]
        return RecipeMiniListSerializer(recipes, many=True).data

    def get_recipes_count(self, instance):
        return instance.user.recipes.count()


class SubscriptionCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'subscriber')

    def to_representation(self, instance):
        return CustomUserSerializer(instance.user, context=self.context).data

    def validate(self, data):
        request = self.context['request']
        if request.user.id == data['user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return data
