from django.core.management.base import BaseCommand
import json
from ...models import Ingredient
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Loads ingredients from JSON file into the database'

    def handle(self, *args, **options):
        try:
            project_root = settings.BASE_DIR
            possible_paths = [
                # Путь для загрузки продуктов из ./ingredients.json
                # (если проект запускается с использованием докера)
                os.path.join(project_root, 'ingredients.json'),
                # Путь для загрузки продуктов из data/ingredients.json
                # (если проект запускается локально без использования докера)
                os.path.join(project_root, '..', 'data', 'ingredients.json'),
            ]

            for file_path in possible_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        created = Ingredient.objects.bulk_create(
                            [Ingredient(**item) for item in json.load(file)],
                            ignore_conflicts=True)
                        self.stdout.write(self.style.SUCCESS(
                            f'Created {len(created)} new ingredients'))
                        break
                except FileNotFoundError:
                    continue
            else:
                raise FileNotFoundError(
                    f'File not found in any of the specified paths')

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'An error occurred: {e}'
            ))
