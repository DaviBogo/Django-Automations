import csv
from django.core.management.base import BaseCommand, CommandParser
from django.apps import apps
from dataentry.models import Student
import datetime
from dataentry.utils import generate_csv_file


class Command(BaseCommand):
    help = 'Export data from Student model to a CSV file'


    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Model name')


    def handle(self, *args, **kwargs):
        model_name = kwargs['model_name'].capitalize()

        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_config.label, model_name)
                break
            except LookupError:
                pass
        if not model:
            self.stderr.write(f'Model {model_name} could not found')
            return

        data = model.objects.all()

        file_path = generate_csv_file(model_name)
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow([field.name for field in model._meta.fields])

            for dt in data:
                writer.writerow([getattr(dt, field.name) for field in model._meta.fields])

        self.stdout.write(self.style.SUCCESS('Data exported succesfully!'))