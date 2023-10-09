
from fastapi import Response
from taskserver.domain.entities.Task import Task
from taskserver.handlers.serializers import TaskBaseSerializer, TaskCreateSerializer, TaskPutOrPatchSerializer
from taskserver.repo.memory import InMemoryTaskRepository
from taskserver.use_cases.task import TaskUseCase


class Serializer():
    def __init__(self, serializer: TaskBaseSerializer):
        self.serializer = serializer

    @property
    def valid(self):
        return self.serializer.is_valid()

    @property
    def data(self):
        return self.serializer.validated_data

    @property
    def errors(self):
        return self.serializer.errors

    def entity(self, required=False):
        if not required or self.required():
            return Task(**self.data) if self.valid else None

    def required(self):
        if not self.valid:
            # return Response(input.errors, status=400)
            raise Exception('Input validation failed.')
        return self

    @staticmethod
    def TaskCreate(request):
        return Serializer(TaskCreateSerializer(data=request.data))

    @staticmethod
    def TaskUpdate(request):
        return Serializer(TaskPutOrPatchSerializer(data=request.data))


class TaskStore():
    repo = InMemoryTaskRepository()

    @staticmethod
    def Current():
        return TaskUseCase(TaskStore.repo)


class TaskAPI():

    def post(self, request):
        store = TaskStore.Current()
        task = Serializer.TaskCreate(request).entity(required=True)

        # Validated task input received
        task = store.insert(task)

        return Response(task.dict(), status=201)

    def put(self, request, task_id):
        store = TaskStore.Current()
        task = Serializer.TaskUpdate(request).entity(required=True)

        # Validated input, check for existing entry
        found = store.get_by_name(task_id)
        if not found:
            errors = {"message": "Task with that name does not exist"}
            return Response(errors, status=400)

        # Valid task was found
        task.key = found.key
        task = store.update(task)

        return Response(task.dict(), status=200)

    def get(self, request, task_id=None):
        store = TaskStore.Current()

        if not task_id:
            # List all tasks
            list = []
            if tasks := store.list():
                list = [task.__dict__ for task in tasks]
            return Response(list, status=200)
        else:
            # Show the task by ID, or error message
            if task := store.get_by_name(task_id):
                return Response(task.dict(), status=200)

            # Not found
            error = {"message": "Task with that name does not exist"}
            return Response(error, status=400)
