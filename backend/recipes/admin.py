from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorited_count',)
    list_filter = ('author', 'tags', 'name')
    search_fields = ('author', 'tags', 'name')


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )
    search_fields = ('name', )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredientAmount)
