from django.core.management.base import BaseCommand
import json
import os
from recipes.models import Recipe
from ingredients.models import Ingredient, IngredientInRecipe
from users.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Loads recipes from JSON file into the database'

    def handle(self, *args, **options):
        if Recipe.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                'Recipes already loaded, skipping.'))
            return
        self.load_from_json('recipes.json')
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded recipes'))

    def load_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                author_username = item['author']
                author = User.objects.get(username=author_username)

                recipe = Recipe.objects.create(
                    author=author,
                    name=item['name'],
                    image=item['image'],
                    text=item['text'],
                    cooking_time=item['cooking_time'],
                )

                for ingredient_data in item.get('ingredients', []):
                    ingredient = Ingredient.objects.get(
                        pk=ingredient_data['id'])
                    IngredientInRecipe.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=ingredient_data['amount']
                    )
