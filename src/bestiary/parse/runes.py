from .xml import TRANSLATION_STRINGS, get_rune_data_from_rewardpattern, get_rune_type_data, get_rune_rarity_data, get_rune_shape_data


def reward_rune(pattern_sku):
    rune_data = get_rune_data_from_rewardpattern(pattern_sku)
    rune_type = [
        TRANSLATION_STRINGS[get_rune_type_data(rtype)['name']]
        for rtype in rune_data['type'].split(',')
    ]
    rarity = TRANSLATION_STRINGS[get_rune_rarity_data(rune_data['rarity'])['name']]
    shape = [get_rune_shape_data(shape)['name'] for shape in rune_data['shape'].split(',')]
    stars = int(rune_data['stars'])  # Stars is number of substats (0 through 5)

    return {
        'type': rune_type,
        'rarity': rarity,
        'shape': shape,
        'stars': stars,
    }
