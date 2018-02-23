import asyncio
import logging
from datetime import datetime
from typing import Optional

from toxn.config import ToxConfig
from toxn.config.models.task.build import BuiltTaskConfig
from toxn.task import build, run_task
from toxn.util import human_timedelta


def build_needs_install(config: ToxConfig) -> bool:
    for name in config.run_tasks:
        env = config.task(name)
        if env.install_build:
            if env.use_develop and env.install_for_build_requires is False:
                continue
            return True
    return False


async def run_tasks(config: ToxConfig, logger: logging.Logger) -> int:
    start = datetime.now()
    result = None
    try:
        run_build = config.build.skip is False and build_needs_install(config)
        built: Optional[BuiltTaskConfig] = await build(config.build) if run_build else None

        if config.run_parallel:
            futures = []
            loop = asyncio.get_event_loop()
            for name in config.run_tasks:
                futures.append(loop.create_task(run_task(config.task(name), built,
                                                         config.skip_missing_interpreters)))
            results = [await f for f in futures]
        else:
            empty_line = run_build
            results = []
            for name in config.run_tasks:
                if empty_line:
                    logger.info('')
                else:
                    empty_line = True
                results.append(await run_task(config.task(name), built, config.skip_missing_interpreters))
        fails = [r for r in results if r]
        result = (fails[0] if len(fails) == 1 else 1) if fails else 0
        return result
    finally:
        logging.info('finished %s with %s', human_timedelta(datetime.now() - start), result)
