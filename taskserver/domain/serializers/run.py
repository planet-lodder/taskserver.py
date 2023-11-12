

from taskserver.domain.serializers.task import TaskRequest
from taskserver.domain.serializers.web import WebSerializer


class TaskRunInputs(TaskRequest):
    job_id: str

    def parse(self):
        # Check if the job key was provided
        self.job_id = self.req.query.get('job_id')

        super().parse()  # Parse task properties


class TaskRunVar(WebSerializer):
    path: str = ''
    task: str = ''
    key: str = ''
    value: str = ''

    def parse(self):
        self.path = self.req.query.get('path', 'Taskfile.yaml')
        self.task = self.req.input('name', self.req.query.get('name', ''))
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
        return self.task, dest, self.key, self.value

    def forDelete(self, dest):
        return self.task, dest, self.key
