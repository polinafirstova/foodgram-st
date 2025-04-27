from drf_extra_fields.fields import Base64ImageField
from django.core.files.base import ContentFile
import base64
import imghdr
import uuid
from rest_framework.exceptions import ParseError


class CustomBase64ImageField(Base64ImageField):

    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and data.startswith('data:'):
                decoded_file = base64.b64decode(data.split(',')[1])

                file_name = str(uuid.uuid4())[:12]
                file_extension = self.get_file_extension(
                    file_name, decoded_file)

                complete_file_name = "%s.%s" % (file_name, file_extension,)
                data = ContentFile(decoded_file, name=complete_file_name)
            return data
        except TypeError as e:
            print(f'TypeError: {e}')
            self.fail('invalid_image')
        except Exception as e:
            print(f'TypeError: {e}')
            self.fail('invalid_image')

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension

        if not extension:
            raise ParseError('Could not determine file type')

        return extension
