import asyncio
import datetime
import logging
import sys
from typing import Sequence

import colorlog  # type: ignore

from .config import ToxConfig, load as load_config
from .config.cli import VERBOSITY_TO_LOG_LEVEL, get_logging
from .env import create_install_package, run_env

LOGGER = logging.getLogger()


def _clean_handlers(log: logging.Logger) -> None:
    for log_handler in list(log.handlers):  # remove handlers of libraries
        log.removeHandler(log_handler)


def _setup_logging(verbose: bool, quiet: bool, logging_fmt: str) -> None:
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


def get_event_loop():
    if sys.platform == 'win32':
        return asyncio.ProactorEventLoop()  # on windows IO needs this
    return asyncio.new_event_loop()  # default on UNIX is fine


def main(argv: Sequence[str]) -> int:
    _setup_logging(*get_logging(argv))

    loop = get_event_loop()
    logging.debug('event loop %r', loop)

    # noinspection PyBroadException
    try:
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run(argv))
        logging.debug('done with %s', result)
        return result
    except SystemExit as exc:
        return exc.code
    except Exception:
        logging.exception('failure')
        return -1
    finally:
        loop.close()


async def run(argv: Sequence[str]) -> int:
    start = datetime.datetime.now()
    # noinspection PyUnusedLocal
    result: int = 1
    try:
        config: ToxConfig = await load_config(argv)

        if config.build.skip is False:
            await create_install_package(config.build)

        for env_name in config.run_environments:
            await run_env(config.env(env_name), config.build)
        result = 0
    finally:
        logging.info('finished %s', datetime.datetime.now() - start)
    return result
