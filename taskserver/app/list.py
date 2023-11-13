from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.list import TaskListUseCase


class WebSearchTerms(WebSerializer):
    terms = ''

    def parse(self):
        self.terms = self.req.input("search", "")


@router.get('/list')
@router.renders("partials/list/index")
def taskList(req, resp):
    view = UseCase.forWeb(req, TaskListUseCase)
    return view.list()


@router.post('/list')
@router.renders("partials/list/index")
def taskSearch(req, resp):
    view = UseCase.forWeb(req, TaskListUseCase)
    input = Serialize.fromWeb(req, WebSearchTerms)
    return view.search(input.terms)
