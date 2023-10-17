
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
