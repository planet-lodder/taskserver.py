import os
import random
import string


class TaskfileInclude(dict):

    def __init__(self, taskfile, key, value, raw={}):
        self.id = key or self._new_id()  # Used for new items (without key name)
        self.key = key
        self.value = value
        self.taskfile = taskfile
        dict.__init__(self, **raw)

    def _new_id(self):
        letters = string.ascii_letters
        return "_new_" + ''.join(random.choice(letters) for i in range(10))

    def validate(self, key, value):
        errors = {}

        def error(key, message):
            errors[key] = errors[key] if key in errors else []
            errors[key].append(message)

        if not key:
            # Key is required
            error("key", "Key name is required")

        if not value:
            # Value is required
            error("value", "Value is required")

        if len(errors.keys()):
            # Basic validation failed, no need to run additional checks
            return errors

        # Check that the path exists
        basepath = os.path.dirname(self.taskfile._path)
        filepath = os.path.join(basepath, value)
        if not os.path.exists(filepath):
            # File or folder does not exists
            error("value", "File or folder path does not point to a taskfile")

        if os.path.isdir(filepath) and not os.path.isfile(filepath + "Taskfile.yaml"):
            # Cannot find a valid taskfile
            error(
                "value", f"Cannot resolve `{filepath}Taskfile.yaml` to a valid file.")

        return errors
