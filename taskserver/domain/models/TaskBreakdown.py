import re

from pydantic import BaseModel

from taskserver.domain.models.Taskfile import Taskfile


class TaskBreakdown(BaseModel):

    @staticmethod
    def forTask(filename, task_name):
        output, _, _ = Taskfile.run(filename, f"{task_name} --summary")

        # Strip everything up to the commands
        output = re.sub(r'(?is).*commands:', '', output, flags=re.MULTILINE)
        commands = []
        type = 'cmd'
        while output:
            match = re.search(r'( - )(Task: )?', output, re.MULTILINE)

            if not match and output:
                # Assume this is a single command
                commands.append({
                    "type": type,
                    "message": output,
                })
                output = ''
            else:
                # Detected the start of a new command
                groups = match.groups()
                start = match.start()
                end = match.end()

                # If there is commands in the buffer, add as the (prev) command
                buffer = output[:start].strip()
                if buffer:
                    commands.append({
                        "type": type,
                        "message": buffer,
                    })

                # Check if this has a task prefix
                type = 'cmd'
                if len(groups) > 1 and 'Task: ' in groups:
                    type = 'task'

                # Find next item entry
                output = output[end:]

        return commands
