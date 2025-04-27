from django.core.management.base import BaseCommand
import json
from ...models import Ingredient


class Command(BaseCommand):
    help = 'Loads ingredients from CSV and JSON files into the database'

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                'Ingredients already loaded, skipping.'))
            return
        self.load_from_json('ingredients.json')
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded ingredients'))

    def load_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.create(
                    name=item['name'], measurement_unit=item['measurement_unit'])
