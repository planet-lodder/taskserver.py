from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase


class ConfigValueInput(WebSerializer):
    path: str = ''
    key: str = ''
    value: str = ''

    def parse(self):
        self.path = self.req.query.get('path', 'Taskfile.yaml')
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
        return dest, self.key, self.value

    def forDelete(self, dest):
        return dest, self.key


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
    view.deleteValue(*input.forDelete("env"))
    return ""  # empty result


@router.post('/config/vars')
@router.renders("partials/values/item")
def taskAddConfigEnv(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    return view.updateValue(*input.forUpdate("vars"))


@router.delete('/config/vars')
def taskRemoveConfigVars(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigValueInput)
    view.deleteValue(*input.forDelete("vars"))
    return ""  # empty result
