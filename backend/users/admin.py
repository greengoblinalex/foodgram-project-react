from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class CustomUserAdmin(BaseUserAdmin):
    list_filter = ('username', 'email')


admin.site.register(User, CustomUserAdmin)
