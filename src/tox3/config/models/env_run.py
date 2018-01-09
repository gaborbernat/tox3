from typing import List, Optional, cast

from .env import EnvConfig


class RunEnvConfig(EnvConfig):

    @property
    def commands(self) -> List[str]:
        return cast(List[str], self._file['commands'])

    @property
    def extras(self) -> List[str]:
        return self._file.get('extras', [])

    @property
    def description(self) -> Optional[str]:
        return self._file.get('description')

    @property
    def deps(self) -> List[str]:
        return self._file.get('deps', [])
