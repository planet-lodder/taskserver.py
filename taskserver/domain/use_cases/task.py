
from taskserver.domain.models.Task import Task, TaskVars
from taskserver.domain.models.TaskBreakdown import TaskBreakdown
from taskserver.domain.models.TaskRun import TaskRun
from taskserver.domain.use_cases.base import TaskfileUseCase


class TaskUseCase(TaskfileUseCase):

    def base(self, task: Task, breakdown: TaskBreakdown = None, vars: TaskVars = None):
        if not task:
            raise Exception('Task is not defined')

        # Get the task vars and their current status
        vars = vars or self.getRunVars(task)
        changes = self.getRunVarStatusMap(vars)
        results = self.defaults()
        results.update({
            "task": task,
            "name": task.name if task else None,

            # Set the htmx hooks for task run variables
            "dest": f'task',
            "vars": vars,
            "changes": changes,
            "breakdown": breakdown or self.taskBreakdown(task.name),
            "htmx_base": "/taskserver/run/var",
        })

        return results

    def runToolbar(self, task_name: str, job_id: str = None):
        results = self.defaults()
        run = self.repo.getTaskRun(job_id) if job_id else None
        task = self.repo.findTask(task_name) if task_name else None
        results.update({
            "task": task,
            "run": run,
        })
        return results

    def getRunVars(self, task: Task):
        # Get the current run variables (if they are cached in the session)
        runVars = self.session.runVars.get(task.name)

        if not runVars:
            # Fetch the current task run vars and keep track of changes
            runVars = self.repo.getTaskValues(task) if task else {}
            self.session.runVars[task.name] = runVars

        return runVars

    def clearRunVars(self, task: Task):
        # Get the current run variables (if they are cached in the session)
        if task.name in self.session.runVars:
            del self.session.runVars[task.name]

    def setRunVar(self, task_name: str, key: str, value):
        task = self.repo.findTask(task_name)
        runVars = self.getRunVars(task) if task else {}
        runVars[key] = value  # Update run var value
        return self.getRunVarStatus(runVars, key)

    def getRunVarStatus(self, runVars: TaskVars, key: str):
        raw = runVars.raw
        eval = runVars.eval

        # Get the new updated status
        status = "Unchanged"
        if not key in runVars or not key in raw:
            status = "New"
        elif not key in runVars and key in raw:
            status = "Deleted"
        elif key in eval and runVars[key] != eval[key]:
            status = "Changed"

        return status

    def getRunVarStatusMap(self, vars: TaskVars):
        changes = {}
        for key in vars:
            changes[key] = self.getRunVarStatus(vars, key)
        return changes

    def updateRunVar(self, task_name, dest, key, value):
        taskfile = self.taskfile

        # Add the (updated) value to the (edited) taskfile
        task = self.repo.findTask(task_name)
        status = self.setRunVar(task_name, key, value)
        print(f' * {status}: {dest}.{key} = {value}')
        result = {
            "dest": dest,
            "key": key,
            "value": value,
            "focus": True,
            "task": task,
            "status": status,
            "taskfile": taskfile,
            "placeholder": "Enter value here",
            "htmx_base": "/taskserver/run/var",
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

    def taskBreakdown(self, task_name: str, run: TaskRun = None, reload=False):
        # Check if we have a task breakdown cached in the run
        if run and run.breakdown:
            return run.breakdown  # Load the cached version

        # Try and resolve the breakdown from cache
        session = self.session
        breakdown = session.breakdown.get(task_name)
        if not breakdown:
            # Generate the task breakdown for current this session
            breakdown = TaskBreakdown.forTask(self.taskfile.path, task_name)
            session.breakdown[task_name] = breakdown

        if run and not run.breakdown:
            run.breakdown = breakdown.copy(deep=True)
            self.repo.saveTaskRun(run)
            return run.breakdown  # Return the cloned copy

        # Show the task view
        return breakdown
