from django.core.management.base import BaseCommand
from bestiary import parse


class Command(BaseCommand):
    def handle(self, *args, **options):
        parse.spells()
        parse.creatures()
