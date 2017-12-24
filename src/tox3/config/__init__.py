import logging
import re
from collections import namedtuple
from pathlib import Path
from typing import Dict, IO, List, Optional, Union

import toml

from .cli import parse


async def load(argv: List[str]):
    options = parse(argv)
    config = ToxConfig.from_toml(options)
    return config


BuildSystem = namedtuple('BuildSystem', ['requires', 'backend'])


class CoreToxConfig:

    def __init__(self, options, build_system: BuildSystem, _raw):
        self._options = options
        self._raw = _raw
        self._build_system = build_system

    @property
    def root_dir(self):
        return self._options.root_dir

    @property
    def work_dir(self) -> Path:
        return self.root_dir / '.tox3'

    @property
    def build_requires(self):
        return self._build_system.requires

    @property
    def build_backend(self):
        return self._build_system.backend

    @property
    def build_backend_full(self):
        return self._build_system.backend.replace(':', '.')


class ToxConfig(CoreToxConfig):

    @classmethod
    def from_toml(cls, options):
        config_file: Union[Path, IO[str]] = options.config
        logging.debug('load config file %s', config_file)
        file_conf = toml.load(str(config_file) if isinstance(config_file, Path) else config_file)

        options.root_dir = (config_file if isinstance(config_file, Path) else Path(config_file.name)).parents[0]

        build_system = BuildSystem(file_conf['build-system']['requires'],
                                   file_conf['build-system']['build-backend'])
        tox = file_conf['tool']['tox3']
        return cls(options, build_system, tox)

    def __init__(self, options, build_system: BuildSystem, raw):
        super().__init__(options, build_system, raw)

        def _raw_env(env_name):
            base = {k: v for k, v in self._raw['env'].items() if not isinstance(v, dict)}
            if env_name in self._raw['env']:
                base.update(self._raw['env'][env_name])
            return base

        self.build = BuildEnvConfig(options, build_system, _raw_env('_build'), '_build')
        self._envs: Dict[str, RunEnvConfig] = {k: RunEnvConfig(options, build_system, _raw_env(k), k) for k in
                                               self.envs}

    @property
    def envs(self):
        return self._raw['envlist']

    @property
    def run_environments(self):
        return self._options.environments if self._options.environments else self.envs

    def env(self, env_name: str) -> 'RunEnvConfig':
        return self._envs[env_name]


class EnvConfig(CoreToxConfig):
    def __init__(self, root_dir: Path, build_system: BuildSystem, raw, name: str):
        super().__init__(root_dir, build_system, raw)
        self.name = name

    @property
    def python(self):
        key = 'basepython'
        if key in self._raw:
            return self._raw[key]
        match = re.match(r'py(\d)(\d)', self.name)
        if match:
            return 'python{}.{}'.format(match.group(1), match.group(2))
        raise ValueError('no base python for {}'.format(self.name))

    @property
    def recreate(self):
        return self._options.recreate


class RunEnvConfig(EnvConfig):

    @property
    def commands(self):
        return self._raw['commands']

    @property
    def extras(self):
        return self._raw.get('extras', [])

    @property
    def description(self):
        return self._raw.get('description')


class BuildEnvConfig(EnvConfig):
    _built_package: Optional[Path] = None

    @property
    def built_package(self) -> Optional[Path]:
        return self._built_package

    @built_package.setter
    def built_package(self, value: Path):
        self._built_package = value
