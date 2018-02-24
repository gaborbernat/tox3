import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from toxn.config.models.task.build import BuildTaskConfig
from toxn.config.models.task.run import RunTaskConfig
from .core import CommonToxConfig
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

        def extract_base_conf(all_task_conf: ConfDict) -> ConfDict:
            return {k: v for k, v in all_task_conf.items() if k in {'set_env', } or not isinstance(v, dict)}

        def _raw_task(task: str) -> ConfDict:
            all_task_conf = self._config_dict.get('task', {})
            task_conf = extract_base_conf(all_task_conf)
            merge_conf(task, all_task_conf, task_conf)

            return task_conf

        def merge_conf(task: str, all_task_conf: ConfDict, task_conf: ConfDict) -> None:
            if task in all_task_conf:
                cur_conf = all_task_conf[task]
                if 'base' in cur_conf:
                    merge_conf(cur_conf['base'], all_task_conf, task_conf)
                task_conf.update(cur_conf)

        self.build = BuildTaskConfig(options,
                                     _raw_task(BuildTaskConfig.NAME),
                                     work_dir,
                                     BuildTaskConfig.NAME,
                                     build_system)
        self._tasks: Dict[str, RunTaskConfig] = {k: RunTaskConfig(options,
                                                                  _raw_task(k),
                                                                  work_dir, k) for k in self.tasks}

    def _run_defined_tasks(self, defined: List[str]) -> List[str]:
        # environments that are invoked on demand
        run_defined: List[str] = []
        for task in self.run_tasks:
            if task not in defined:
                run_defined.append(task)
        return run_defined
                                    
    def task(self, name: str) -> RunTaskConfig:
        return self._tasks[name]

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
        """run tox tasks in parallel once building the project finishes

        :note: CLI only"""
        return cast(bool, getattr(self._cli, 'run_parallel'))

    @property
    def skip_missing_interpreters(self) -> bool:
        """skip tox tasks for whom we fail to find a matching Python interpreter"""
        return cast(bool, self._config_dict.get('skip_missing_interpreters', False))
