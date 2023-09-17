from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Ingredient, Recipe, RecipeIngredientAmount, Tag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        favorited_by = cleaned_data.get('favorited_by')
        shopping_cart = cleaned_data.get('shopping_cart')

        if (Recipe.objects.filter(name=name, favorited_by=favorited_by
                                  ).exclude(id=self.instance.id).exists()):
            raise ValidationError(
                'This recipe is already in favorites for this user.')

        if (Recipe.objects.filter(name=name, shopping_cart=shopping_cart
                                  ).exclude(id=self.instance.id).exists()):
            raise ValidationError(
                'This recipe is already in the shopping cart for this user.')


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
