
import json
import os
import re
import time

from ansi2html import Ansi2HTMLConverter
from ansi2html.style import (get_styles)

from taskserver import router, task_server
from taskserver.models.TaskNode import TaskNode
from taskserver.models.TaskfileConfig import taskfile_for
from taskserver.utils import HtmxRequest

root = TaskNode('', 'Task Actions')
root.populate(task_server.list())


def format_output(output):
    if not output:
        return ""

    converter = Ansi2HTMLConverter(linkify=True)
    formatted = converter.prepare(output)

    dark_bg = formatted["dark_bg"]
    all_styles = get_styles(dark_bg)
    backgrounds = all_styles[:5]
    used_styles = filter(
        lambda e: e.klass.lstrip(
            ".") in formatted["styles"], all_styles
    )
    style = "\n".join(
        list(map(str, backgrounds + list(used_styles))))

    body = formatted["body"]
    output = f'<style>{style}</style>\n<pre>{body}</pre>'
    return output


@router.post('/run')
@router.renders('task/run/details')
def taskRun(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)

    # Collect the head and body
    body = req.body or {}
    name = body["name"] if "name" in body else ""
    task = None if not name else root.find(name)

    error = ''
    if not name:
        error = 'Please specify a task name'
    elif not task:
        error = f'Task "{name}" could not be found.'

    result = {
        "title": task.key if task else "unknown",
        "toolbar": "task/toolbar/task.html",        
        "taskfile": taskfile,
        "task": task,
        "name": name,
        "error": error,
    }
    if not error:
        try:
            # Add HEAD and BODY values to ENV vars
            env = os.environ.copy()

            # Execute the task command (given the input HEAD and BODY)
            output = taskfile.run(name, env)
            output = format_output(output)

            # Capture the details to the task that was spawned
            result.update({"output": output})

        except Exception as ex:
            # The task failed to launch
            print(f'Something went wrong: {ex}')
            result.update({"error": str(ex)})

    # Return the modal dialog, and assume validation failed or something went wrong
    return result

@router.get('/run/details')
@router.renders('task/run/details')
def taskRunDialog(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)

    task = root.find(htmx.triggerName)
    name = task.key if task else ""

    # Show the task view
    return {
        "taskfile": taskfile,
        "task": task,
        "name": name,
        "output": "TODO: Add console log output...",
    }

@router.get('/run/dialog')
@router.renders('task/run/modal')
def taskRunDialog(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)

    task = root.find(htmx.triggerName)
    name = task.key if task else ""

    # Show the task view
    return {
        "taskfile": taskfile,
        "task": task,
        "name": name,
    }


@router.post('/run/dialog')
@router.renders('task/run/modal')
def taskRun(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)

    # Collect the head and body
    body = req.body or {}
    name = body["name"] if "name" in body else ""
    task = None if not name else root.find(name)

    error = ''
    if not name:
        error = 'Please specify a task name'
    elif not task:
        error = f'Task "{name}" could not be found.'

    result = {
        "taskfile": taskfile,
        "task": task,
        "name": name,
        "error": error,
    }
    if not error:
        try:
            # Add HEAD and BODY values to ENV vars
            env = os.environ.copy()

            # Execute the task command (given the input HEAD and BODY)
            output = taskfile.run(name, env)
            output = format_output(output)

            # Capture the details to the task that was spawned
            result.update({"output": output})

            # Return the running task to the main content screen
            return router.render_template("task/run/confirm.html", result)

        except Exception as ex:
            # The task failed to launch
            print(f'Something went wrong: {ex}')
            result.update({"error": str(ex)})

    # Return the modal dialog, and assume validation failed or something went wrong
    return result


@router.get('/run/var')
@router.renders('task/run/vars/item')
def taskRunDialog(req, resp):
    taskfile = taskfile_for(req)
    htmx = HtmxRequest(req)

    task = root.find(htmx.triggerName)
    print(f'TASK VARS: {taskfile}')
    key = htmx.prompt
    value = ""

    # Show the task view
    return {
        "taskfile": taskfile,
        "task": task,
        "key": key,
        "value": value,
    }
