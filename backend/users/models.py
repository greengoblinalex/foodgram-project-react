from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_MAX_LENGTH, FIELD_MAX_LENGTH
from .managers import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    subscriptions = models.ManyToManyField(
        'self',
        related_name='subscribers',
        symmetrical=False,
        blank=True,
        verbose_name='Подписчики'
    )

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
