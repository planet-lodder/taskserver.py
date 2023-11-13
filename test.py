#!/usr/bin/env python3
import yaml

from taskserver.domain.models.Task import TaskBase
from taskserver.domain.models.Taskfile import Taskfile

def load_task():
    path = './taskserver/tests/models/Task.yaml'
    with open(path, "r") as stream:
        raw = yaml.safe_load(stream)
        res = TaskBase(**raw)
        print(yaml.dump(res.dict()))

def load_taskfile():
    taskfile = Taskfile.load('Taskfile.yaml')
    print(f' - Taskfile: {taskfile}')
    print(yaml.dump(taskfile.dict()))

def test():
    #load_task()
    load_taskfile()


if __name__ == '__main__':
    test()
