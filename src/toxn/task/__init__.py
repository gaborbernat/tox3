"""

toxn run tasks in order of their dependency graph
- every task has one and exactly one environment attached to it
- the environment has:
    - a Python interpreter attached to it,
    - a set of dependencies:
        - optionally the build package
        - optionally the for build required packages
        - defines within the tox file (either directly expressed, or via a requirement file)
        - dependencies of the package
    - whenever the Python interpreter or the dependencies change in a non extending way we recreated the env
    - commands:
        - setup
        - core
        - teardown

The build task is reserved. This one builds the project, and when present will be installed (and ran) for tasks.

"""
from .build import build
from .run import run_task
