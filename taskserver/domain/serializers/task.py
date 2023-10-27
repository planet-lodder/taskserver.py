from taskserver.domain.models.TaskNode import TaskNode
from taskserver.domain.serializers.web import WebSerializer
from taskserver.domain.repositories.base import TaskfileRepository


class TaskRequest(WebSerializer):
    name = None
    file = None

    def parse(self):
        self.file = self.req.query.get('file', 'Taskfile.yaml')
        self.name = self.req.query.get('name') # from GET
        self.name = self.name or self.req.input('name') # from POST
        
        if not self.name:
            self.errors.append('Task name required')

    def selected(self, repo: TaskfileRepository) -> TaskNode:
        return repo.getMenu(self.name)
