from taskserver.domain.entities.Task import Task
from taskserver.use_cases.task import TaskUseCase


def test_create_task_use_case(task_factory, task_repo):
    task_use_case = TaskUseCase(task_repo=task_repo)
    task_data = task_factory.build()
    task_entity = Task(**task_data.__dict__)
    task = task_use_case.insert(task_entity)
    assert task
    assert task.key == task_data.key
    assert task.name == task_data.name
    assert task.desc == task_data.desc


def test_update_task_use_case(task_factory, task_repo):
    task_use_case = TaskUseCase(task_repo=task_repo)
    task_data = task_factory()
    task_entity = Task(**task_data.__dict__)
    task_entity.name = "Test_1"
    task_entity.desc = "Desc_1"

    task = task_use_case.update(task_entity)
    assert task
    assert task.name == "Test_1"
    assert task.desc == "Desc_1"


def test_get_task_use_case(task_factory, task_repo):
    task_use_case = TaskUseCase(task_repo=task_repo)
    task_data = task_factory()
    task = task_use_case.get_by_name(task_data.name)
    assert task
    assert task.name == task_data.name
    assert task.desc == task_data.desc


def test_list_task_use_case(task_factory, task_repo):
    task_use_case = TaskUseCase(task_repo=task_repo)
    task_factory(name="test1")
    task_factory(name="test2")
    task_factory(name="test3")
    task = task_use_case.list()
    assert task
    assert len(task) == 3


def test_delete_task_use_case(task_factory, task_repo):
    task_use_case = TaskUseCase(task_repo=task_repo)

    task_data = task_factory()
    task_use_case.delete(task_data.name)

    task = task_use_case.get_by_name(task_data.name)
    assert not task