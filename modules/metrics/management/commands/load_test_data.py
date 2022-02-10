from django.core.management.base import BaseCommand
import csv
from ...models import Metric


class Command(BaseCommand):
    help = 'Load test data from csv file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument(
            '-d',
            '--delimiter',
            type=str,
            default=',',
            help='custom delimiter'
        )

    def handle(self, *args, **options):
        filename = options['filename']
        delimiter = options['delimiter']

        with open(filename) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=delimiter)

            Metric.objects.bulk_create([
                Metric(**entry) for entry in reader
            ])
