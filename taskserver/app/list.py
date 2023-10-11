from taskserver import router
from taskserver.domain.serializers import Serialize, WebSerializer
from taskserver.domain.use_cases.base import UseCase
from taskserver.domain.use_cases.list import TaskListUseCase


class WebSearchTerms(WebSerializer):
    def parse(self): return self.body("search", "")


@router.get('/list')
@router.renders("partials/list/index")
def taskList(req, resp):
    view = UseCase.forWeb(req, TaskListUseCase)
    return view.list()


@router.post('/list')
@router.renders("partials/list/index")
def taskSearch(req, resp):
    view = UseCase.forWeb(req, TaskListUseCase)
    terms = Serialize.fromWeb(req, WebSearchTerms).parse()
    return view.search(terms)
