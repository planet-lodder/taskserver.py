
import os
import random
import string
import subprocess
import yaml
import json
import yq
from copy import deepcopy
from typing import Dict, List, Optional, Sequence

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.repositories.base import TaskfileRepository


class FilesystemTaskfileRepo(TaskfileRepository):
    # Internal variables
    taskfile: Taskfile = None
    tasks: List[Task] = None
    edits: Taskfile = None  # Keep track of changed values
    menu: TaskNode = None

    def __init__(self, filename: str):
        super().__init__(filename)

        # Load the taskfile into memory
        self.taskfile = self.tryLoadTaskfile(filename)

    # Try and load existing taskfile (if it exists)
    def tryLoadTaskfile(self, path) -> Taskfile:
        try:
            return Taskfile.load(path)
        except:
            # Load empty taskfile if not found on disk
            return Taskfile(path=path, includes={}, version=3, env={}, vars={}, tasks={})

    # Return the cached taskfile config
    def getConfig(self) -> Taskfile: return self.taskfile

    # Create a copy of the originals, for editing
    def getConfigEdits(self) -> Taskfile:
        self.edits = self.edits or deepcopy(self.taskfile)
        return self.edits

    # Save the given taskfile to disk
    def saveConfig(self, taskfile: Taskfile, reload=False) -> Taskfile:
        # Save the diffs back to the original taskfile
        # Note: We use diffs to preserve original file's YAML formatting
        self.saveDiffsOnly(taskfile.path, self.taskfile, taskfile)
        # Alternatively, if formatting is not an issue, we could simplify this to:
        # with open(taskfile.path) as f: f.write(yaml.safe_dump(taskfile))

        # After saving the taskfile, update the local caches
        self.taskfile = Taskfile.load(taskfile.path) if reload else taskfile
        self.edits = None

        return self.taskfile

    # Compares old and new values, to selectively update only changed values
    def saveDiffsOnly(self, filename: str, old: Taskfile, new: Taskfile):
        def flatten(values: dict, base=''):
            mapped = {}
            for key, val in values.items():
                subkey = f'{base}.{key}'
                if type(val) == dict:
                    subvalues = flatten(val, subkey)
                    mapped.update(subvalues)
                else:
                    mapped[subkey] = val
            return mapped

        # Get the mappings for all changed values
        oldvalues = flatten(old.dict())
        newvalues = flatten(new.dict())
        changed = {}
        deleted = {}
        for k, v in newvalues.items():
            if not k in oldvalues or oldvalues[k] != v:
                changed[k] = v
        for k, v in oldvalues.items():
            if not k in newvalues:
                deleted[k] = v
        diffs = {
            "changed": changed,
            "deleted": deleted
        }

        # Using the computed diffs, we will do partial updates
        for k, v in diffs["changed"].items():
            # Apply new and/or updated values
            print(f' * {k} = {v} (update)')
            yq.cli(['-iY', f'{k}={json.dumps(v)}', filename])
        for k, v in diffs["deleted"].items():
            # Delete removed values
            print(f' - {k} (delete)')
            yq.cli(['-iY', f'del({k})', filename])

    def listTasks(self) -> Sequence[Task]:
        if self.tasks:
            return self.tasks  # Use cached list of tasks
        try:
            # No cached list of tasks, so we go discover them
            taskfile = self.taskfile

            # Run: task --list-all --json
            output, err, res = Taskfile.run(taskfile.path, '--list-all --json')

            # Parse the JSON into a list of tasks
            obj = json.loads(output)

            # Parse the items into a list
            list = obj.get("tasks", [])
            path = obj.get("location", "")
            base = os.path.dirname(path) if path else os.getcwd()
            path = path.removeprefix(base + "/")
            tasks = []
            for item in list:
                # Update and normalize paths for all tasks by stripping base folder prefix
                loc = item.get("location", {})
                src = loc.get("taskfile", '')
                src = src.removeprefix(base + "/")
                task = Task(
                    src=src,
                    path=path,
                    name=item.get("name"),
                    desc=item.get("desc"),
                    up_to_date=bool(item.get('up_to_date', False)),
                )
                tasks.append(task)

            # Save ref to the new list of parse tasks
            self.tasks = tasks

            return tasks
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {taskfile.path}.')

    def searchTasks(self, terms) -> Sequence[Task]:
        def matches(val, term):
            return term.lower() in val.lower()

        def search(task):
            match_all = True
            if terms:
                # Search for each work in the terms given
                for term in terms.split(' '):
                    found = False
                    found = found or matches(task.name, term)
                    found = found or matches(task.desc, term)
                    match_all = match_all and found
            return match_all

        tasks = self.listTasks()  # Get the list of tasks to filter
        return tasks if not len(terms) else list(filter(search, tasks))

    def findTask(self, name) -> Optional[Task]:
        for task in filter(lambda t: t.name == name, self.listTasks()):
            return task
        return None

    def command(self, command, env={}) -> str:
        try:
            # Set the ENV vars to pass to the process
            env = os.environ.copy()
            env.update(env)

            # Build the command and run as sub process
            pop = command if type(command) == list else command.split(" ")
            res = subprocess.run(
                pop,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            # Get the output and error streams
            return res.stdout.decode()
        except Exception as e:
            print('ERROR!', e)
            return None

    def runShadowTask(self, path, task_raw):
        rand = ''.join(random.choice(string.ascii_letters) for i in range(10))
        temp_file = f'{path}.{rand}'

        # Read the original taskfile contents
        input = ""
        with open(path, 'r') as f:
            input = f.read()

        # Add the temp task to the manifest
        data = yaml.safe_load(input)
        data['tasks'] = data.get('tasks', {})
        data['tasks']['__env'] = task_raw

        # Create a shadow copy of the taskfile
        with open(temp_file, 'w') as f:
            f.write(yaml.dump(data))

        # Run the command to parse the values
        output = self.command(['task', '-t', temp_file, '__env'])

        # Remove the temp taskfile
        os.remove(temp_file)

        return output

    def getTaskValues(self, task: Task) -> TaskVars:
        if not task:
            return TaskVars() # No task was provided
        
        # Keep track of the evaluated task variables
        values = TaskVars()

        # Define a new (raw) task that will print each var value (to a file)
        rand = ''.join(random.choice(string.ascii_letters) for i in range(10))
        temp_path = f'.task/temp/vars/{rand}'
        cmds = [f'mkdir -p {temp_path}']  # Create folder if not exist

        # Get the raw task data
        data = self.taskfile.dict().get('tasks', {}).get(task.name)
        if not data:
            includes = filter(lambda x: x, self.taskfile.includes.keys())
            print(f'INCLUDE --=> {includes}')

        if not data or type(data) == list:
            # This task has no vars defined (or does ot exists)
            return values

        # Now that we have the raw task data, lets check for any custom vars to resolve
        vars = data.get('vars', {})
        for key in vars:
            val = vars[key]
            values.raw[key] = val
            cmds.append(f'echo -n {"{{ ."+key+" }}"} > {temp_path}/{key}.txt')

        # Using the target vars, resolve their current value
        self.runShadowTask(task.path, {
            "vars": vars,
            "cmds": cmds
        })

        for key in vars:
            val = ''
            file = f'{temp_path}/{key}.txt'
            with open(file, 'r') as f:
                val = f.read()
                values[key] = val
                values.eval[key] = val
            os.remove(file)  # Clean up temp files
        os.rmdir(temp_path)  # Clean up temp files

        return values

    def getMenu(self, task_path: str = '') -> Optional[TaskNode]:
        if not self.menu:
            # Generate the node list for the side navigation
            self.menu = TaskNode(path=self.taskfile.path, name='')
            self.menu.populate(self.listTasks())
        if not task_path:
            # Return the root node
            return self.menu
        # Search for the node by task path
        return self.menu.find(task_path)
