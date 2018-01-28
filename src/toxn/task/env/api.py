from abc import abstractmethod
from typing import List


class TaskEnv:

    @abstractmethod
    def __init__(self):
        """create the environment"""

    @abstractmethod
    def add_dependencies(self, deps: List[str]):
        """add dependencies"""

    @abstractmethod
    def run(self, cmd):
        """"""
