import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    help = 'Импорт тегов из tags.json'

    def handle(self, *args, **kwargs):
        with open('./recipes/management/commands/tags.json',
                  encoding='utf8') as file:
            self.stdout.write('Загрузка тегов в базу данных...')
            Tag.objects.bulk_create(
                [Tag(
                    name=data['name'],
                    color=data['color'],
                    slug=data['slug']
                ) for data in json.load(file)]
            )
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка тегов произошла успешно!'
            )
        )
