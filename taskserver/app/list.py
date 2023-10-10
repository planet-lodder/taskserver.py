from taskserver import router
from taskserver.domain.handlers.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.list import TaskListUseCase


@router.get('/list')
@router.renders("partials/list/index")
def taskList(req, resp):
    store = UseCase.forWeb(req, TaskListUseCase)
    return {
        "taskfile": store.taskfile,
        "list": store.list()
    }


@router.post('/list')
@router.renders("partials/list/index")
def taskSearch(req, resp):
    class WebSearchTerms(WebSerializer):
        def parse(self):
            return self.body["search"] if "search" in self.body else ""

    store = UseCase.forWeb(req, TaskListUseCase)
    input = Serialize.fromWeb(req, WebSearchTerms)
    terms = input.parse()
    return {
        "taskfile": store.taskfile,
        "list": store.filter(terms)
    }
