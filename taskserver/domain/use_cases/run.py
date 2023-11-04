import datetime
import os

from ansi2html import Ansi2HTMLConverter
from ansi2html.style import (get_styles)
from click import Command
from colorama import Fore, Style

from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.TaskBreakdown import TaskCommand
from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.models.TaskRun import TaskRun
from taskserver.domain.models.Taskfile import Taskfile
from taskserver.domain.serializers import Serializer
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.base import TaskfileUseCase
from taskserver.domain.use_cases.task import TaskUseCase


class TaskRunUseCase(TaskUseCase):

    def runIndex(self, input: TaskRequest, node: TaskNode, job_id: str):
        run = self.repo.getTaskRun(job_id) if job_id else None
        name = run.task.name if run and run.task else input.name
        task = self.repo.findTask(name) if name else None
        breakdown = self.taskBreakdown(name, run) if name else None
        result = self.base(task) if task else {
            "taskfile": self.taskfile,
            "task": task,
        }
        result.update({
            "title": task.name if task else "unknown",
            "toolbar": "partials/toolbar/task.html",
            "disabled": True,  # Clear the change status
            "output": self.format_output(run.stdout) if run else '',
            "run": run,
            "breakdown": breakdown,
        })

        return result

    def createRun(self, task: Task, vars: dict, cli_args=''):
        # Create a new object to track the process and its output
        vars = self.getRunVars(task)
        run = TaskRun(task=task, vars=vars, cli_args=cli_args)
        run.breakdown = self.taskBreakdown(task.name, run) if task else None

        # Now that the task has been started, clear run vars and reload details
        self.repo.saveTaskRun(run)
        self.clearRunVars(task)

        return self.repo.startTaskRun(run)

    def tryRun(self, input: TaskRequest, node: TaskNode, vars={}):
        task = self.repo.findTask(input.name) if node else None
        vars = self.getRunVars(task) if task and not len(vars.keys()) else vars
        result = self.base(task) if task else {
            "taskfile": self.taskfile,
            "task": task,
            "name": input.name,
        }
        result.update({
            "title": task.name if task else "unknown",
            "toolbar": "partials/toolbar/task.html",
            "open": input.req.input('open'),
            "cli_args": input.req.input('cli_args', ''),
        })

        # Check for validation issues
        if not input.validate():
            result.update({"error": '\n'.join(input.errors)})
            return result
        if not task:
            result.update({"error": 'Task not found'})
            return result

        try:
            # Create a new run session and spawn the task
            run = self.createRun(task, vars, result.get("cli_args", ''))

            # TODO: Format the terminal output to HTML
            output = self.format_output(run.stdout) if run.stdout else ''

            # Capture the details to the task that was spawned
            result.update({
                "run": run,
                "vars": vars,  # Show run vars (pinned)
                "changes": {},  # Clear the change status
                "disabled": True,  # Clear the change status
                "output": output,
            })
        except Exception as ex:
            # The task failed to launch
            print(f'{Fore.RED}{ex}{Style.RESET_ALL}')
            result.update({"error": str(ex)})

        return result

    def runDialog(self, task_name: str):
        task = self.repo.findTask(task_name)
        result = self.base(task) if task else {
            "taskfile": self.taskfile,
            "task": task,
            "name": task_name,
        }
        if not task and task_name:
            result.update({"error": 'No Task with that name'})
        elif not task:
            result.update({"error": 'Please enter a task name'})

        return result

    def runStatus(self, job_id: str):
        run = self.repo.getTaskRun(job_id) if job_id else None
        return {
            "run": run,
        }

    def runVarDetails(self, task_name, key_name):
        task = self.repo.findTask(task_name)
        return {
            "taskfile": self.taskfile,
            "task": task,
            "key": key_name,
            "value": "",
        }

    def getRunBreakdown(self, task_name: str, job_id: str, state):
        task = self.repo.findTask(task_name)
        run = self.repo.getTaskRun(job_id) if job_id else None
        breakdown = self.taskBreakdown(task_name, run)

        if state == 'expand' or state == 'collapse':
            # Expand / collapse all task commands
            self.toggleCommandRecursive(breakdown, state == 'expand')
            if run:
                self.repo.saveTaskRun(run)  # Update state
        
        result = self.base(task)
        result.update({
            "breakdown": breakdown,
            "run": run
        })
        return result

    def toggleCommandRecursive(self, cmd: Command, state: bool):
        if not cmd or not isinstance(cmd, TaskCommand):
            return

        parent: TaskCommand = cmd
        parent.open = state
        for item in parent.cmds:
            self.toggleCommandRecursive(item, state)

    def toggleRunBreakdown(self, task_name: str, job_id: str, index: str, state: bool):
        task = self.repo.findTask(task_name)
        run = self.repo.getTaskRun(job_id) if job_id else None
        breakdown = self.taskBreakdown(task_name, run)

        # Start from the current task breakdown root
        cmd = breakdown
        if index:
            # Find the indexed task command to toggle
            for pos in index.split(','):
                i = int(pos)
                cmd = cmd.cmds[i] if cmd and i < len(cmd.cmds) else None
        if cmd:
            # Toggle command state
            cmd.open = state
        if cmd and run:
            # Update state of the breakdown
            run.breakdown = breakdown
            self.repo.saveTaskRun(run)

        # Build the result object
        result = self.base(task)
        result.update({
            "breakdown": breakdown,
            "indexed": index,
            "cmd": cmd,
            "run": run
        })
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
            lambda e: e.klass.lstrip(".") in formatted["styles"],
            all_styles
        )
        style = "\n".join(
            list(map(str, backgrounds + list(used_styles))))

        body = formatted["body"]
        output = f'<style>{style}</style>\n<pre>{body}</pre>'
        return output
