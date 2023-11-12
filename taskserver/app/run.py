

from anyserver import WebRequest, WebResponse

from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.serializers.run import TaskRunInputs, TaskRunVar
from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.run import TaskRunUseCase


@router.get('/run')
@router.renders('task/single')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    node = input.selected(view.repo)
    result = view.runIndex(input, node, input.job_id)

    return result


@router.post('/run')
@router.renders('task/single')
def taskRun(req: WebRequest, resp: WebResponse):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    node = input.selected(view.repo)
    vars = req.inputs('config.task.', strip_prefix=True)
    result = view.tryRun(input, node, vars)

    if run := result.get("run"):
        new_url = f'{req.path}?job_id={run.id}'
        resp.head['HX-Replace-Url'] = new_url
    return result


@router.get('/run/toolbar')
@router.renders("partials/toolbar/command")
def taskUpdateRunVar(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    return view.runToolbar(input.name, input.job_id)


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


@router.get('/run/status')
@router.renders('partials/run/status')
def taskStatus(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Trigger update event when status is loaded
    #resp.head['hx-trigger'] = input.name

    # Try and run the task (no additional parameters)
    return view.runStatus(input.job_id)


@router.post('/run/stop')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    return view.stopJob(input.job_id)


@router.get('/run/breakdown')
@router.renders('partials/run/breakdown')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    state = req.query.get('state')

    # Do a breakdown of the current task
    result = view.getRunBreakdown(input.name, input.job_id, state)
    return result


@router.get('/run/breakdown/toggle')
@router.renders('partials/run/breakdown/item')
def taskBreakdown(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    index = req.query.get('index', '')
    state = req.query.get('state', 'closed') == 'open'

    # Do a breakdown of the current task
    result = view.toggleRunBreakdown(input.name, input.job_id, index, state)
    return result


@router.get('/run/output')
@router.renders('partials/terminal/window')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)

    # Try and run the task (no additional parameters)
    result = view.runOutput(input.job_id)

    return result
