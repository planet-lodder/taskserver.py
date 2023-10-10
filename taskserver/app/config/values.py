from taskserver import router
from taskserver.domain.handlers.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase
from taskserver.utils import HtmxRequest


class ConfigValueInput(WebSerializer):
    def parse(self): return None

    def forUpdate(self, dest):
        htmx = HtmxRequest(self.req)

        # Resolve key for value that changed
        key = htmx.prompt or ""
        if not key and htmx.triggerName:
            key = htmx.triggerName[len(f'config.{dest}.'):]

        # Get the key value
        value = "" if not key else htmx.input(f'config.{dest}.{key}') or ""

        # Return relevant information
        return dest, key, value

    def forDelete(self, dest):
        htmx = HtmxRequest(self.req)
        key = htmx.triggerName
        return dest, key


@router.post('/config/env')
@router.renders("partials/values/item")
def taskEditConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    return view.updateValue(*input.forUpdate("env"))


@router.delete('/config/env')
def taskRemoveConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    view.removeValue(*input.forDelete("env"))
    return ""  # empty result


@router.post('/config/vars')
@router.renders("partials/values/item")
def taskAddConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    return view.updateValue(*input.forTarget("vars"))


@router.delete('/config/vars')
def taskRemoveConfigVars(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    view.removeValue(*input.forDelete("vars"))
    return ""  # empty result
