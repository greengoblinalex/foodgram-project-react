from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None,
                         password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not extra_fields.get('first_name'):
            raise ValueError('The first_name field must be set')
        if not extra_fields.get('last_name'):
            raise ValueError('The last_name field must be set')

        return self._create_user(username, email, password, **extra_fields)
