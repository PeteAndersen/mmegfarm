from django_filters import rest_framework as filters

from bestiary.models import Creature, SpellEffect


def filter_array_value(queryset, name, value):
    return queryset.filter(**{name: value.split(',')})


class CreatureFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')
    archetype = filters.ChoiceFilter(choices=Creature.ARCHETYPE_CHOICES)
    element = filters.ChoiceFilter(choices=Creature.ELEMENT_CHOICES)
    group = filters.ChoiceFilter(choices=Creature.GROUP_CHOICES)
    subgroup = filters.CharFilter(name='subgroup__contains', method=filter_array_value)
    subgroup__contained_by = filters.CharFilter(method=filter_array_value)
    subgroup__overlap = filters.CharFilter(method=filter_array_value)
    lore = filters.CharFilter(lookup_expr='icontains')

    spell_name = filters.CharFilter(name='spell__title', lookup_expr='istartswith')
    spell_description = filters.CharFilter(name='spell__description', lookup_expr='icontains')
    spell_turns = filters.NumberFilter(name='spell__turns')
    spell_turns__gte = filters.NumberFilter(name='spell__turns', lookup_expr='gte')
    spell_turns__lte = filters.NumberFilter(name='spell__turns', lookup_expr='lte')
    spell_passive = filters.BooleanFilter(name='spell__passive')
    spell_effect = filters.CharFilter(name='spell__spelleffect__effect', lookup_expr='iexact')
    spell_target = filters.ChoiceFilter(
        name='spell__spelleffect__target',
        choices=SpellEffect.TARGET_CHOICES,
    )
    spell_params_contains = filters.CharFilter(
        name='spell__spelleffect__params__has_keys',
        method=filter_array_value
    )

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