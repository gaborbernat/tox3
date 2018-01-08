import asyncio
import datetime
import logging
import sys
from typing import Iterable

import colorlog

from .build import create_install_package
from .config import load as load_config, ToxConfig
from .config.cli import VERBOSITY_TO_LOG_LEVEL, get_logging
from .env import run_env

LOGGER = logging.getLogger()


def _clean_handlers(log):
    for log_handler in list(log.handlers):  # remove handlers of libraries
        log.removeHandler(log_handler)


def _setup_logging(verbose: bool, quiet: bool, logging_fmt: str):
    """Setup logging."""
    _clean_handlers(LOGGER)
    if verbose is None:
        verbose = 0
    if quiet:
        LOGGER.addHandler(logging.NullHandler())
    else:
        level = VERBOSITY_TO_LOG_LEVEL.get(verbose, logging.DEBUG)
        fmt = f'%(log_color)s{logging_fmt}'
        formatter = colorlog.ColoredFormatter(fmt)
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.setLevel(level)
        LOGGER.setLevel(level)
        stream_handler.setFormatter(formatter)
        LOGGER.addHandler(stream_handler)
        logging.debug('setup logging to %s', logging.getLevelName(level))


def main(argv: Iterable[str]) -> None:
    _setup_logging(*get_logging(argv))

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    logging.debug('got event loop %r', loop)

    try:
        result = loop.run_until_complete(run(argv))
        logging.debug('done with %s', result)
        return result
    finally:

        loop.close()


async def run(argv: Iterable[str]):
    start = datetime.datetime.now()
    try:
        config: ToxConfig = await load_config(argv)

        await create_install_package(config.build)

        for env_name in config.run_environments:
            await run_env(config.env(env_name), config.build)
        result = 0
    except BaseException:
        result = 1
        raise
    finally:
        logging.info('finished %s', datetime.datetime.now() - start)
    return result


def build_package():
    pass
