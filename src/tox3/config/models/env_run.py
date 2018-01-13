import shlex
from typing import List, Optional

from tox3.util import list_to_cmd

from .env import EnvConfig


class RunEnvConfig(EnvConfig):

    @property
    def commands(self) -> List[str]:
        commands: List[str] = self._file.get('commands', [])
        result = []
        for command in commands:
            command = self._substitute(command).strip()
            cmd = list_to_cmd(shlex.split(command))
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
    def usedevelop(self) -> bool:
        return self._file.get('usedevelop', False)

    @property
    def posargs(self) -> str:
        args = getattr(self._options, 'args', [])
        return list_to_cmd(args)
