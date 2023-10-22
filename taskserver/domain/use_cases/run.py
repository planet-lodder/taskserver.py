import os

from ansi2html import Ansi2HTMLConverter
from ansi2html.style import (get_styles)

from taskserver.domain.models.Task import Task
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.serializers import Serializer
from taskserver.domain.use_cases.taskfile import TaskfileUseCase
from taskserver.models.TaskfileConfig import TaskfileConfig


class TaskRunUseCase(TaskfileUseCase):

    def findTask(self, task_name: str) -> Task:
        return self.root.find(task_name)

    def breakdown(self, task_name: str):
        task = self.findTask(task_name)
        breakdown = []

        if task and self.taskfile:
            # Not a leaf node, so show the search results instead
            config = TaskfileConfig.resolve(self.path)
            breakdown = config.breakdown(task.key)

        # Show the task view
        return {
            "task": task,
            "taskfile": self.taskfile,
            "breakdown": breakdown,
        }

    def runDialog(self, task_name: str):
        task = self.root.find(task_name)
        return {
            "taskfile": self.taskfile,
            "task": task,
            "name": task_name,
        }

    def runVarDetails(self, task_name, key_name):
        task = self.root.find(task_name)
        return {
            "taskfile": self.taskfile,
            "task": task,
            "key": key_name,
            "value": "",
        }

    def tryRunDialog(self, input: Serializer, task: Task):
        result = {
            "taskfile": self.taskfile,
            "task": task,
            "name": task.name,
        }
        if input.validate():
            try:
                # Add HEAD and BODY values to ENV vars
                env = os.environ.copy()

                # Execute the task command (given the input HEAD and BODY)
                output = self.taskfile.run(task.name, env)
                output = self.format_output(output)

                # Capture the details to the task that was spawned
                result.update({"output": output})

            except Exception as ex:
                # The task failed to launch
                print(f'Something went wrong: {ex}')
                result.update({"error": str(ex)})
        else:
            result.update({"error": '\n'.join(input.errors)})

        return result

    def tryRun(self, input: Serializer, node: TaskNode, vars={}):
        task = self.repo.findTask(node.key)
        result = {
            "title": task.key if task else "unknown",
            "toolbar": "partials/toolbar/task.html",
            "taskfile": self.taskfile,
            "task": task,
            "name": task.name,
            "vars": vars,
        }
        if input.validate():
            try:
                # Add HEAD and BODY values to ENV vars
                env = vars

                # Execute the task command (given the input HEAD and BODY)
                output = self.taskfile.run(task.name, env)
                output = self.format_output(output)

                # Capture the details to the task that was spawned
                result.update({"output": output})

            except Exception as ex:
                # The task failed to launch
                print(f'Something went wrong: {ex}')
                result.update({"error": str(ex)})
        else:
            result.update({"error": '\n'.join(input.errors)})

        return result

    def format_output(self, output):
        if not output:
            return ""

        converter = Ansi2HTMLConverter(linkify=True)
        formatted = converter.prepare(output)

        dark_bg = formatted["dark_bg"]
        all_styles = get_styles(dark_bg)
        backgrounds = all_styles[:5]
        used_styles = filter(
            lambda e: e.klass.lstrip(
                ".") in formatted["styles"], all_styles
        )
        style = "\n".join(
            list(map(str, backgrounds + list(used_styles))))

        body = formatted["body"]
        output = f'<style>{style}</style>\n<pre>{body}</pre>'
        return output
