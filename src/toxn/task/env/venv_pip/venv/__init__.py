import logging
import os
import pickle
import re
import sys
from functools import partial
from pathlib import Path
from typing import MutableMapping, Optional

from toxn.config.models.task.base import VEnv
from toxn.config.models.venv import Install, VEnvCreateParam, VEnvParams
from toxn.task.interpreters import Python, find_python
from toxn.util import CmdLineBufferPrinter, Loggers, list_to_cmd, print_to_sdtout, rm_dir, run


def strip_env_vars(bin_path: Path) -> MutableMapping[str, str]:
    os_env = os.environ.copy()
    paths = os_env.get('PATH', '').split(os.pathsep)
    paths = [str(bin_path)] + paths
    os_env['PATH'] = os.pathsep.join(paths)
    if 'PYTHONPATH' in os_env:
        del os_env['PYTHONPATH']
    return os_env


async def install(venv: VEnv, params: Install) -> None:
    if params.packages:
        cmd = list(params.base_cmd)
        if params.use_develop:
            cmd.append('-e')
        cmd.extend(params.packages)
        venv.logger.info('install %s', list_to_cmd(cmd))
        await run(cmd, env=strip_env_vars(venv.params.bin_path), shell=True, logger=venv.logger,
                  exit_on_fail=True,
                  stdout=partial(print_to_sdtout, level=logging.DEBUG),
                  stderr=partial(print_to_sdtout, level=logging.ERROR))


async def setup(params: VEnvCreateParam) -> VEnv:
    """create a virtual environment"""
    if params.recreate:
        rm_dir(params.dir, 'recreate on', params.logger)

    cache = _load_cache(params)
    if cache is not None:
        return cache

    base = await find_python(params.python, params.logger)
    venv_core = await _create_venv(base, params)

    result = VEnv(base, venv_core, params.logger)

    params.logger.debug(f'write virtualenv config {params.cache}')
    with open(params.cache, mode='wb') as file:
        result.logger = None  # type: ignore
        pickle.dump(result, file)
        result.logger = params.logger
    return result


def _env_deps_changed(params: VEnvCreateParam, venv: VEnv) -> bool:
    return params.python != venv.python.python_name


def _load_cache(venv: VEnvCreateParam) -> Optional[VEnv]:
    if venv.cache.exists():
        venv.logger.debug(f'load already existing virtualenv at {venv.cache}')
        with open(venv.cache, mode='rb') as file:
            result: VEnv = pickle.load(file)
            result.logger = venv.logger
        if not _env_deps_changed(venv, result):
            return result
        rm_dir(venv.dir, 'task core dependencies changed', venv.logger)
    return None


async def _create_venv(base_python: Python, venv: VEnvCreateParam) -> VEnvParams:
    venv.logger.info('create venv %s at %r with %r', venv.name, venv.dir, base_python.version)
    if base_python.major_version < 3:
        venv_core = await _create_venv_python_2(base_python, venv.dir, venv.logger)
    else:
        venv_core = await _create_venv_python_3(base_python, venv.dir, venv.logger)
    return venv_core


async def _create_venv_python_3(base_python: Python, venv_dir: Path, logger: Loggers) -> VEnvParams:
    printer = CmdLineBufferPrinter(limit=2)
    script = Path(__file__).parent / '_venv.py'
    await run(cmd=[base_python.exe, script, venv_dir], stdout=printer, logger=logger)
    executable, bin_path = Path(printer.elements.pop()), Path(printer.elements.pop())
    return VEnvParams(venv_dir, bin_path, executable, await site_package(executable, logger))


async def _create_venv_python_2(base_python: Python, venv_dir: Path, logger: Loggers) -> VEnvParams:
    printer = CmdLineBufferPrinter(limit=None)
    await run([sys.executable, '-m', 'virtualenv', '--no-download', '--python',
               base_python.exe, venv_dir], stdout=printer, logger=logger)
    pattern = re.compile(r'New python executable in (.*)')
    for line in printer.elements:
        logger.info(line)
        match = re.match(pattern, line)
        if match:
            executable = Path(match.group(1))
            bin_path = executable.parent
            break
    else:
        raise Exception('could not find executable')
    return VEnvParams(venv_dir, bin_path, executable, await site_package(executable, logger))


async def site_package(executable: Path, logger: Loggers) -> Path:
    printer = CmdLineBufferPrinter(limit=1)

    await run(cmd=[executable, '-c', 'from distutils.sysconfig import get_python_lib;'
                                     'print(get_python_lib())'],
              stdout=printer, logger=logger)
    return Path(printer.last)
