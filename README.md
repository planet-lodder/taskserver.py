> This project is heavily inspired by [Taskfile.dev](https://taskfile.dev/), and built on top of it's functionality. 


<p align="center" style="padding-top:20px">
 <img width="100px" src="static/img/logo.svg" align="center" alt="GitHub Readme Stats" />
 <h1 align="center">Taskfile Server</h1>
 <p align="center">Taskfile Server is a web application, to run and manage Taskfile automations.</p>
</p>
  <p align="center">    
    <a href="https://gohugo.io/">
      <img src="https://img.shields.io/badge/Python%20-3.10+%20-gray.svg?colorA=c9177e&colorB=FF4088&style=for-the-badge"/>
    </a>
    <a href="https://tailwindcss.com/">
      <img src="https://img.shields.io/badge/TailwindCSS%20-V3-gray.svg?colorA=0284c7&colorB=38bdf8&style=for-the-badge"/>
    </a>
    <a href="https://alpinejs.dev/">
      <img src="https://img.shields.io/badge/Alpine.js%20-V3-gray.svg?colorA=68a5af&colorB=77c1d2&style=for-the-badge"/>
    </a>
  </p>

  <p align="center">
    <a href="https://www.club404.io">View Demo</a>
    ·
    <a href="https://github.com/Club404/website/issues">Report Bug</a>
  </p>
</p>

This project gives the ability to run and manage `task`'s from any given host or cloud environment.

## Features

Features include:
 - a user interface
 - configurable taskfiles
 - spawning and managing tasks
 - modify task vars before run
 - show execution path (with full drill down)

Features that are not included (yet):
 - Authentication and Authorization of users (eg: local only)
 - Multitenancy and user based run contexts, permissions
 - Security hardening and Threat Analysis report(s)
 
## Previews and dark mode support

We support both light and dark mode (auto detects from browser settings):

![Light Mode](./static/img/sample-light.png)
![Dark Mode](./static/img/sample-dark.png)


## Motivation

Taskfile works well for automating all kinds of tasks. Some features include:

- It's declared in a simple, machine-readable file format (YAML).
- Task varibales make it easy to define defaults and overrides.
- It subbports `includes` making it composable / extensible.
- Task caching and run metadata make it efficient and fast.
- Good support for debugging, dry-run of tasks (with execution plans).

As your taskfile's become larger and more complicated, it becomes harder to manage and understand. 

We try to tackle this problem by giving more advanced tooling around managing these task automations from a web interface, with the ability to track execution steps in near real time.

