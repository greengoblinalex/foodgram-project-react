from django import forms
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet


from .models import (FavoriteRecipe, Ingredient, Recipe,
                     RecipeIngredientAmount, ShoppingCartRecipe,
                     Tag, Subscription)
from .constants import (MIN_COOKING_TIME_VALUE, MIN_INGREDIENT_AMOUNT,
                        START_INGREDIENT_AMOUNT_FORMS)


class RecipeIngredientAmountFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        current_forms_count = self.total_form_count() - len(self.deleted_forms)

        if (current_forms_count < MIN_INGREDIENT_AMOUNT):
            raise ValidationError(
                'Необходимо добавить хотя бы один рецепт')

        for form in self.forms:
            if not all(form.cleaned_data.get(field)
                       for field in ['ingredient', 'amount']):
                raise ValidationError(
                    'Необходимо заполнить все данные о рецепте')


class RecipeIngredientAmountInline(admin.TabularInline):
    model = RecipeIngredientAmount
    formset = RecipeIngredientAmountFormSet
    extra = START_INGREDIENT_AMOUNT_FORMS


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        super().clean()
        cooking_time = self.cleaned_data.get('cooking_time')

        if not cooking_time:
            raise ValidationError('Необходимо указать время приготовления.')

        if cooking_time < MIN_COOKING_TIME_VALUE:
            raise ValidationError(
                'Время приготовления должно быть не менее 1 минуты.')

        tags = self.cleaned_data.get('tags')
        if not tags:
            raise ValidationError('Необходимо указать хотя бы один тег.')

        tag_ids = [tag.id for tag in tags]
        if len(set(tag_ids)) != len(tag_ids):
            raise ValidationError('Теги не должны дублироваться.')

        for tag_id in tag_ids:
            get_object_or_404(Tag, id=tag_id)


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
