---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the bug
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:

```python
# Minimal reproducible example
from pytest_once import once_fixture

@once_fixture(autouse=True, scope="session")
def my_fixture():
    # Your code here
    pass
```

## Expected behavior
A clear and concise description of what you expected to happen.

## Actual behavior
What actually happened.

## Environment
- pytest-once version: [e.g., 0.1.0]
- Python version: [e.g., 3.12.0]
- pytest version: [e.g., 8.4.0]
- pytest-xdist version (if applicable): [e.g., 3.8.0]
- OS: [e.g., Ubuntu 22.04, macOS 14.0, Windows 11]

## Additional context
Add any other context about the problem here.

## Logs/Output
```
Paste relevant logs or error messages here
```
