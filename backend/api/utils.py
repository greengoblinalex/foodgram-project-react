import base64
import uuid

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.core.files.base import ContentFile


class Base64ImageField(serializers.Field):
    def to_internal_value(self, data):
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        decoded_img = base64.b64decode(imgstr)

        # Генерируем уникальное имя файла
        file_name = f"{uuid.uuid4()}.{ext}"

        return ContentFile(decoded_img, name=file_name)

    def to_representation(self, value):
        return value.url if value else None


class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_page_size(self, request):
        page_size = int(request.query_params.get('limit', self.page_size))

        return max(page_size, 1)


def get_is_subscribed(self, instance):
    user = self.context['request'].user
    if user.is_authenticated:
        return instance in user.subscriptions.all()
    return False
