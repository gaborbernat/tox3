import asyncio
import logging
import sys
from typing import List

from tox3.build import create_install_package
from tox3.config import load as load_config
from tox3.config.cli import VERBOSITY_TO_LOG_LEVEL, get_verbose

LOGGER = logging.getLogger()


def _clean_handlers(log):
    for log_handler in list(log.handlers):  # remove handlers of libraries
        log.removeHandler(log_handler)


def _setup_logging(verbose=None, quiet=False):
    """Setup logging."""
    _clean_handlers(LOGGER)
    if verbose is None:
        verbose = 0
    if quiet:
        LOGGER.addHandler(logging.NullHandler())
    else:
        level = VERBOSITY_TO_LOG_LEVEL.get(verbose, logging.DEBUG)
        locate = 'pathname' if verbose >= 3 else 'module'
        formatter = logging.Formatter(str("[%(asctime)s] %(levelname)s [%({})s:%(lineno)d] %(message)s".format(locate)))
        stream_handler = logging.StreamHandler(stream=sys.stderr)
        stream_handler.setLevel(level)
        LOGGER.setLevel(level)
        stream_handler.setFormatter(formatter)
        LOGGER.addHandler(stream_handler)
        logging.debug('setup logging to %s', logging.getLevelName(level))


def main(argv: List[str]):
    _setup_logging(*get_verbose(argv))

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
    config = await load_config(argv)
    await create_install_package(config)

    print('')
    for env_name in config.envs:
        print(f'{env_name} => {config.env(env_name)}')
        
    return 0


def build_package():
    pass


if __name__ == '__main__':
    main(sys.argv[1])
