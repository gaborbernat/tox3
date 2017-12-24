import asyncio
import logging
import shelve
import sys
from typing import List, Optional

import colorlog

from tox3.build import create_install_package
from tox3.config import load as load_config, ToxConfig
from tox3.config.static.cli import VERBOSITY_TO_LOG_LEVEL, get_logging
from tox3.env import run_env

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


def main(argv: List[str]) -> None:
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


async def run(argv: List[str]):
    config: ToxConfig = await load_config(argv)

    cache_file = str(config.work_dir / '.tox3.cache')
    with shelve.open(cache_file) as cache:
        prev_config: Optional[ToxConfig] = cache.get('config')

        await create_install_package(config.build, prev_config.build if prev_config else None)

        for env_name in config.run_environments:
            await run_env(config.env(env_name), config.build)
        cache.__setitem__('config', config)

    return 0


def build_package():
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
