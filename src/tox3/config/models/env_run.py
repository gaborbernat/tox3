import shlex
from pathlib import Path
from typing import List, Optional

from tox3.util import list_to_cmd
from .env import EnvConfig


class RunEnvConfig(EnvConfig):

    @property
    def commands(self) -> List[List[str]]:
        commands: List[str] = self._file.get('commands', [])
        result = []
        for command in commands:
            command = self._substitute(command).strip()
            cmd = shlex.split(command)
            if cmd:
                result.append(cmd)
        return result

    @property
    def extras(self) -> List[str]:
        return self._file.get('extras', [])

    @property
    def description(self) -> Optional[str]:
        return self._file.get('description')

    @property
    def deps(self) -> List[str]:
        return self._file.get('deps', [])

    @property
    def install_build_requires(self) -> bool:
        return self._file.get('install_build_requires', False)

    @property
    def install_for_build_requires(self) -> bool:
        return self._file.get('install_for_build_requires', False)

    @property
    def use_develop(self) -> bool:
        return self._file.get('use_develop', False)

    @property
    def posargs(self) -> str:
        args = getattr(self._options, 'args', [])
        return list_to_cmd(args)

    @property
    def change_dir(self) -> Path:
        change_dir = self._file.get('change_dir')
        if change_dir is None:
            return self.root_dir
        return Path(change_dir)
