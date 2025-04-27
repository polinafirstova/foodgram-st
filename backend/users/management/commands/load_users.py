from django.core.management.base import BaseCommand
import json
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Loads users from JSON file into the database'

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(self.style.SUCCESS(
                'Users already loaded, skipping.'))
            return
        self.load_from_json('users.json')
        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded users'))

    def load_from_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                User.objects.create_user(
                    username=item['username'],
                    email=item['email'],
                    password=item['password'],
                    first_name=item.get('first_name', ''),
                    last_name=item.get('last_name', ''),
                    is_staff=item.get('is_staff', False),
                    is_superuser=item.get('is_superuser', False),
                )
                if item.get('is_superuser', False):
                    user = User.objects.get(username=item['username'])
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
