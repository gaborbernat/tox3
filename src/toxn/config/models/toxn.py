import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from .core import CommonToxConfig
from toxn.config.models.task.build import BuildTaskConfig
from toxn.config.models.task.run import RunTaskConfig
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

        def _is_extra_task(key: str, conf: Any) -> bool:
            return isinstance(conf, dict) and \
                   key not in self.default_tasks and \
                   key not in {BuildTaskConfig.NAME, 'set_env'}

        self.default_tasks: List[str] = cast(List[str], self._config_dict.get('default_tasks', []))
        self.extra_tasks: List[str] = [k for k, v in self._config_dict.get('task', {}).items() if
                                       _is_extra_task(k, v)]
        defined = self.default_tasks + self.extra_tasks

        tasks = cast(List[str], getattr(self._cli, 'tasks', []))
        self.run_tasks: List[str] = tasks if tasks else self.default_tasks
        self.run_defined_tasks = self._run_defined_tasks(defined)

        self.tasks: List[str] = defined + self.run_defined_tasks

        def _raw_env(env_name: str) -> ConfDict:
            env = self._config_dict.get('task', {})
            base = {k: v for k, v in env.items() if k in {'set_env', } or not isinstance(v, dict)}
            if env_name in env:
                base.update(env[env_name])
            return base

        self.build = BuildTaskConfig(options,
                                     _raw_env(BuildTaskConfig.NAME),
                                     work_dir,
                                     BuildTaskConfig.NAME,
                                     build_system)
        self._envs: Dict[str, RunTaskConfig] = {k: RunTaskConfig(options,
                                                                 _raw_env(k),
                                                                 work_dir, k) for k in self.tasks}

    def _run_defined_tasks(self, defined: List[str]) -> List[str]:
        # environments that are invoked on demand
        run_defined: List[str] = []
        for env in self.run_tasks:
            if env not in defined:
                run_defined.append(env)
        return run_defined

    def task(self, env_name: str) -> RunTaskConfig:
        return self._envs[env_name]

    @property
    def work_dir(self) -> Path:
        """working directory of the project

        default value: create a unique key  into the users home folder `.toxn` folder (first 12 chars of
        :meth:`toxn.config.ToxConfig.root_dir` basename, plus hash of the absolute root dir path, salted to not
        conflict with already existing)
        """
        return self._work_dir

    @property
    def action(self) -> str:
        """the action to be executed, one of :literal_data:`toxn.config.cli.ACTIONS`

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
