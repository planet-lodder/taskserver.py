
from asyncio import Task
from taskserver.domain.models.Task import TaskVars
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskUseCase(TaskfileUseCase):

    def base(self, task: Task):
        if not task:
            raise Exception('Task is not defined')

        # Get the task vars and their current status
        vars = self.getRunVars(task)
        changes = {}
        for key in vars:
            changes[key] = self.getRunVarStatus(vars, key)

        return {
            "taskfile": self.taskfile,
            "task": task,

            # Set the htmx hooks for task run variables
            "dest": f'task',
            "vars": vars,
            "changes": changes,
            "htmx_base": "/taskserver/run/var",
        }

    def getRunVars(self, task: Task):
        # Get the current run variables (if they are cached in the session)
        runVars = self.session.runVars.get(task.name)

        if not runVars:
            # Fetch the current task run vars and keep track of changes
            runVars = self.repo.getTaskValues(task) if task else {}
            self.session.runVars[task.name] = runVars

        return runVars

    def setRunVar(self, task_name: str, key: str, value):
        task = self.repo.findTask(task_name)
        runVars = self.getRunVars(task) if task else {}
        runVars[key] = value  # Update run var value
        return self.getRunVarStatus(runVars, key)

    def getRunVarStatus(self, runVars: TaskVars, key: str):
        # Get the new updated status
        status = "Unchanged"

        raw = runVars.raw
        eval = runVars.eval
        if not key in runVars or not key in raw:
            status = "New"
        elif not key in runVars and key in raw:
            status = "Deleted"
        elif key in eval and runVars[key] != eval[key]:
            status = "Changed"

        return status

    def updateRunVar(self, task_name, dest, key, value):
        taskfile = self.taskfile

        # Add the (updated) value to the (edited) taskfile
        status = self.setRunVar(task_name, key, value)
        print(f' * {status}: {dest}.{key} = {value}')
        result = {
            "dest": dest,
            "key": key,
            "value": value,
            "focus": True,
            "status": status,
            "taskfile": taskfile,
            "placeholder": "Enter value here",
            "htmx_base": "/taskserver/run/var",
            "htmx_query": f"?name={task_name}&key={key}"
        }

        return result

    def deleteRunVar(self, task_name, dest, key):
        if not task_name or not key:
            raise Exception("Expected task 'name' and 'key' for TaskVar.")

        print(f' * DELETE: {dest}.{key}')
        task = self.repo.findTask(task_name)
        runVars = self.getRunVars(task) if task else None
        if runVars and key in runVars:
            del runVars[key]  # Update run var value
