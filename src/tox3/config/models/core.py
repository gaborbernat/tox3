import argparse
from pathlib import Path
from typing import List

from ..project import FileConf, BuildSystem
from ..util import Substitute


class CoreToxConfig(Substitute):

    def __init__(self,
                 options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: FileConf) -> None:
        self._options: argparse.Namespace = options
        self._file: FileConf = file
        self._build_system: BuildSystem = build_system

    @property
    def root_dir(self) -> Path:
        return self._options.__getattribute__('root_dir')

    @property
    def work_dir(self) -> Path:
        return self.root_dir / '.tox3'

    @property
    def build_requires(self) -> List[str]:
        return self._build_system.requires

    @property
    def build_backend_full(self) -> str:
        return self._build_system.backend.replace(':', '.')

    @property
    def build_backend(self) -> str:
        return self._build_system.backend

    @property
    def build_backend_base(self) -> str:
        at = self.build_backend.find(':')
        if at == -1:
            at = len(self.build_backend)
        return self.build_backend[:at]
