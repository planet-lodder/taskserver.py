
import json
import logging
import os
import subprocess

import yaml

from taskserver.utils import bind


class TaskfileServer(dict):
    location = bind("location")
    config = bind("config")
    tasks = bind("tasks")

    def __init__(self, location="Taskfile.yaml", tasks=[]):
        dict.__init__(self, location=location, tasks=tasks)
        self.log = logging.getLogger('task-server')
        self.config = self.load(location)

    def list(self):
        return self.tasks

    def filter(self, terms):
        def matches(key, vals, term):
            return key in vals and term.lower() in vals[key].lower()

        def search(task):
            if not terms:
                return True

            # Search for each work in the terms given
            match_all = True
            for term in terms.split(' '):
                found = False
                found = found or matches("name", task, term)
                found = found or matches("desc", task, term)
                found = found or matches("summary", task, term)
                match_all = match_all and found

            return match_all
        if len(terms):
            return list(filter(search, self.tasks))
        return self.tasks

    def load(self, path=None, reload=False):
        path = path if path else self.location
        if not os.path.isfile(path):
            raise Exception(f"Taskfile {path} not found!")

        try:
            command = f"task -t {self.location} --list-all --json"
            pop = command.split(" ")
            res = subprocess.run(pop, stdout=subprocess.PIPE)
            raw = res.stdout.decode().strip()
            obj = json.loads(raw)
        except Exception as e:
            raise Exception(
                f'{e}\n\nWARNING: Failed to load and parse the taskfile: {path}.')

        cwd = os.getcwd()
        path = obj["location"] if "location" in obj else ""
        list = obj["tasks"] if "tasks" in obj else []

        if reload:
            # Clear currrent list of tasks
            self.tasks = []

        # Update and normalize paths for all tasks by stripping base folder prefix
        self.location = path = path.removeprefix(cwd + "/")
        for task in list:
            # Append the task to list of known tasks
            self.tasks.append(task)

            # Update sub task location
            if "location" in task and "taskfile" in task["location"]:
                path = task["location"]["taskfile"]
                path = path.removeprefix(cwd + "/")
                task["location"]["taskfile"] = path

        # Load the raw config file for this taskfile
        with open(self.location, "r") as stream:
            self.config = yaml.safe_load(stream)
            return self.config

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def test():
    taskfile = TaskfileServer()
    res = taskfile
    out = json.dumps(res, indent=2)
    print(out)


if __name__ == '__main__':
    test()
