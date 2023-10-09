# Taskfile Server

This project was heavily inspired and built on top of by [Taskfile](https://taskfile.dev/).

## Motivation

This project implements a web server and user interface for working with [Taskfile's](https://taskfile.dev/). 

Taskfile works well for automating all kinds of tasks. Some features include:

- It's declared in a simple, machine-readable file format (YAML).
- It subbports (file) `includes` making it composable / extensible.
- Task varibales make it easy to define defaults and overrides
- Internal task caching and run metadata make it extremely efficient
- Good support for debugging and dry-run of tasks (with execution plan)

As your taskfile's become larger, and more complicated, it bacomes harder to manage and understand. Having an overview and way to navigate this is what the project aims to do.

Native support for installing tasks, from lets say a github repo, is also not available.

## Architecture

 - [Clean Architecture in Python](https://medium.com/@surajit.das0320/understanding-clean-architecture-in-python-deep-dive-on-the-code-17141dc5761a)
 - Python + FastAPI / Anyserver
 - AlpineJS + HTMX for frontend interactivity
 - Tailwind for styling and responsive layouts
