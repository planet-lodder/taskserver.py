

from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.run import TaskRunUseCase
from taskserver.utils import HtmxRequest

class TaskRunInputs(WebSerializer):
    _task = None

    @property
    def name(self):
        return self.body("name", "")

    @property
    def trigger(self):
        return HtmxRequest(self.req).triggerName

    @property
    def prompt(self):
        return HtmxRequest(self.req).prompt

    def task(self, root):
        if not self._task:
            self._task = root.find(self.name)
        return self._task

    def parse(self):
        if not self.name:
            error = 'Please specify a task name'
            self.errors.append(error)
        elif not self._task:
            error = f'Task "{self.name}" could not be found.'
            self.errors.append(error)
        return self._task


@router.post('/run')
@router.renders('task/single')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    task = input.task(view.root)
    result = view.tryRun(input, task)
    return result


@router.get('/run/dialog')
@router.renders('partials/run/modal')
def taskRunDialog(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    result = view.runDialog(input.trigger)
    return result


@router.post('/run/dialog')
@router.renders('partials/run/modal')
def taskRun(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    task = input.task(view.root)
    result = view.tryRun(input, task)
    failed = "error" in result and result["error"]
    return result if failed else router.render_template("partials/run/confirm.html", result)


@router.get('/run/var')
@router.renders('partials/run/vars/item')
def taskRunDialog(req, resp):
    view = UseCase.forWeb(req, TaskRunUseCase)
    input = Serialize.fromWeb(req, TaskRunInputs)
    return view.runVarDetails(input.trigger, input.prompt)
