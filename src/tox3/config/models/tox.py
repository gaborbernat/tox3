import argparse
from pathlib import Path
from typing import Any, Dict, List, cast

from .core import CoreToxConfig
from .env_build import BuildEnvConfig
from .env_run import RunEnvConfig
from ..project import BuildSystem, FileConf


class ToxConfig(CoreToxConfig):

    def __init__(self,
                 options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: FileConf,
                 work_dir: Path) -> None:
        super().__init__(options, build_system, file, work_dir)

        def _is_extra_env(key: str, conf: Any) -> bool:
            return isinstance(conf, dict) and \
                   key not in self.default_run_environments and \
                   key not in {BuildEnvConfig.NAME, 'set_env'}

        self.default_run_environments: List[str] = cast(List[str], self._file.get('envlist', []))
        self.extra_defined_environments: List[str] = [k for k, v in self._file.get('env', {}).items() if
                                                      _is_extra_env(k, v)]
        defined = self.default_run_environments + self.extra_defined_environments

        environments = cast(List[str], getattr(self._options, 'environments', []))
        self.run_environments: List[str] = environments if environments else self.default_run_environments
        self.run_defined_environments = self._run_defined_environments(defined)

        self.environments: List[str] = defined + self.run_defined_environments

        def _raw_env(env_name: str) -> FileConf:
            env = self._file.get('env', {})
            base = {k: v for k, v in env.items() if k in {'set_env', } or not isinstance(v, dict)}
            if env_name in env:
                base.update(env[env_name])
            return base

        self.build = BuildEnvConfig(options,
                                    build_system,
                                    _raw_env(BuildEnvConfig.NAME),
                                    work_dir,
                                    BuildEnvConfig.NAME)
        self._envs: Dict[str, RunEnvConfig] = {k: RunEnvConfig(options,
                                                               build_system,
                                                               _raw_env(k),
                                                               work_dir, k) for k in
                                               self.environments}

    def _run_defined_environments(self, defined: List[str]) -> List[str]:
        # environments that are invoked on demand
        run_defined: List[str] = []
        for env in self.run_environments:
            if env not in defined:
                run_defined.append(env)
        return run_defined

    def env(self, env_name: str) -> RunEnvConfig:
        return self._envs[env_name]

    @property
    def action(self) -> str:
        return cast(str, getattr(self._options, 'action'))
