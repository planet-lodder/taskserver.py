#!/usr/bin/env python3
from anyserver import AnyServer

from backend.api.status import router as STATUS_ROUTES
from backend.task import router as TASK_ROUTES

app = AnyServer()
# app.config.reloads = "main:app.app"
app.static("./public")
app.register(STATUS_ROUTES)
app.register(TASK_ROUTES)


def main():
    app.start()


if __name__ == '__main__':
    main()
