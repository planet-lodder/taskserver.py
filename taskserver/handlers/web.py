
from fastapi import Response
from taskserver.domain.entities.Task import Task
from taskserver.handlers.serializers import TaskCreateSerializer
from taskserver.repo.memory import InMemoryTaskRepository
from taskserver.use_cases.task import TaskUseCase


class TaskAPIView():
    def post(self, request):
        
        task_serializer = TaskCreateSerializer(data=request.data)
        if not task_serializer.is_valid():
            return Response(task_serializer.errors, status=400)
        task_entity = Task(**task_serializer.validated_data)
        task_repo = InMemoryTaskRepository()
        task = TaskUseCase(task_repo).insert(task_entity)
        return Response(task.dict(), status=201)

    def put(self, request, task_id):
        task_repo = InMemoryTaskRepository()
        task = TaskUseCase(task_repo).get_by_id(task_id)
        if not task:
            return Response(
                {"message": "Task with that name does not exist"},
                status=400,
            )
        else:
            task_serializer = TaskCreateSerializer(data=request.data)
            if not task_serializer.is_valid():
                return Response(task_serializer.errors, status=400)
            task_entity = Task(**task_serializer.validated_data)
            task_entity.key = task.key
            task_repo = InMemoryTaskRepository()
            task = TaskUseCase(task_repo).update(task_entity)
            return Response(task.dict(), status=200)

    def get(self, request, task_id=None):
        task_repo = InMemoryTaskRepository()
        if not task_id:
            if tasks := TaskUseCase(task_repo).list():
                tasks_dict = [task.__dict__ for task in tasks]
            else:
                tasks_dict = {}
            return Response(
                {
                    "message": tasks_dict,
                },
                status=200,
            )
        else:
            if task := TaskUseCase(task_repo).get_by_id(task_id):
                return Response(task.dict(), status=200)
            else:
                return Response(
                    {"message": "Task with that name does not exist"},
                    status=400,
                )
