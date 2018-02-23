"""A task environment that is:
- created:
-- via venv on Python 3
-- virtualenv on Python 2
- and installs dependencies via pip"""
from typing import List

from toxn.task.env.api import TaskEnv


class VenvPip(TaskEnv):
    def __init__(self) -> None:
        super().__init__()

    def add_dependencies(self, deps: List[str]) -> None:
        pass

    def run(self, cmd: List[str]) -> None:
        pass
