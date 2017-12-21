from pathlib import Path
from typing import Union, IO

import toml


class Config:
    def __init__(self, config: Union[Path, IO[str]]):
        self.root_dir = (config if isinstance(config, Path) else Path(config.name)).parents[0]
        if isinstance(config, Path):
            config = str(config)

        _toml = toml.load(config)
        self.build_requires = _toml['build-system']['requires']
        self.build_backend = _toml['build-system']['build-backend']

        self._raw = _toml['tool']['tox3']

    @property
    def envs(self):
        return self._raw['envlist']

    def env(self, env_name):
        base = {k: v for k, v in self._raw['env'].items() if not isinstance(v, dict)}
        if env_name in self._raw['env']:
            base.update(self._raw['env'][env_name])
        return base

    @property
    def workdir(self) -> Path:
        return self.root_dir / '.tox3'


def load_config(config: Union[Path, IO[str]]) -> Config:
    return Config(config)
