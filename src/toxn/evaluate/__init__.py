"""evaluate a toxn workflow"""

import asyncio
import logging
import sys
from typing import Sequence

import colorlog  # type: ignore

from .list_tasks import list_bare, list_tasks
from .run_tasks import run_tasks
from ..config import ToxConfig, load as load_config
from ..config.cli import get_logging

ROOT_LOGGER = logging.getLogger()
LOGGER = logging.getLogger('main')


def _setup_logging(verbose: str, quiet: bool, logging_fmt: str) -> None:
    """Setup logging."""
    for log_handler in list(ROOT_LOGGER.handlers):  # remove handlers of libraries
        ROOT_LOGGER.removeHandler(log_handler)
    if quiet:
        ROOT_LOGGER.addHandler(logging.NullHandler())
    else:
        level = getattr(logging, verbose)
        fmt = f'%(log_color)s{logging_fmt}'
        formatter = colorlog.ColoredFormatter(fmt)
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.setLevel(level)
        ROOT_LOGGER.setLevel(level)
        stream_handler.setFormatter(formatter)
        ROOT_LOGGER.addHandler(stream_handler)
        LOGGER.debug('task logging to %s', logging.getLevelName(level))


def get_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()  # on windows IO needs this
    return asyncio.new_event_loop()  # default on UNIX is fine


def main(argv: Sequence[str]) -> int:
    _setup_logging(*get_logging(argv))

    loop = get_event_loop()
    LOGGER.debug('event loop %r', loop)

    # noinspection PyBroadException
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(execute(argv))
    except SystemExit as exception:
        return exception.code
    except Exception:
        LOGGER.exception('')
        return -1
    finally:
        loop.close()


async def execute(argv: Sequence[str]) -> int:
    # noinspection PyUnusedLocal
    result: int = 1
    config: ToxConfig = await load_config(argv)
    if config.action == 'run':
        result = await run_tasks(config, LOGGER)
    elif config.action == 'list':
        result = await list_tasks(config, LOGGER)
    elif config.action == 'list-bare':
        result = await list_bare(config.tasks, LOGGER)
    elif config.action == 'list-default-bare':
        result = await list_bare(config.default_tasks, LOGGER)
    return result
