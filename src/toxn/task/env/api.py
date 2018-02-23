from abc import abstractmethod
from typing import List


class TaskEnv:

    @abstractmethod
    def __init__(self) -> None:
        """create the environment"""

    @abstractmethod
    def add_dependencies(self, deps: List[str]) -> None:
        """add dependencies"""

    @abstractmethod
    def run(self, cmd: List[str]) -> None:
        """"""
