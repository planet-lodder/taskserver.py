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

    def update(self, partials):
        # Update the partial values
        for subpath, value in partials.items():
            curr = self
            parts = subpath.split('.')
            while len(parts):
                key = parts[0]
                parts = parts[1:]
                if len(parts) == 0:
                    # Set the (updated) value
                    curr[key] = value
                else:
                    # Walk the tree to the edge leaf
                    curr = curr[key]

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

    def flatten(self, values, base=''):
        mapped = {}
        for key, val in values.items():
            subkey = f'{base}.{key}'
            if type(val) == dict:
                subvalues = self.flatten(val, subkey)
                mapped.update(subvalues)
            else:
                mapped[subkey] = val
        return mapped

    def diffs(self):
        oldvalues = self.flatten(self._orig)
        newvalues = self.flatten(self)
        changed = {}
        deleted = {}
        for k, v in newvalues.items():
            if not k in oldvalues or oldvalues[k] != v:
                changed[k] = v
        for k, v in oldvalues.items():
            if not k in newvalues:
                deleted[k] = v
        return {
            "changed": changed,
            "deleted": deleted
        }

    def save(self, reload=False):
        print(f'Saving config changes to "{self._path}"...')
        diffs = self.diffs()
        for k, v in diffs["changed"].items():
            # Apply new and/or updated values
            print(f' * {k} = {v} (update)')
            self.save_partial(k, v)
        for k, v in diffs["deleted"].items():
            # Delete removed values
            print(f' - {k} (delete)')
            self.delete_partial(k)

        if reload:
            # Reload config from disk
            new = TaskfileConfig.load(self._path)
            self.clear()
            self.update(new)
            self._orig = new._orig

    def save_partial(self, yaml_path, value):
        # Update a subpath of the YAML document (eg: `.vars.VERSION='0.0.1'`)
        yq.cli(['-iY', f'{yaml_path}={json.dumps(value)}', self._path])

    def delete_partial(self, yaml_path):
        # Update a subpath of the YAML document (eg: `del(.env.VERSION)`)
        yq.cli(['-iY', f'del({yaml_path})', self._path])






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
