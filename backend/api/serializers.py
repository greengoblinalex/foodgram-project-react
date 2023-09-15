import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredientAmount, Tag
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.constants import USERNAME_PATTERN

from .utils import Base64ImageField, get_is_subscribed

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, data):
        if (not data['email']
                or not data['username']
                or not data['first_name']
                or not data['last_name']
                or not data['password']):
            raise serializers.ValidationError('Все поля должны быть заполнены')

        return data

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
        return get_is_subscribed(self, instance)


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
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='recipe_ingredient_amounts')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance in user.favorite_recipes.all()
        return False

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance in user.shopping_cart_recipes.all()
        return False


class RecipePOSTSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='recipe_ingredient_amounts')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient_amounts')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )

            RecipeIngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient_amounts')

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.clear()
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )

            RecipeIngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=instance,
                amount=ingredient['amount']
            )

        instance.save()

        return instance

    def add_to_favorites(self, instance):
        user = self.context['request'].user
        user.favorite_recipes.add(instance)
        instance.favorited_count = instance.favorited_by.count()
        instance.save()
        return True

    def remove_from_favorites(self, instance):
        user = self.context['request'].user
        user.favorite_recipes.remove(instance)
        instance.favorited_count = instance.favorited_by.count()
        instance.save()
        return True

    def add_to_shopping_cart(self, instance):
        user = self.context['request'].user
        user.shopping_cart_recipes.add(instance)
        return True

    def remove_from_shopping_cart(self, instance):
        user = self.context['request'].user
        user.shopping_cart_recipes.remove(instance)
        return True


class RecipeSubscriptionSerializer(RecipeGETSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        request = self.context['request']
        if request.user.id == data['id']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        return data

    def add_to_subscriptions(self, instance):
        user = self.context['request'].user
        user.subscriptions.add(instance)
        return True

    def remove_from_subscriptions(self, instance):
        user = self.context['request'].user
        user.subscriptions.remove(instance)
        return True

    def get_recipes(self, instance):
        recipes_limit = self.context.get('recipes_limit')
        recipes = instance.recipes.all().order_by('-id')[:recipes_limit]
        return RecipeSubscriptionSerializer(recipes, many=True).data

    def get_recipes_count(self, instance):
        return instance.recipes.count()

    def get_is_subscribed(self, instance):
        return get_is_subscribed(self, instance)
