import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file', type=str,
            default='data/ingredients.json',
            help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

            for item in data:
                name = item.get('name')
                measurement_unit = item.get('measurement_unit')

                if name and measurement_unit:
                    Ingredient.objects.create(
                        name=name, measurement_unit=measurement_unit)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
