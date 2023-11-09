from datetime import datetime
from typing import Callable, List
from taskserver.domain.models.TaskCommand import Command, TaskCommand
from taskserver.domain.models.TaskTracker import TaskTracker


class TaskTimer(TaskTracker):
    root: TaskCommand
    onUpdate: Callable

    def __init__(self, root: TaskCommand, onUpdate=None) -> None:
        super().__init__()
        self.root = root
        self.onUpdate = onUpdate

    def save(self):
        if self.onUpdate:
            self.onUpdate()

    def setOverflow(self, parent: Command, overflow: str): ...

    def cmdStarted(self, stack: List[TaskCommand], cmd_raw: str, up_to_date: bool = None):
        parent: TaskCommand = stack[-1] if len(stack) else None
        cmds = parent.cmds if parent else []

        def active(c: Command):
            return c.value.startswith(cmd_raw) and not c.started

        found = list(filter(active, cmds))
        if cmd := found[0] if len(found) else None:
            cmd.started = datetime.now()
            self.markFinishedUpTo(parent, cmd)
            self.save()

    def taskStarted(self, stack: List[TaskCommand], cmd_name: str, up_to_date: bool = None):
        cmd: Command = None

        def unstarted(c: Command):
            return c.value == cmd_name and not c.started

        # Check for root task starting...
        if not len(stack) and self.root.value == cmd_name:
            #self.root.started = datetime.now()
            stack.append(self.root)
            self.save()
        elif parent := stack[-1] if len(stack) else self.root:
            # Find a matching node in the parent's (unstarted) commands
            found = list(filter(unstarted, parent.cmds))
            if len(found):
                cmd = found[0]
                self.markFinishedUpTo(parent, cmd)

        if cmd:
            cmd.started = datetime.now()
            stack.append(cmd)  # Make this command the active node
            self.save()

    def taskUpToDate(self, stack: List[TaskCommand], cmd: TaskCommand):
        if parent := stack[-1] if len(stack) else None:
            self.markFinishedUpTo(parent, cmd)
        if cmd:
            cmd.up_to_date = True
            cmd.started = datetime.now()
            cmd.finished = cmd.started
            self.closeTask(cmd)

    def taskFinished(self, stack: List[TaskCommand], cmd: TaskCommand):
        parent = stack[-1] if len(stack) else None
        cmd.finished = datetime.now()
        self.markFinishedUpTo(parent, cmd)
        self.closeTask(cmd)

    def taskFailed(self, stack: List[TaskCommand], cmd: TaskCommand, exitCode=1):
        finished = datetime.now()

        # If this is a task command, check last child prcess that was finished
        def mark_last_run_as_failed(parent: Command):
            parent.finished = finished
            parent.exitCode = exitCode

            if isinstance(parent, TaskCommand) and parent.cmds:
                # Find all previous siblings that needs to be closed
                found = list(filter(lambda c: c.started, parent.cmds))
                if active := found[-1] if len(found) else None:
                    mark_last_run_as_failed(active)

        # Set current task exit code
        mark_last_run_as_failed(cmd)

        # Add exitCode all the way up to root
        for parent in stack:
            parent.exitCode = exitCode
        self.closeTask(cmd)

    def markFinishedUpTo(self, parent: TaskCommand, cmd: Command):
        if parent and isinstance(parent, TaskCommand) and parent.cmds and cmd in parent.cmds:
            # Find all previous siblings that needs to be closed

            for index, sibling in enumerate(parent.cmds):
                if sibling.finished:
                    continue  # Already completed
                elif sibling != cmd:
                    # Close sibling preceding the active command
                    if index + 1 < len(parent.cmds):
                        # Use the starting time for the next command as the finish time for this command
                        next = parent.cmds[index + 1]
                        sibling.finished = next.started
                    self.closeTask(sibling)
                else:
                    # Stop updating timestamps, as this is the active node
                    return

    def closeTask(self, cmd: TaskCommand, save=True):
        if not cmd.finished:
            cmd.finished = datetime.now()

        # Finish any open child nodes
        if isinstance(cmd, TaskCommand) and cmd.cmds:
            for i, sub in enumerate(cmd.cmds):
                if i + 1 < len(cmd.cmds):
                    # Use the starting time for the next command as the finish time for this command
                    next = cmd.cmds[i + 1]
                    sub.finished = next.started
                else:
                    # No next command, so just use current timestamp
                    sub.finished = cmd.finished
                self.closeTask(sub, save=False)

        # Close any open and dangling tasks
        if save:
            self.save()
