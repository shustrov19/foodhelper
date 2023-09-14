import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка в базу данных из ingredients.json'

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json',
                  encoding='utf8') as file:
            self.stdout.write('Загрузка в базу данных...')
            Ingredient.objects.bulk_create(
                [Ingredient(
                    name=data['name'],
                    measurement_unit=data['measurement_unit']
                    ) for data in json.load(file)]
            )
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка произошла успешно!'
            )
        )
