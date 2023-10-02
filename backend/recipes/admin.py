from django import forms
from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe,
                     RecipeIngredientAmount, ShoppingCartRecipe, Tag,
                     Subscription)


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'tags', 'name')
    search_fields = ('author', 'tags', 'name')


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )
    search_fields = ('name', )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredientAmount)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCartRecipe)
admin.site.register(Subscription)
