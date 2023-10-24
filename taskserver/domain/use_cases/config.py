from functools import reduce
import os
import random
import string
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig

HINT_EMPTY_VALUE = "Enter path to Taskfile.yaml or directory containing one"


def _new_id():  # Pseudo random id, to track this edit session
    return "_new_" + ''.join(random.choice(string.ascii_letters) for i in range(10))


class TaskConfigUseCase(TaskfileUseCase):

    @property
    def edits(self): return self.repo.getConfigEdits()

    def index(self, trigger_import=False):
        taskfile = self.edits  # Load a shadow copy of the config for editing

        # Detect any changed values
        changes = {}
        for key in taskfile.includes.keys():
            changes[key] = self.getStatusChange('includes', key)

        return {
            "title": "Configuration",
            "toolbar": "partials/toolbar/config.html",
            "taskfile": taskfile,
            "changes": changes,
            "trigger_import": trigger_import
        }

    def getStatusChange(self, property, key):
        # Get property values
        old = self.taskfile.dict().get(property, {})
        new = self.edits.dict().get(property, {})

        # Check for the key values (past and present)
        value = old.get(key) if type(old) == dict else None
        updated = new.get(key) if type(new) == dict else None

        # Compare and return the status
        if value == None and updated:
            return "New"  # New value detected
        elif updated == None:
            return "Deleted"  # Delete the existing value
        elif value != updated:
            return "Changed"  # Value has changed
        return "Unchanged"

    def newInclude(self, key, value):
        taskfile = self.edits  # Load a shadow copy of the config for editing
        id = key or _new_id()  # Track item with a unique id
        hint = value if value and key else HINT_EMPTY_VALUE
        focus = f'key_{id}' if not key else f'value_{id}'
        status = "New"  # Mark as new (for styling purposes)
        return {
            "taskfile": taskfile,
            "id": id,
            "key": key or "",
            "value": value or "",
            "autofocus": focus,
            "placeholder": hint,
            "status": status,
        }

    def getInclude(self, key, value=None):
        if not key:
            raise Exception('Key not found')
        taskfile = self.edits  # Load a shadow copy of the config for editing
        value = value if value != None else taskfile.includes.get(key, '')
        return {
            "taskfile": taskfile,
            "key": key,
            "value": value,
            "status": self.getStatusChange('includes', key),
        }

    def updateInclude(self, id, key, value, action=None):
        # Validate inputs for the given taskfile include
        errors = self.validateInclude(id, key, value)
        focus = f'key_{id}' if not key else f'value_{id}'
        changed = False        

        # Ckeck for key changes and validation errors
        if errors.get('key'):
            # Focus on key validation error(s)
            focus = f'key_{id}'
        elif key != id and id in self.edits.includes:
            # Include has been renamed
            print(f' * INCLUDES [ {id} -> {key} ] == {value} (renamed)')

            # We are renaming an existing item, so delete the old entry
            self.edits.includes[key] = self.edits.includes[id]
            del self.edits.includes[id]

            id = key  # Save the key as the new id
            focus = f'value_{key}'  # Move focus to value field

        # Check for any validation errors
        if not len(errors):
            # Only update the value if it changed
            changed = not key in self.edits.includes  # is new entry?
            changed = changed or self.edits.includes[key] != value
            if changed:
                print(f' * INCLUDES [ {key} ] == {value} (updated)')
                self.edits.includes[key] = value

        # Return the current state values
        return {
            "taskfile": self.edits,  # Use shadow copy for edit
            "id": id,
            "key": key or "",
            "value": value or "",
            "status": self.getStatusChange('includes', key),
            "placeholder": HINT_EMPTY_VALUE,
            "autofocus": focus,
            "errors": errors,
        }

    def validateInclude(self, old_key, key, value):
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

        if key and not key == old_key:
            if key in self.taskfile.includes:
                # Key is already defined, fail validation
                error("key", 'Key with this name already exists')

        # Check that the path exists
        basepath = os.path.dirname(self.taskfile.path)
        filepath = os.path.join(basepath, value)
        if not os.path.exists(filepath):
            # File or folder does not exists
            error("value", "File or folder path does not point to a taskfile")

        if os.path.isdir(filepath) and not os.path.isfile(filepath + "Taskfile.yaml"):
            # Cannot find a valid taskfile
            error(
                "value", f"Cannot resolve `{filepath}Taskfile.yaml` to a valid file.")

        return errors

    def deleteInclude(self, key):
        if not key:
            raise Exception("Expected 'include' key name.")
        if key in self.edits.includes:
            del self.edits.includes[key]  # Soft delete the value from memory

    # -----------------------------------------------------------------------
    # TODO: Deprecate the partial logic in favour of explicit
    # -----------------------------------------------------------------------

    def updatePartial(self, values):
        taskfile = self.taskfile
        # TODO: Re-enable update and save functionality
        # taskfile = TaskfileConfig.resolve(self.path)
        # taskfile.update(values)
        # taskfile.save(reload=True)
        result = {
            "title": "Configuration",
            "toolbar": "partials/toolbar/config.html",
            "taskfile": taskfile,
        }
        return result

    def updateValue(self, dest, key, value):
        taskfile = self.taskfile

        print(f'Update config.{dest}: {taskfile.path}')
        print(f' --> config[{dest}][{key}] == {value}')

        values = taskfile[dest] = taskfile[dest] if dest in taskfile else {}
        if not key in values or not value == values[key]:
            # Update the value that is stored in memory
            values[key] = value

        result = {
            "dest": dest,
            "key": key,
            "value": value,
            "focus": True,
            "taskfile": taskfile,
            "placeholder": "Enter value here",
        }

        return result

    def deleteValue(self, dest, key):
        if not key:
            raise Exception("Expected 'hx-trigger-name' header.")

        taskfile = self.taskfile
        if dest in taskfile and key in taskfile[dest]:
            del taskfile[dest][key]
