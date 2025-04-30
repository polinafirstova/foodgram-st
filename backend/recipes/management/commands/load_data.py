from django.core.management.base import BaseCommand
import json
from ...models import Ingredient
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Loads ingredients from JSON file into the database'

    def handle(self, *args, **options):
        try:
            if Ingredient.objects.exists():
                self.stdout.write(self.style.SUCCESS(
                    'Ingredients already loaded, skipping.'))
                return

            project_root = settings.BASE_DIR
            file_path = os.path.join(project_root, 'ingredients.json')
            # Проверка нужна, чтобы загрузить продукты локально из /data/ingredients.json
            if not os.path.exists(file_path):
                file_path = os.path.join(
                    project_root, '..', 'data', 'ingredients.json')
                if not os.path.exists(file_path):
                    raise FileNotFoundError(
                        f'File not found')
            with open(file_path, 'r', encoding='utf-8') as file:
                created = Ingredient.objects.bulk_create(
                    [Ingredient(**item) for item in json.load(file)])
                self.stdout.write(self.style.SUCCESS(
                    f'Created {len(created)} new ingredients'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'An error occurred with file '
                f'{file_path}: {e}'
            ))
