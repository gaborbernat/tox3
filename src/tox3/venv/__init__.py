import logging
import os
import pickle
import re
import sys
from pathlib import Path
from typing import Mapping, Optional

from tox3.config.models.venv import Install, VEnvCreateParam, VEnvParams
from tox3.interpreters import Python, find_python
from tox3.util import CmdLineBufferPrinter, rm_dir, run, list_to_cmd


def strip_env_vars(bin_path: Path) -> Mapping[str, str]:
    os_env = os.environ.copy()
    paths = os_env.get('PATH', '').split(os.pathsep)
    paths = [str(bin_path)] + paths
    os_env['PATH'] = os.pathsep.join(paths)
    if 'PYTHONPATH' in os_env:
        del os_env['PYTHONPATH']
    return os_env


class VEnv:

    def __init__(self, python: Python, params: VEnvParams) -> None:
        self.params: VEnvParams = params
        self.python: Python = python
        logging.info('virtual environment executable for %r ready at %r', self.python.python_name,
                     self.params.executable)

    async def install(self, params: Install) -> None:
        if params.packages is not None:
            cmd = '{} {} {}'.format(params.base_cmd,
                                    '-e' if params.use_develop else '',
                                    list_to_cmd(params.packages))
            await run(cmd, env=strip_env_vars(self.params.bin_path), shell=True)


async def setup(params: VEnvCreateParam) -> VEnv:
    """create a virtual environment"""
    if params.recreate:
        rm_dir(params.dir, 'recreate on')

    cache = _load_cache(params)
    if cache is not None:
        return cache

    base = await find_python(params.python)
    venv_core = await _create_venv(base, params)

    result = VEnv(base, venv_core)

    logging.debug(f'write virtualenv config {params.cache}')
    with open(params.cache, mode='wb') as file:
        pickle.dump(result, file)

    return result


def _env_deps_changed(params: VEnvCreateParam, venv: VEnv) -> bool:
    return params.python != venv.python.python_name


def _load_cache(venv: VEnvCreateParam) -> Optional[VEnv]:
    if venv.cache.exists():
        logging.debug(f'load already existing virtualenv at {venv.cache}')
        with open(venv.cache, mode='rb') as file:
            result: VEnv = pickle.load(file)
        if not _env_deps_changed(venv, result):
            return result
        rm_dir(venv.dir, 'env core dependencies changed')
    return None


async def _create_venv(base_python: Python, venv: VEnvCreateParam) -> VEnvParams:
    logging.info('create venv %s at %r with %s', venv.name, venv.dir, base_python.version)
    if base_python.major_version < 3:
        venv_core = await _create_venv_python_2(base_python, venv.dir)
    else:
        venv_core = await _create_venv_python_3(base_python, venv.dir)
    return venv_core


async def _create_venv_python_3(base_python: Python, venv_dir: Path) -> VEnvParams:
    printer = CmdLineBufferPrinter(limit=2)
    script = Path(__file__).parent / '_venv.py'
    await run(cmd=[base_python.exe, script, venv_dir], stdout=printer)
    executable, bin_path = Path(printer.elements.pop()), Path(printer.elements.pop())
    return VEnvParams(venv_dir, bin_path, executable, await site_package(executable))


async def _create_venv_python_2(base_python: Python, venv_dir: Path) -> VEnvParams:
    printer = CmdLineBufferPrinter(limit=None)
    await run([sys.executable, '-m', 'virtualenv', '--no-download', '--python',
               base_python.exe, venv_dir],
              stdout=printer)
    pattern = re.compile(r'New python executable in (.*)')
    for line in printer.elements:
        logging.info(line)
        match = re.match(pattern, line)
        if match:
            executable = Path(match.group(1))
            bin_path = executable.parent
            break
    else:
        raise Exception('could not find executable')
    return VEnvParams(venv_dir, bin_path, executable, await site_package(executable))


async def site_package(executable: Path) -> Path:
    printer = CmdLineBufferPrinter(limit=1)
    await run(cmd=[executable, '-c', 'import site; import json; print(json.dumps(site.getsitepackages()))'],
              stdout=printer)
    return Path(printer.json[-1])
