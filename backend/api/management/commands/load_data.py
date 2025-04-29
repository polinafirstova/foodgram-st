from django.core.management.base import BaseCommand, CommandError
import json
from api.models import Ingredient, IngredientInRecipe, Recipe, User
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Loads data (ingredients, recipes, users) from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['ingredients', 'recipes', 'users'],
            help='Type of data to load (ingredients, recipes, users)',
        )

    def handle(self, *args, **options):
        data_type = options['type']

        if data_type == 'ingredients':
            self.load_ingredients(self._get_data_file_path('ingredients.json'))
        elif data_type == 'recipes':
            self.load_recipes(self._get_data_file_path('recipes.json'))
        elif data_type == 'users':
            self.load_users(self._get_data_file_path('users.json'))
        else:
            raise CommandError(
                'Invalid data type. Choose from ingredients, recipes, users.')

    def load_ingredients(self, filename):
        self._load_data(filename, 'ingredients', self._process_ingredients)

    def load_recipes(self, filename):
        self._load_data(filename, 'recipes', self._process_recipes)

    def load_users(self, filename):
        self._load_data(filename, 'users', self._process_users)

    def _get_data_file_path(self, filename):
        project_root = settings.BASE_DIR

        data_dir = os.path.join(project_root, 'data')
        if not os.path.exists(data_dir):
            data_dir = os.path.join(project_root, '..', 'data')
            if not os.path.exists(data_dir):
                raise FileNotFoundError(
                    f'Data directory not found')

        return os.path.join(data_dir, filename)

    def _load_data(self, filename, data_type, process_function):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                process_function(data)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'{filename} not found!'))
            raise
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                f'Invalid JSON format in {filename}!'))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
            raise

    def _process_ingredients(self, data):
        existing_ingredients = Ingredient.objects.values_list(
            'name', flat=True)
        ingredients_to_create = []
        for item in data:
            if item['name'] not in existing_ingredients:
                ingredients_to_create.append(Ingredient(**item))
        Ingredient.objects.bulk_create(ingredients_to_create)
        self.stdout.write(self.style.SUCCESS(
            f'Created {len(ingredients_to_create)} new ingredients'))

    def _process_recipes(self, data):
        recipes_created = 0
        existing_recipe_names = Recipe.objects.values_list('name', flat=True)
        try:
            all_users = {user.username: user for user in User.objects.all()}
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error fetching users: {e}. Skipping recipes.'))
            return

        for item in data:
            if item['name'] not in existing_recipe_names:
                author_username = item['author']
                author = all_users.get(author_username)
                if not author:
                    self.stdout.write(self.style.ERROR(
                        f'Author with username «{author_username}» not found! '
                        + f'Skipping recipe «{item['name']}»'))
                    continue

                recipe = Recipe.objects.create(
                    author=author,
                    name=item['name'],
                    image=item['image'],
                    text=item['text'],
                    cooking_time=item['cooking_time'],
                )
                recipes_created += 1

                ingredients_in_recipe = []
                for ingredient_data in item.get('ingredients', []):
                    try:
                        ingredient = Ingredient.objects.get(
                            name=ingredient_data['name'])
                        ingredients_in_recipe.append(
                            IngredientInRecipe(
                                recipe=recipe,
                                ingredient=ingredient,
                                amount=ingredient_data['amount']
                            )
                        )
                    except Ingredient.DoesNotExist:
                        self.stdout.write(self.style.ERROR(
                            f'Ingredient «{ingredient_data['name']}» not found! '
                            f'Skipping ingredient in recipe «{recipe.name}»'))
                        continue

                IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)

        self.stdout.write(self.style.SUCCESS(
            f'Created {recipes_created} new recipes'))

    def _process_users(self, data):
        users_to_create = []
        for item in data:
            if not User.objects.filter(username=item['username']).exists() and \
                    not User.objects.filter(email=item['email']).exists():
                user = User(
                    username=item['username'],
                    email=item['email'],
                    first_name=item.get('first_name', ''),
                    last_name=item.get('last_name', ''),
                    is_staff=item.get('is_staff', False),
                    is_superuser=item.get('is_superuser', False),
                )
                user.set_password(item['password'])
                users_to_create.append(user)

        created_users = User.objects.bulk_create(users_to_create)

        for item, user in zip(data, users_to_create):
            if item.get('is_superuser', False):
                user.is_staff = True
                user.is_superuser = True
                user.save()

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(created_users)} new users'))
