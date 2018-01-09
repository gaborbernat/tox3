from pathlib import Path
from typing import Optional, List

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

