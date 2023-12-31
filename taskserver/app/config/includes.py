from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.config import TaskConfigUseCase


class ConfigIncludeInputs(WebSerializer):
    path: str = None
    id: str = ''
    key: str = ''
    value: str = ''
    renamed: str = ''
    action: str = ''

    def parse(self):
        # Extract the relevant inputs from the request
        self.path = self.req.query.get('path', 'Taskfile.yaml')
        self.id = self.req.query.get('id', '')
        self.key = self.req.input('key', self.id)
        self.value = self.req.input('value')
        self.action = self.req.input('action')

        # Get action from the GET query params (if defined)
        if not self.action and 'action' in self.req.query:
            self.action = self.req.query['action']

        # Look for request originating from HTMX interactions (if HTMX request)
        if not self.key and self.htmx:
            if requested_key := self.htmx.prompt:
                self.key = requested_key  # User entered new key name from prompt


@router.get('/config/includes')
@router.renders("partials/config/includes/items/default")
def taskInclude(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    if input.action == 'close' and input.key.startswith('_new'):
        return ""  # Canceling a new (unsaved) entity, return empty
    return view.getInclude(input.key, input.value)


@router.put('/config/includes')
@router.renders("partials/config/includes/items/edit")
def taskIncludeAdd(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    return view.newInclude(input.key, input.value)


@router.post('/config/includes')
@router.renders("partials/config/includes/items/edit")
def taskIncludeEdit(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)

    # If the edit action was triggered, we fetch the current value to display
    if input.action == "edit" and input.key and not input.value:
        includes = view.repo.getConfigEdits().includes or {}
        input.value = includes.get(input.key)

    # Validate input and create data context object
    result = view.updateInclude(
        input.id, 
        input.key, 
        input.value, 
        action=input.action
    )
    errors = result.get("errors", [])

    # Respond with different content according to action and if input was validated
    if len(errors) or input.action in ["edit", "add"]:
        # Keep in edit mode if not validated
        return result

    # Value has been updated successfully, show the default view and close edit mode
    return router.render_template("partials/config/includes/items/default.html", result)


@router.delete('/config/includes')
def taskIncludeDelete(req, resp):
    view = UseCase.forWeb(req, TaskConfigUseCase)
    input = Serialize.fromWeb(req, ConfigIncludeInputs)
    view.deleteInclude(input.key)
    return ""  # empty result
