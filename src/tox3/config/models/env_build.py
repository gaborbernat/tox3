from pathlib import Path
from typing import List, Optional

from .env import EnvConfig


class BuildEnvConfig(EnvConfig):
    NAME: str = '_build'
    _built_package: Optional[Path] = None
    _for_build_requires: List[str] = []

    @property
    def built_package(self) -> Optional[Path]:
        return self._built_package

    @built_package.setter
    def built_package(self, value: Path) -> None:
        self._built_package = value

    @property
    def for_build_requires(self) -> List[str]:
        return self._for_build_requires

    @for_build_requires.setter
    def for_build_requires(self, value: List[str]) -> None:
        self._for_build_requires = value

    @property
    def build_wheel(self) -> bool:
        return self._file.get('build_wheel', True)

    @property
    def build_type(self) -> str:
        return 'wheel' if self.build_wheel else 'sdist'

    @property
    def build_requires(self) -> List[str]:
        return self._build_system.requires

    @property
    def build_backend_full(self) -> str:
        return self._build_system.backend.replace(':', '.')

    @property
    def build_backend(self) -> Optional[str]:
        return self._build_system.backend

    @property
    def build_backend_base(self) -> str:
        at = self.build_backend.find(':')
        if at == -1:
            at = len(self.build_backend)
        return self.build_backend[:at]
