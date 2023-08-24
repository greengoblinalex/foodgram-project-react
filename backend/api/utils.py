import base64, uuid

from rest_framework import serializers
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
