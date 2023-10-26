import os

from ansi2html import Ansi2HTMLConverter
from ansi2html.style import (get_styles)

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.TaskRun import TaskRun
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.serializers import Serializer
from taskserver.domain.use_cases.base import TaskfileUseCase
from taskserver.domain.use_cases.task import TaskUseCase


class TaskRunUseCase(TaskUseCase):

    def createRun(self, task: Task, vars: dict):
        # Create a new object to track the process and its output
        info = TaskRun(
            task=task,
            vars=self.getRunVars(task)
        )

        # Now that the task has been started, clear run vars and reload details
        self.clearRunVars(task)

        return info

    def tryRun(self, input: Serializer, node: TaskNode, vars={}):
        task = self.repo.findTask(node.name)
        result = self.base(task)
        result.update({
            "title": task.name if task else "unknown",
            "toolbar": "partials/toolbar/task.html",
        })
        if input.validate():
            try:
                # Create a new run session and spawn the task
                run = self.createRun(task, vars)
                run.start()

                # TODO: Format the terminal output to HTML
                output = self.format_output(run.stdout) if run.stdout else ''

                # Capture the details to the task that was spawned
                result.update({
                    "run": run,
                    "vars": vars, # Show run vars (pinned)
                    "changes": {}, # Clear the change status
                    "output": output,
                })
            except Exception as ex:
                # The task failed to launch
                print(f'Something went wrong: {ex}')
                result.update({"error": str(ex)})
        else:
            result.update({"error": '\n'.join(input.errors)})

        return result

    def tryRunDialog(self, input: Serializer, task: Task):
        result = self.base(task)
        if input.validate():
            try:
                # Add HEAD and BODY values to ENV vars
                env = os.environ.copy()

                # Execute the task command (given the input HEAD and BODY)
                output, _, _ = Taskfile.run(self.taskfile.path, task.name, env)
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

    def runDialog(self, task_name: str):
        task = self.repo.findTask(task_name)
        return {
            "taskfile": self.taskfile,
            "task": task,
            "name": task_name,
        }

    def runVarDetails(self, task_name, key_name):
        task = self.repo.findTask(task_name)
        return {
            "taskfile": self.taskfile,
            "task": task,
            "key": key_name,
            "value": "",
        }

    def format_output(self, output):
        if not output:
            return ""

        converter = Ansi2HTMLConverter(linkify=True)
        formatted = converter.prepare(output)

        dark_bg = formatted["dark_bg"]
        all_styles = get_styles(dark_bg)
        backgrounds = all_styles[:5]
        used_styles = filter(
            lambda e: e.klass.lstrip(".") in formatted["styles"],
            all_styles
        )
        style = "\n".join(
            list(map(str, backgrounds + list(used_styles))))

        body = formatted["body"]
        output = f'<style>{style}</style>\n<pre>{body}</pre>'
        return output
