from django import forms
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import (
    FavoriteRecipe, Ingredient, Recipe,
    RecipeIngredientAmount, ShoppingCartRecipe, Tag, Subscription
)
from .constants import MIN_COOKING_TIME_VALUE


class RecipeIngredientAmountInline(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data['cooking_time']
        if cooking_time < MIN_COOKING_TIME_VALUE:
            raise ValidationError(
                'Время приготовления должно быть не менее 1 минуты.')
        return cooking_time

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if not tags:
            raise ValidationError('Необходимо указать хотя бы один тег.')

        tag_ids = [tag.id for tag in tags]
        if len(set(tag_ids)) != len(tag_ids):
            raise ValidationError('Теги не должны дублироваться.')

        for tag_id in tag_ids:
            get_object_or_404(Tag, id=tag_id)

        return tags

    def clean_ingredients(self):
        ingredients = self.cleaned_data['ingredients']
        if not ingredients:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент.')

        ingredient_ids = [ingredient['ingredient']['id']
                          for ingredient in ingredients]

        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise ValidationError('Ингредиенты не должны дублироваться.')

        for ingredient_id in ingredient_ids:
            get_object_or_404(Ingredient, id=ingredient_id)

        return ingredients


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'tags', 'name')
    search_fields = ('author__username', 'tags__name', 'name')
    inlines = [RecipeIngredientAmountInline]
    form = RecipeAdminForm


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )
    search_fields = ('name', )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCartRecipe)
admin.site.register(Subscription)
