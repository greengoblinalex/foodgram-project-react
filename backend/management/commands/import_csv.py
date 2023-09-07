import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=str,
            default='data/ingredients.csv',
            help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                name = row['name']
                measurement_unit = row['measurement_unit']

                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
