from django.core.management.base import BaseCommand
from bestiary import parse


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Parsing regions...')
        parse.regions()
        print('Parsing levels...')
        parse.levels()
        print('Done!')
