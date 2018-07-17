from django_filters import rest_framework as filters
from django.db.models import Count
from bestiary.models import Creature, Dungeon


def filter_array_value(queryset, name, value):
    return queryset.filter(**{name: value.split(',')}).distinct()


def filter_reverse_lookup_count(queryset, name, value):
    # django-filter doesn't properly support the __len lookup
    count_name = name + '_count'
    return queryset.annotate(**{count_name: Count(name)}).filter(**{count_name: value})


def filter_has_all_related(queryset, name, value):
    filter_values = value.split(',')
    for val in filter_values:
        queryset = queryset.filter(**{name: val})

    return queryset.distinct()


class CreatureFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    archetype = filters.CharFilter(field_name='archetype__in', method=filter_array_value)
    element = filters.CharFilter(field_name='element__in', method=filter_array_value)
    group = filters.CharFilter(field_name='group__in', method=filter_array_value)
    subgroup = filters.CharFilter(field_name='subgroup__contains', method=filter_array_value)
    subgroup__contained_by = filters.CharFilter(method=filter_array_value)
    subgroup__overlap = filters.CharFilter(method=filter_array_value)
    lore = filters.CharFilter(lookup_expr='icontains')
    evolvesTo_count = filters.NumberFilter(field_name='evolvesTo', method=filter_reverse_lookup_count)

    spell_name = filters.CharFilter(field_name='spell__title', lookup_expr='istartswith')
    spell_description = filters.CharFilter(field_name='spell__description', lookup_expr='icontains')
    spell_turns = filters.NumberFilter(field_name='spell__turns')
    spell_turns__gte = filters.NumberFilter(field_name='spell__turns', lookup_expr='gte')
    spell_turns__lte = filters.NumberFilter(field_name='spell__turns', lookup_expr='lte')
    spell_passive = filters.BooleanFilter(field_name='spell__passive')
    spell_effect = filters.CharFilter(field_name='spell__spelleffect__effect', method=filter_has_all_related)
    spell_effect_any = filters.CharFilter(field_name='spell__spelleffect__effect__in', method=filter_array_value)
    spell_target = filters.CharFilter(field_name='spell__spelleffect__target__in', method=filter_array_value)
    scales_with = filters.CharFilter(field_name="spell__spelleffect__params__incBase__in", method=filter_array_value)

    class Meta:
        model = Creature
        fields = {
            'slug': ['exact', 'isnull'],
            'game_id': ['exact'],
            'creatureType': ['exact'],
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


class DungeonFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Dungeon
        fields = {
            'game_id': ['exact'],
            'group': ['exact'],
            'always_available': ['exact']
        }
