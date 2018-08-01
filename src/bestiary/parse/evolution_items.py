from .xml import get_evolution_item, get_evolutionitem_data_from_rewardpattern


def evolution_item_reward(sku):
    items = []
    pattern_data = get_evolutionitem_data_from_rewardpattern(sku)
    small_qty = int(pattern_data['small'])
    if small_qty > 0:
        item_data = get_evolution_item(pattern_data['smallEvolutionItemSku'])
        items.append({
            'type': item_data['type'],
            'size': item_data['size'],
            'quantity': small_qty
        })

    large_qty = int(pattern_data['big'])
    if large_qty > 0:
        item_data = get_evolution_item(pattern_data['bigEvolutionItemSku'])
        items.append({
            'type': item_data['type'],
            'size': item_data['size'],
            'quantity': large_qty
        })

    return items
