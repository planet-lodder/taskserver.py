

from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.run import TaskRunUseCase


class TaskRunInputs(TaskRequest):

    def parse(self):
        super().parse()  # Parse task properties

        if not self.name:
            error = 'Please specify a task name'
            self.errors.append(error)


class TaskRunVar(WebSerializer):
    path: str = ''
    task: str = ''
    key: str = ''
    value: str = ''

    def parse(self):
        self.path = self.req.query.get('path', 'Taskfile.yaml')
        self.task = self.req.input('name', self.req.query.get('name', ''))
        self.key = self.req.query.get('key', '')
        self.value = self.req.input(f'value', '')

        if not self.key and self.htmx:
            # Look for request originating from HTMX interactions
            if requested_key := self.htmx.prompt:
                self.key = requested_key  # User entered new key name from prompt

        # Ensure that the key is defined before continuing
        if not self.key:
            raise Exception('Key required for config value.')

    def forUpdate(self, dest):
        # Get the key value
        self.value = self.req.input(f'config.{dest}.{self.key}', '')

        # Return relevant information
        return self.task, dest, self.key, self.value

    def forDelete(self, dest):
        return self.task, dest, self.key


@router.post('/run')
@router.renders('task/single')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    node = input.selected(view.repo)
    vars = req.inputs('config.task.', strip_prefix=True)
    result = view.tryRun(input, node, vars)

    return result


@router.get('/run/var')
@router.renders('partials/run/vars/item')
def taskRunVar(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Get the task variable details
    key = input.htmx.prompt if input.htmx else ''
    return view.runVarDetails(input.name, key)


@router.post('/run/var')
@router.renders("partials/values/item")
def taskUpdateRunVar(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunVar)
    return view.updateRunVar(*input.forUpdate(f'task'))


@router.delete('/run/var')
def taskDeleteRunVar(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunVar)
    view.deleteRunVar(*input.forDelete(f'task'))
    return ""  # empty result


@router.get('/run/dialog')
@router.renders('partials/run/modal')
def taskRunDialog(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Open a modal dialog to run task with parameters
    return view.runDialog(input.name)


@router.post('/run/dialog')
@router.renders('partials/run/modal')
def taskRunDialogUpdate(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Run the task with the given parameters supplied by the modal dialog
    node = input.selected(view.repo)
    result = view.tryRun(input, node)
    failed = result.get("error") != None

    if failed:
        return result  # Validation failed or runtime invalid

    # Task run has been confirmed, clear the modal and force refresh of main display
    return router.render_template("partials/run/confirm.html", result)


@router.get('/run/breakdown')
@router.renders('partials/run/list')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Do a breakdown of the current task
    result = view.taskBreakdown(input.name)
    return result
