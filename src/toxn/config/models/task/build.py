import argparse
from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional, Type, Union, cast

from toxn.config.project import BuildSystem, ConfDict
from .base import TaskConfig


class BuildTaskConfig(TaskConfig):
    NAME: str = 'build'
    _built_package: Optional[Path] = None
    _for_build_requires: Union[Type[ValueError], List[str]] = ValueError

    def __init__(self,
                 _cli: argparse.Namespace,
                 config_dict: ConfDict,
                 project_work_dir: Path,
                 name: str,
                 build_system: BuildSystem,
                 task: SimpleNamespace) -> None:
        super().__init__(_cli, config_dict, project_work_dir, name, task)
        self._build_system: BuildSystem = build_system

    @property
    def build_wheel(self) -> bool:
        return self._config_dict.get('build_wheel', True)

    @property
    def build_type(self) -> str:
        return 'wheel' if self.build_wheel else 'sdist'

    @property
    def build_requires(self) -> List[str]:
        return self._build_system.requires

    @property
    def build_backend_full(self) -> Optional[str]:
        if self._build_system.backend is None:
            return None
        return self._build_system.backend.replace(':', '.')

    @property
    def build_backend(self) -> Optional[str]:
        return self._build_system.backend

    @property
    def build_backend_base(self) -> Optional[str]:
        if self.build_backend is None:
            return None
        at = self.build_backend.find(':')
        if at == -1:
            at = len(self.build_backend)
        return self.build_backend[:at]

    @property
    def skip(self) -> bool:
        return self._config_dict.get('skip', False)

    @property
    def teardown_commands(self) -> List[List[str]]:
        return self._extract_command(self._config_dict.get('tear_down', []))


class BuiltTaskConfig(BuildTaskConfig):

    def __init__(self,
                 base: BuildTaskConfig,
                 for_build_requires: List[str],
                 built_package: Path) -> None:
        self._for_build_requires: List[str] = for_build_requires
        self._built_package: Path = built_package
        super().__init__(base._cli, base._config_dict, base.work_dir, base.name, base._build_system, base.task)

    @property
    def package(self) -> Optional[Path]:
        return self._built_package

    @property
    def for_build_requires(self) -> List[str]:
        return cast(List[str], self._for_build_requires)
