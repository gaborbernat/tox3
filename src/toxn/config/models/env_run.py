from pathlib import Path
from typing import List, Optional

from toxn.util import list_to_cmd
from .env import EnvConfig


class RunEnvConfig(EnvConfig):

    @property
    def commands(self) -> List[List[str]]:
        return self._extract_command(self._config_dict.get('commands', []))

    @property
    def extras(self) -> List[str]:
        return self._config_dict.get('extras', [])

    @property
    def description(self) -> Optional[str]:
        return self._config_dict.get('description')

    @property
    def deps(self) -> List[str]:
        return self._config_dict.get('deps', [])

    @property
    def install_build_requires(self) -> bool:
        return self._config_dict.get('install_build_requires', False)

    @property
    def install_for_build_requires(self) -> bool:
        return self._config_dict.get('install_for_build_requires', False)

    @property
    def use_develop(self) -> bool:
        return self._config_dict.get('use_develop', False)

    @property
    def posargs(self) -> str:
        args = getattr(self._cli, 'args', [])
        return list_to_cmd(args)

    @property
    def change_dir(self) -> Path:
        change_dir = self._config_dict.get('change_dir')
        if change_dir is None:
            return self.root_dir
        return Path(change_dir)

    @property
    def install_build(self) -> bool:
        return not self._config_dict.get('skip_install', False)
