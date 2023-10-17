
from colorama import Style
import yaml


def bind(key):
    def get(self, key):
        self[key] = {} if not key in self else self[key]
        return self[key]

    def set(self, key, value):
        self[key] = value

    return property(
        lambda self: get(self, key),
        lambda self, value: set(self, key, value),
    )


def flatten(values, base=''):
    mapped = {}
    for key, val in values.items():
        subkey = f'{base}.{key}'
        if type(val) == dict:
            subvalues = flatten(val, subkey)
            mapped.update(subvalues)
        else:
            mapped[subkey] = val
    return mapped


def partial_values(values, prefix):
    found = {}
    for key in filter(lambda k: k.startswith(prefix), values):
        subpath = key[len(prefix):]
        found[subpath] = values[key]
    return found
