import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from .core import CommonToxConfig
from .env_build import BuildEnvConfig
from .env_run import RunEnvConfig
from ..project import BuildSystem, ConfDict


class ToxConfig(CommonToxConfig):

    def __init__(self,
                 options: argparse.Namespace,
                 build_system: BuildSystem,
                 config_dict: ConfDict,
                 config_path: Optional[Path],
                 work_dir: Path) -> None:
        self._work_dir: Path = work_dir
        self.config_path: Optional[Path] = config_path
        self._build_system: BuildSystem = build_system
        super().__init__(options, config_dict)

        def _is_extra_env(key: str, conf: Any) -> bool:
            return isinstance(conf, dict) and \
                   key not in self.default_run_environments and \
                   key not in {BuildEnvConfig.NAME, 'set_env'}

        self.default_run_environments: List[str] = cast(List[str], self._config_dict.get('envlist', []))
        self.extra_defined_environments: List[str] = [k for k, v in self._config_dict.get('env', {}).items() if
                                                      _is_extra_env(k, v)]
        defined = self.default_run_environments + self.extra_defined_environments

        environments = cast(List[str], getattr(self._cli, 'environments', []))
        self.run_environments: List[str] = environments if environments else self.default_run_environments
        self.run_defined_environments = self._run_defined_environments(defined)

        self.environments: List[str] = defined + self.run_defined_environments

        def _raw_env(env_name: str) -> ConfDict:
            env = self._config_dict.get('env', {})
            base = {k: v for k, v in env.items() if k in {'set_env', } or not isinstance(v, dict)}
            if env_name in env:
                base.update(env[env_name])
            return base

        self.build = BuildEnvConfig(options,
                                    _raw_env(BuildEnvConfig.NAME),
                                    work_dir,
                                    BuildEnvConfig.NAME,
                                    build_system)
        self._envs: Dict[str, RunEnvConfig] = {k: RunEnvConfig(options,
                                                               _raw_env(k),
                                                               work_dir, k) for k in self.environments}

    def _run_defined_environments(self, defined: List[str]) -> List[str]:
        # environments that are invoked on demand
        run_defined: List[str] = []
        for env in self.run_environments:
            if env not in defined:
                run_defined.append(env)
        return run_defined

    def _env(self, env_name: str) -> RunEnvConfig:
        return self._envs[env_name]

    @property
    def work_dir(self) -> Path:
        """working directory of the project

        default value: create a unique key  into the users home folder `.tox3` folder (first 12 chars of
        :meth:`tox3.config.ToxConfig.root_dir` basename, plus hash of the absolute root dir path, salted to not
        conflict with already existing)
        """
        return self._work_dir

    @property
    def action(self) -> str:
        """the action to be executed, one of :data:`tox3.config.cli.ACTIONS`

        :note: CLI only"""
        return cast(str, getattr(self._cli, 'action'))

    @property
    def run_parallel(self) -> bool:
        """run tox environments in parallel once building the project finishes

        :note: CLI only"""
        return cast(bool, getattr(self._cli, 'run_parallel'))

    @property
    def skip_missing_interpreters(self) -> bool:
        """skip tox environments for whom we fail to find a matching Python interpreter"""
        return cast(bool, self._config_dict.get('skip_missing_interpreters', False))
