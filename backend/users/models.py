from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import EMAIL_MAX_LENGTH, FIELD_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        blank=True,
        null=False,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        blank=True,
        null=False,
        unique=True,
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        blank=True,
        null=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        blank=True,
        null=False,
        verbose_name='Фамилия'
    )
