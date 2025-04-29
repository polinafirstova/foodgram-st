from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
import base64
import uuid
from rest_framework import serializers


class Base64ToImageField(Base64ImageField):
    def to_internal_value(self, data):
        if not data:
            return None

        try:
            if isinstance(data, str) and data.startswith('data:'):
                decoded_file = base64.b64decode(data.split(',')[1])
                file_name = str(uuid.uuid4())[:12]
                complete_file_name = f'{file_name}.jpg'
                data = ContentFile(decoded_file, name=complete_file_name)
            return data
        except TypeError as e:
            print(f'TypeError: {e}')
            self.fail('invalid_image')
        except Exception as e:
            print(f'Error: {e}')
            self.fail('invalid_image')


class Base64RequiredImageField(Base64ToImageField):
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('Это поле обязательно')
        return super().to_internal_value(data)
