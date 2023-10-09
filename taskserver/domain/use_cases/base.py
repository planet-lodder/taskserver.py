from abc import ABC, abstractmethod

from taskserver.domain.entities.Task import Task


class AbstractTaskUseCase(ABC):
    
    @abstractmethod
    def get_by_name(self, task_name):
        ...

    @abstractmethod
    def insert(self, task: Task):
        ...

    @abstractmethod
    def update(self, task: Task):
        ...

    @abstractmethod
    def delete(self, task_name):
        ...

    @abstractmethod
    def list(self):
        ...
