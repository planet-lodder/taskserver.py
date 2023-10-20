
import pytest

from pydantic import ValidationError

from taskserver.domain.models.Task import Task, TaskVars


def test_task_vars():
    vars = TaskVars({
        "ALPHA": "aaa",
        "BETA": "bbb",
    })

    # Check that task vars were set correctly
    assert vars
    assert vars.keys() == ["ALPHA", "BETA"]
    assert vars["ALPHA"] == "aaa"
    assert vars["BETA"] == "bbb"


def test_task_create():
    task = Task(
        desc="test description",
        vars={
            "ALPHA": "aaa",
            "BETA": "bbb",
        },
        sources=[
            "requirements.txt"
        ],
        generates=[
            "dist/**"
        ]
    )

    # Check that basic properties on Task is set correctly
    assert task
    assert task.desc == "test description"
    assert task.sources == ["requirements.txt"]
    assert task.generates == ["dist/**"]

    # Check that task vars were set correctly
    assert task.vars
    assert task.vars.keys() == ["ALPHA", "BETA"]
    assert task.vars["ALPHA"] == "aaa"
    assert task.vars["BETA"] == "bbb"
