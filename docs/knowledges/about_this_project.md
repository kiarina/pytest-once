---
title: About this project
description: >-
  Information about the pytest-once project.
---

## Why

When running tests in parallel with `pytest-xdist`, there's a frequent need to **execute setup procedures only once**. For example:

- Starting Docker containers
- Initializing test databases
- Starting mock external services
- Heavy initialization processes (taking several seconds to tens of seconds)

Normal `pytest` fixtures run independently in each worker process, so even with `scope="session"`, **setup runs as many times as there are workers**. This causes:

- ⚠️ Resource waste (e.g., starting multiple identical containers)
- ⚠️ Runtime errors such as port conflicts
- ⚠️ Increased test execution time

`pytest-once` uses **file lock-based inter-process synchronization** to achieve truly "once-only" setup even in xdist environments. It provides a simple API that can transform existing fixtures with a single decorator.

## Design Philosophy

- **Setup-only**: No teardown support for simplicity and reliability
- **Idempotent setup**: Encourage cleanup within setup for safe re-runs
- **External cleanup**: Rely on CI environment destruction or external tools (docker-compose, etc.)
- **Simple API**: Just one decorator with minimal parameters

## Tech Stack

- language: Python 3.12+
- runtime management: mise
- dependency / environment management: uv
- code formatting: ruff
- linting: ruff
- typecheck: mypy
- testing: pytest
- task runner: mise (File Tasks)
