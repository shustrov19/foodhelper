import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка в базу данных из ingredients.json'

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json',
                  encoding='utf8') as file:
            data = json.load(file)
            ingredients = []
            for i in data:
                ingredients.append(
                    Ingredient(name=i['name'],
                               measurement_unit=i['measurement_unit'])
                    )
            print('Загрузка в базу данных...')
            Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка произошла успешно!'
            )
        )
