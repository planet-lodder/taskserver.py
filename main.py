#!/usr/bin/env python3
from anyserver import AnyServer
from taskserver import router as TASK_ROUTES

app = AnyServer(prefers='FastAPI')
app.register(TASK_ROUTES)
app.static("./static")


def main():
    app.start()


if __name__ == '__main__':
    main()
