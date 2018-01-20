import asyncio
import datetime
import logging
import sys
from itertools import chain
from typing import List, Sequence

import colorlog  # type: ignore

from tox3.util import human_timedelta
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
    return any(config.env(name).install_build and not config.env(name).use_develop for name in config.run_environments)


async def run(argv: Sequence[str]) -> int:
    start = datetime.datetime.now()
    # noinspection PyUnusedLocal
    result: int = 1
    config: ToxConfig = await load_config(argv)
    if config.action == 'run':
        try:
            result = await run_tox_envs(config)
        finally:
            LOGGER.info('finished %s with %s', human_timedelta(datetime.datetime.now() - start), result)
    elif config.action == 'list':
        result = await list_envs(config)
    elif config.action == 'list-bare':
        for env in config.environments:
            LOGGER.info(env)
    elif config.action == 'list-default-bare':
        for env in config.default_run_environments:
            LOGGER.info(env)
    return result


async def list_envs(config: ToxConfig) -> int:
    width = max(len(e) for e in chain(config.default_run_environments,
                                      config.extra_defined_environments,
                                      config.run_defined_environments))

    def print_envs(environments: List[str], type_info: str) -> None:
        if environments:
            LOGGER.info(f'{type_info}:')
        for env in environments:
            env_str = env.ljust(width)
            LOGGER.info(f'{env_str} -> {config.env(env).description}')

    print_envs(config.default_run_environments, 'default environments')
    print_envs(config.extra_defined_environments, 'extra defined environments')
    print_envs(config.run_defined_environments, 'run defined environments')
    return 0


async def run_tox_envs(config: ToxConfig) -> int:
    run_build = config.build.skip is False and build_needs_install(config)
    if run_build:
        await create_install_package(config.build)

    if config.run_parallel:
        futures = []
        loop = asyncio.get_event_loop()
        for env_name in config.run_environments:
            futures.append(loop.create_task(run_env(config.env(env_name), config.build)))
        results = [await f for f in futures]
    else:
        empty_line = run_build
        results = []
        for env_name in config.run_environments:
            if empty_line:
                LOGGER.info('')
            else:
                empty_line = True
            results.append(await run_env(config.env(env_name), config.build))
    return 1 if any(r for r in results) else 0
