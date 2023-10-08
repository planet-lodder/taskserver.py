#!/usr/bin/env python3
from anyserver import AnyServer

from taskserver.task import router as TASK_ROUTES

app = AnyServer()

def main():
    # app.config.reloads = "main:app.app"
    app.register(TASK_ROUTES)
    app.static("./public")
    app.start()


if __name__ == '__main__':
    main()
