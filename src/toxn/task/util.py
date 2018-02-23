import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

from toxn.config.models.task.base import TaskConfig
from toxn.config.models.venv import Install
from toxn.util import Loggers


def install_params(batch_name: str, packages: List[str], config: TaskConfig,
                   develop: bool = False) -> Install:
    return Install(batch_name, packages, config.install_command, develop)


class TaskLogging(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """

    def process(self, msg: str, kwargs: Any) -> Tuple[str, Dict[str, Any]]:
        task = self.extra.get('task')  # type: ignore
        if task is None:
            task_info = ''
        else:
            task_info = f'[{task}] '
        return f"{task_info}{msg}", kwargs


@contextmanager
def change_dir(to_dir: Path, logger: Loggers) -> Generator[None, None, None]:
    cwd = Path(os.getcwd())
    if cwd != to_dir:
        logger.debug('change cwd to %r', to_dir)
        os.chdir(str(to_dir))
    try:
        yield
    finally:
        if cwd != to_dir:
            logger.debug('change cwd to %r', to_dir)
            os.chdir(str(cwd))
