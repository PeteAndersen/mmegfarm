import json

from .xml import get_spell_random_data


# string true/false to bool
def to_boolean(string):
    return string in ['true', 'True', 'TRUE']


def params_to_dict(params):
    ret = {}
    for param in params.split(','):
        values = param.split(':')
        if len(values) == 2:
            # key:value pair
            try:
                # See if it's an int or float by parsing it
                value = json.loads(values[1])
                ret[values[0]] = value
            except json.JSONDecodeError:
                # Just interpret as string
                ret[values[0]] = values[1]
        else:
            # simply presence of key
            ret[values[0]] = True

    if 'spell' in ret:
        ret['spell'] = get_spell_random_data(ret['spell'])

    return ret
