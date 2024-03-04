from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Prints Hello World"

    def handle(self, *args, **kwargs):
        print('Hello World 1')
        self.stdout.write('Hello World')