from taskserver.domain.entities.Task import Task


class TaskBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["desc", "vars", "sources", "generates", ]


class TaskCreateSerializer(TaskBaseSerializer):
    ...


class TaskPutOrPatchSerializer(TaskBaseSerializer):
    ...


class TaskDetailSerializer(TaskBaseSerializer):
    ...


class TaskListSerializer(TaskBaseSerializer):
    class Meta:
        model = Task
        fields = TaskBaseSerializer.Meta.fields + ["id", ]
