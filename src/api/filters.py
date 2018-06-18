from django_filters import rest_framework as filters

from bestiary.models import Creature


def filter_array_contains(queryset, name, value):
    return queryset.filter(**{f'{name}__contains': value.split(',')})


def filter_array_contained_by(queryset, name, value):
    return queryset.filter(**{f'{name}__contained_by': value.split(',')})


def filter_array_overlap(queryset, name, value):
    return queryset.filter(**{f'{name}__overlap': value.split(',')})


class CreatureFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')
    archetype = filters.ChoiceFilter(choices=Creature.ARCHETYPE_CHOICES)
    element = filters.ChoiceFilter(choices=Creature.ELEMENT_CHOICES)
    group = filters.ChoiceFilter(choices=Creature.GROUP_CHOICES)
    subgroup = filters.CharFilter(method=filter_array_contains)
    subgroup__contained_by = filters.CharFilter(method=filter_array_contained_by)
    subgroup__overlap = filters.CharFilter(method=filter_array_overlap)
    lore = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Creature
        fields = {
            'playable': ['exact'],
            'summonable': ['exact'],
            'rank': ['exact', 'gte', 'lte'],
            'hp': ['exact', 'gte', 'lte'],
            'attack': ['exact', 'gte', 'lte'],
            'defense': ['exact', 'gte', 'lte'],
            'criticalChance': ['exact', 'gte', 'lte'],
            'criticalDamage': ['exact', 'gte', 'lte'],
            'accuracy': ['exact', 'gte', 'lte'],
            'resistance': ['exact', 'gte', 'lte'],
            'initialSpeed': ['exact', 'gte', 'lte'],
            'speed': ['exact', 'gte', 'lte'],
        }
