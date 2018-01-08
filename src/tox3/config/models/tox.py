from typing import Dict

from .core import CoreToxConfig
from .env_build import BuildEnvConfig
from .env_run import RunEnvConfig
from ..project import BuildSystem


class ToxConfig(CoreToxConfig):

    def __init__(self, options, build_system: BuildSystem, file):
        super().__init__(options, build_system, file)

        def _raw_env(env_name):
            base = {k: v for k, v in self._file['env'].items() if not isinstance(v, dict)}
            if env_name in self._file['env']:
                base.update(self._file['env'][env_name])
            return base

        self.build = BuildEnvConfig(options, build_system, _raw_env(BuildEnvConfig.NAME), BuildEnvConfig.NAME)
        self._envs: Dict[str, RunEnvConfig] = {k: RunEnvConfig(options, build_system, _raw_env(k), k) for k in
                                               self.envs}

    @property
    def envs(self):
        return self._file['envlist']

    @property
    def run_environments(self):
        environments = self._options.__getattribute__('environments')
        return environments if environments else self.envs

    def env(self, env_name: str) -> RunEnvConfig:
        return self._envs[env_name]
