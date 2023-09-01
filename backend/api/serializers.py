import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from recipes.models import Ingredient, RecipeIngredientAmount, Tag, Recipe
from users.constants import USERNAME_PATTERN
from .utils import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, data):
        if not data['email'] or not data['username'] or not data['first_name'] or not data['last_name'] or not data['password']:
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
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeGETSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='amount')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')


class RecipePOSTSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientAmountSerializer(
        many=True, source='amount')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')

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

    # def update(self, instance, validated_data):
    #     tags_data = validated_data.pop('tags')
    #     ingredients_data = validated_data.pop('ingredients')

    #     instance.name = validated_data.get('name', instance.name)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time', instance.cooking_time)
    #     instance.save()

    #     instance.tags.clear()
    #     for tag_data in tags_data:
    #         tag, created = Tag.objects.get_or_create(**tag_data)
    #         instance.tags.add(tag)

    #     instance.ingredients.clear()
    #     for ingredient_data in ingredients_data:
    #         ingredient, created = Ingredient.objects.get_or_create(
    #             **ingredient_data)
    #         instance.ingredients.add(ingredient)

    #     return instance
