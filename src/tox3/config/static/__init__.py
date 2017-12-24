""" holds all configuration information - input entries and runtime generated (states)"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional

from tox3.config.static.cli import parse
from tox3.config.static.project import FileConf, BuildSystem


class CoreToxConfig:

    def __init__(self,
                 options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: FileConf) -> None:
        self._options: argparse.Namespace = options
        self._file: FileConf = file
        self._build_system: BuildSystem = build_system

    @property
    def root_dir(self) -> Path:
        return self._options.__getattribute__('root_dir')

    @property
    def work_dir(self) -> Path:
        return self.root_dir / '.tox3'

    @property
    def build_requires(self) -> List[str]:
        return self._build_system.requires

    @property
    def build_backend(self) -> str:
        return self._build_system.backend

    @property
    def build_backend_full(self) -> str:
        return self._build_system.backend.replace(':', '.')


class ToxConfig(CoreToxConfig):

    def __init__(self, options, build_system: BuildSystem, file):
        super().__init__(options, build_system, file)

        def _raw_env(env_name):
            base = {k: v for k, v in self._file['env'].items() if not isinstance(v, dict)}
            if env_name in self._file['env']:
                base.update(self._file['env'][env_name])
            return base

        self.build = BuildEnvConfig(options, build_system, _raw_env('_build'), '_build')
        self._envs: Dict[str, RunEnvConfig] = {k: RunEnvConfig(options, build_system, _raw_env(k), k) for k in
                                               self.envs}

    @property
    def envs(self):
        return self._file['envlist']

    @property
    def run_environments(self):
        environments = self._options.__getattribute__('environments')
        return environments if environments else self.envs

    def env(self, env_name: str) -> 'RunEnvConfig':
        return self._envs[env_name]


class EnvConfig(CoreToxConfig):
    def __init__(self,
                 _options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: Dict,
                 name: str):
        super().__init__(_options, build_system, file)
        self.name = name

    @property
    def python(self) -> str:
        key = 'basepython'
        if key in self._file:
            return self._file[key]
        match = re.match(r'py(\d)(\d)', self.name)
        if match:
            return 'python{}.{}'.format(match.group(1), match.group(2))
        raise ValueError('no base python for {}'.format(self.name))

    @property
    def recreate(self) -> bool:
        return self._options.__getattribute__('recreate')


class BuildEnvConfig(EnvConfig):
    pass


class RunEnvConfig(EnvConfig):

    @property
    def commands(self) -> List[str]:
        return self._file['commands']

    @property
    def extras(self) -> List[str]:
        return self._file.get('extras', [])

    @property
    def description(self) -> Optional[str]:
        return self._file.get('description')
