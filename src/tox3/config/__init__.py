import logging
from pathlib import Path
from typing import IO, List, Optional, Union

import toml

from .cli import parse


async def load(argv: List[str]):
    options = parse(argv)
    config = Config(options)
    logging.debug('load config file %r', config)
    return config


class Config:
    def __init__(self, options):
        config_file: Union[Path, IO[str]] = options.config
        self.root_dir = (config_file if isinstance(config_file, Path) else Path(config_file.name)).parents[0]

        logging.debug('load config file %s', config_file)
        file_conf = toml.load(str(config_file) if isinstance(config_file, Path) else config_file)

        self.build_requires: List[str] = file_conf['build-system']['requires']
        self.build_backend: str = file_conf['build-system']['build-backend'].replace(':', '.')
        self._built_package: Optional[Path] = None

        self._raw = file_conf['tool']['tox3']

    @property
    def envs(self):
        return self._raw['envlist']

    def env(self, env_name):
        base = {k: v for k, v in self._raw['env'].items() if not isinstance(v, dict)}
        if env_name in self._raw['env']:
            base.update(self._raw['env'][env_name])
        return base

    @property
    def work_dir(self) -> Path:
        return self.root_dir / '.tox3'

    @property
    def built_package(self) -> Optional[Path]:
        return self._built_package

    @built_package.setter
    def built_package(self, value: Path):
        self._built_package = value

    def __repr__(self):
        args = {'envs': self.envs,
                'root_dir': self.root_dir,
                'work_dir': self.work_dir}
        for env in self.envs:
            args[env] = repr(self.env(env))
        msg = ",\n".join("{}={!r}".format(k, v) for k, v in args.items())
        return f'{self.__class__}({msg})'
