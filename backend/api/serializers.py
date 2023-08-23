import re

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.constants import USERNAME_PATTERN


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate(self, data):
        if not data['email'] or not data['username'] or not data['first_name'] or not data['last_name'] or not data['password']:
            raise serializers.ValidationError('Все поля должны быть заполнены')
        return data

    def validate_username(self, data):
        if not re.match(USERNAME_PATTERN, data):
            raise serializers.ValidationError(
                'Поле username должно содержать '
                'только буквы, цифры и знаки @/./+/-/_'
            )
        if data.lower() == 'me':
            raise serializers.ValidationError(
                'Недопустимое username: зарезервированное ключевое слово `me`')
        return data
