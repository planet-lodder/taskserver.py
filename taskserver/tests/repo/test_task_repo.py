import pytest

from taskserver.domain.entities import Task


def test_task_repository_insert(task_factory, task_repo):
    task_data = task_factory.build()
    task_entity = Task(**task_data.__dict__)
    task_repo.insert(task_entity)
    task_obj = task_repo.get_by_name(task_entity.name)
    assert task_obj.name == task_entity.name


def test_task_repository_get_by_name(task_factory, task_repo):
    task_data = task_factory()
    task = task_repo.get_by_name(task_data.name)
    assert task
    assert task.key == task_data.key
    assert task.name == task_data.name


def test_task_repository_update(task_factory, task_repo):
    task_data = task_factory()
    assert task_data.name != "Test_1"
    assert task_data.desc != "Desc_1"

    task_entity = Task(**task_data.__dict__)
    task_entity.name = "Test_1"
    task_entity.desc = "Desc_1"

    task = task_repo.update(task_entity)
    assert task
    assert task.key == task_entity.key
    assert task.name == "Test_1"
    assert task.desc == "Desc_1"
    assert task_entity.name == "Test_1"
    assert task_entity.desc == "Desc_1"

def test_task_repository_delete(task_factory, task_repo):
    task_data = task_factory()
    task_repo.delete(task_data.name)
    task = task_repo.get_by_name(task_data.name)
    assert not task


def test_task_repository_list(task_factory, task_repo):
    task_factory(name="test1")
    task_factory(name="test2")
    task_factory(name="test3")

    tasks = task_repo.list()
    assert tasks
    assert len(tasks) == 3