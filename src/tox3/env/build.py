"""build the project"""
import datetime
import logging
import os
from pathlib import Path
from typing import List, Optional, cast

from toxn.config import BuildEnvConfig
from toxn.config.models.venv import VEnvCreateParam
from toxn.env.util import EnvLogging, change_dir, install_params
from toxn.util import CmdLineBufferPrinter, human_timedelta, list_to_cmd, rm_dir, run
from toxn.venv import VEnv, setup as setup_venv

LOGGER = EnvLogging(logging.getLogger(__name__), {'env': '_build'})


async def create_install_package(config: BuildEnvConfig) -> None:
    start = datetime.datetime.now()
    result = None
    name = '_build'
    try:
        LOGGER.info('build project %s as %s', config.root_dir, config.build_type)
        env = await setup_venv(VEnvCreateParam(config.recreate, config.work_dir, name, config.python, LOGGER))
        config.venv = env
        await env.install(install_params(f'build requires',
                                         config.build_requires,
                                         config))

        out_dir = await _make_and_clean_out_dir(env)

        with change_dir(config.root_dir, LOGGER):
            if config.build_backend is not None:
                config.for_build_requires = await _get_requires_for_build(env, config.build_type,
                                                                          cast(str, config.build_backend_base),
                                                                          cast(str, config.build_backend_full))
                await env.install(install_params(f'for build requires',
                                                 config.for_build_requires,
                                                 config))

            result = await _build(env, out_dir, config.build_type,
                                  config.build_backend_base, config.build_backend_full)
            config.built_package = result
        for command in config.teardown_commands:
            LOGGER.info('teardown: %s$ %s', config.root_dir, list_to_cmd(command))
            result_code = await run(command, logger=LOGGER, shell=True,
                                    exit_on_fail=True)
            if result_code:
                break
    finally:
        LOGGER.info('built %s in %s', result, human_timedelta(datetime.datetime.now() - start))


async def _build(env: VEnv,
                 out_dir: Path,
                 build_type: str,
                 build_backend_base: Optional[str],
                 build_backend_full: Optional[str]) -> Path:
    if build_backend_full is not None:
        printer = CmdLineBufferPrinter(limit=1)
        script = f"""
import sys
import {build_backend_base}        
basename = {build_backend_full}.build_{build_type}(sys.argv[1])
print(basename)
"""
        await run([env.params.executable, '-c', script, out_dir], stdout=printer, logger=LOGGER)
        result = out_dir / printer.last
    else:
        build_cmd = 'sdist' if build_type == 'sdist' else 'bdist_wheel'
        await run([env.params.executable, 'setup.py', build_cmd, '--dist-dir', out_dir, "--formats=zip"], logger=LOGGER)
        # noinspection PyTypeChecker
        result = next(out_dir.iterdir())
    return result


async def _get_requires_for_build(env: VEnv,
                                  build_type: str,
                                  build_backend_base: str,
                                  build_backend_full: str) -> List[str]:
    printer = CmdLineBufferPrinter(limit=1)
    script = f"""
import {build_backend_base}        
import json
for_build_requires = {build_backend_full}.get_requires_for_build_{build_type}(None)
print(json.dumps(for_build_requires))
        """
    await run([str(env.params.executable), '-c', script], stdout=printer, logger=LOGGER)
    return cast(List[str], printer.json)


async def _make_and_clean_out_dir(env: VEnv) -> Path:
    out_dir = env.params.root_dir / '.out'
    if out_dir.exists():
        if not out_dir.is_dir():
            rm_dir(out_dir, 'package destination is a file', LOGGER)
        else:
            for _ in out_dir.iterdir():
                rm_dir(out_dir, 'package destination is not empty', LOGGER)
                break
    os.makedirs(str(out_dir), exist_ok=True)
    return out_dir
