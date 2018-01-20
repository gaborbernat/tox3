import asyncio
import datetime
import logging
import sys
from typing import Sequence

import colorlog  # type: ignore

from .config import ToxConfig, load as load_config
from .config.cli import get_logging
from .env import create_install_package, run_env

ROOT_LOGGER = logging.getLogger()
LOGGER = logging.getLogger('main')


def _clean_handlers(log: logging.Logger) -> None:
    for log_handler in list(log.handlers):  # remove handlers of libraries
        log.removeHandler(log_handler)


def _setup_logging(verbose: str, quiet: bool, logging_fmt: str) -> None:
    """Setup logging."""
    _clean_handlers(ROOT_LOGGER)
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
        LOGGER.debug('setup logging to %s', logging.getLevelName(level))


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
        result = loop.run_until_complete(run(argv))
        LOGGER.debug('done with %s', result)
        return result
    except SystemExit as exc:
        return exc.code
    except Exception:
        LOGGER.exception('failure')
        return -1
    finally:
        loop.close()


def build_needs_install(config: ToxConfig) -> bool:
    return any(config.env(name).install_build for name in config.run_environments)


async def run(argv: Sequence[str]) -> int:
    start = datetime.datetime.now()
    # noinspection PyUnusedLocal
    result: int = 1
    try:
        config: ToxConfig = await load_config(argv)

        if config.build.skip is False and build_needs_install(config):
            await create_install_package(config.build)

        for env_name in config.run_environments:
            LOGGER.info('')
            result = await run_env(config.env(env_name), config.build)
            if result:
                break
        else:
            result = 0
    finally:
        LOGGER.info('finished %s', datetime.datetime.now() - start)
    return result
