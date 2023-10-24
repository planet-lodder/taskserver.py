import os
import json
import re
import subprocess
from colorama import Style, Fore
import yaml
import yq

from copy import deepcopy

# In-memory cache of all the taskfiles by path name
TASKFILE_CACHE = {}


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


class TaskfileConfig(dict):
    version = bind("version")
    includes = bind("includes")
    env = bind("env")
    vars = bind("vars")
    tasks = bind("tasks")

    # Keep track of the original values
    _orig = {}
    _path = None

    def __init__(self, raw={}):
        self._orig = deepcopy(raw)  # Save ref to original values
        dict.__init__(self, **raw)

    def status(self, yaml_path):
        if not yaml_path[0] == '.':
            raise Exception(f'Not a valid yaml path: {yaml_path}')

        old = self._orig
        new = self
        parts = yaml_path.split('.')[1:]
        while len(parts):
            key = parts[0]
            parts = parts[1:]

            # Walk the tree to the edge leaf
            old = old[key] if old and key in old else None
            new = new[key] if new and key in new else None

            if len(parts) == 0:
                # Set the (updated) value
                if not new and old:
                    return "Deleted"
                if new and not old:
                    return "New"
                if new and old and json.dumps(new) != json.dumps(old):
                    return "Changed"
                return "Unchanged"

        return True


    @staticmethod
    def load(path):
        if not os.path.isfile(path):
            raise Exception(f"Taskfile {path} not found!")

        # Load the raw config file for this taskfile
        with open(path, "r") as stream:
            raw = yaml.safe_load(stream)
            res = TaskfileConfig(raw)
            res._path = path
            return res

    @staticmethod
    def resolve(path=None):
        path = path if path else "Taskfile.yaml"

        # Load the config into memory if not already cached
        if not path in TASKFILE_CACHE:
            TASKFILE_CACHE[path] = TaskfileConfig.load(path)

        return TASKFILE_CACHE[path]
