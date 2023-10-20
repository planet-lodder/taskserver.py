

from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.run import TaskRunUseCase


class TaskRunInputs(TaskRequest):
    _task = None

    def parse(self):
        super().parse()  # Parse task properties

        if not self.name:
            error = 'Please specify a task name'
            self.errors.append(error)
        
        #if not self._task:
        #    error = f'Task "{self.name}" could not be found.'
        #    self.errors.append(error)
            
        return self._task


@router.post('/run')
@router.renders('task/single')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    task = input.selected(view.repo)
    vars = req.inputs('config.vars.', strip_prefix=True)
    result = view.tryRun(input, task, vars)

    return result


@router.get('/run/dialog')
@router.renders('partials/run/modal')
def taskRunDialog(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Open a modal dialog to run task with parameters
    result = view.runDialog(input.name)

    return result


@router.post('/run/dialog')
@router.renders('partials/run/modal')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Run the task with the given parameters supplied by the modal dialog
    task = input.selected(view.repo)
    result = view.tryRun(input, task)
    failed = "error" in result and result["error"]

    if failed:
        return result  # Validation failed or runtime invalid

    # Task run has been confirmed, clear the modal and force refresh of main display
    return router.render_template("partials/run/confirm.html", result)


@router.get('/run/var')
@router.renders('partials/run/vars/item')
def taskRunDialog(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Get the task variable details
    key = input.htmx.prompt if input.htmx else ''
    return view.runVarDetails(input.name, key)


@router.get('/run/breakdown')
@router.renders('partials/run/list')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)    

    # Do a breakdown of the current task
    result = view.breakdown(input.name)
    return result
