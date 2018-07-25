from django.core.management.base import BaseCommand
from bestiary import parse


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Parsing creatures...')
        parse.creatures()
        print('Setting evolution relationships...')
        parse.evolutions()
        print('Parsing spells...')
        parse.spells()
        print('Updating special cases...')
        parse.special_case_creatures()
        print('Done!')
