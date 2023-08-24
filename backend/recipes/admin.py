from django.contrib import admin

from .models import Ingredient, Tag, Recipe

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
