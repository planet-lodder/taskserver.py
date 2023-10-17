from taskserver.models.TaskNode import TaskNode
from taskserver.domain.serializers.web import WebSerializer
from taskserver.domain.repositories.base import ATaskfileRepository


class TaskRequest(WebSerializer):
    name = None
    file = None

    def parse(self):
        self.name = self.req.query.get('name') # from GET
        self.name = self.name or self.req.input('name') # from POST

        self.file = self.req.query.get('file', 'Taskfile.yaml')

    def selected(self, repo: ATaskfileRepository) -> TaskNode:
        return repo.nodes.find(self.name)
