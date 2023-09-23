import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open('./recipes/management/commands/ingredients.json',
                  encoding='utf8') as file:
            self.stdout.write('Загрузка ингредиентов в базу данных...')
            Ingredient.objects.bulk_create(
                [Ingredient(
                    name=data['name'],
                    measurement_unit=data['measurement_unit']
                ) for data in json.load(file)]
            )
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка ингредиентов произошла успешно!'
            )
        )
