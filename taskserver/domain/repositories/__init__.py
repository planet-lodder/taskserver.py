
# Keep track of all the loaded taskfiles
from taskserver.domain.repositories.base import TaskfileRepository
from taskserver.domain.repositories.memory import InMemoryTaskRepository


LOADED_TASKFILES = {}


class Repository():

    @staticmethod
    def forTaskfile(file: str) -> TaskfileRepository:
        cache = LOADED_TASKFILES
        if not file in cache:
            # TODO: Load filesystem repo if file exists
            cache[file] = InMemoryTaskRepository(file)
        return cache[file]
