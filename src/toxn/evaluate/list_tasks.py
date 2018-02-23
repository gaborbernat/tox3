import logging
from itertools import chain
from typing import Callable, List, Sized

from toxn.config import ToxConfig


async def list_tasks(config: ToxConfig, logger: logging.Logger) -> int:
    def max_len(getter: Callable[[str], Sized]) -> int:
        return max(len(getter(e)) for e in chain(config.default_tasks,
                                                 config.extra_tasks,
                                                 config.run_defined_tasks))

    width = max_len(lambda e: e)
    python_width = max_len(lambda e: config.task(e).python)

    def print_tasks(tasks: List[str], type_info: str) -> None:
        if tasks:
            logger.info(f'{type_info}:')
        for name in tasks:
            task_str = name.ljust(width)
            python_str = config.task(name).python.ljust(python_width)
            logger.info(f'{task_str} [{python_str}] -> {config.task(name).description}')

    print_tasks(config.default_tasks, 'default tasks')
    print_tasks(config.extra_tasks, 'extra defined tasks')
    print_tasks(config.run_defined_tasks, 'run defined tasks')
    return 0


async def list_bare(tasks: List[str], logger: logging.Logger) -> int:
    for task in tasks:
        logger.info(task)
    return 0
