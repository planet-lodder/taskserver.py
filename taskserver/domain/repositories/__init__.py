
import os

from taskserver.domain.repositories.base import TaskfileRepository
from taskserver.domain.repositories.filesystem import FilesystemTaskfileRepo
from taskserver.domain.repositories.memory import InMemoryTaskRepository


# Keep track of all the loaded taskfiles
LOADED_TASKFILES = {}


class Repository():

    @staticmethod
    def forTaskfile(file: str) -> TaskfileRepository:
        cache = LOADED_TASKFILES
        if file in cache:  # Check for cached result
            return cache[file]

        # Resolve the repository type
        if file.startswith(':memory:'):
            # In-memory taskfile
            filename = file[len(':memory:'):]
            cache[file] = InMemoryTaskRepository(filename)
        elif os.path.isfile(file):
            # Taskfile exists on disk, load it into memory
            cache[file] = FilesystemTaskfileRepo(file)
        else:
            # Fallback, save new taskfile in memory
            cache[file] = InMemoryTaskRepository(file)

        return cache[file]
