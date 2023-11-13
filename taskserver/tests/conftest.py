import pytest

from pytest_factoryboy import register
from factories import TaskFactory
from taskserver.repo.memory import InMemoryTaskRepository

register(TaskFactory, name="task_factory")


@pytest.fixture
def task_repo():
    return InMemoryTaskRepository()
