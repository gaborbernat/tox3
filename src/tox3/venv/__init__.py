import logging
import os
import pickle
import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional, List

from tox3.interpreters import find_python, Python
from tox3.util import run, CmdLineBufferPrinter, rm_dir


class VenvParams(NamedTuple):
    recreate: bool
    dest_dir: Path
    name: str
    python: str

    @property
    def dir(self) -> Path:
        return self.dest_dir / self.name

    @property
    def cache(self) -> Path:
        return self.dir / f'.{self.name}.tox.cache'


class VenvCore(NamedTuple):
    root_dir: Path
    bin_path: Path
    executable: Path
    site_package: Path


class Venv:

    def __init__(self, base: Python, venv_core: VenvCore):
        self.core = venv_core
        self.base = base
        logging.info('virtual environment executable for %r ready at %r', self.base.python_name,
                     self.core.executable)

    async def pip(self, deps: List[str], batch_name: str = ''):
        if deps is not None:
            logging.info('pip install %s %r', batch_name, deps)
            os_env = os.environ.copy()
            if 'PYTHONPATH' in os_env:
                del os_env['PYTHONPATH']
            await run([self.core.executable, '-m', 'pip', 'install', '-U', *deps], env=os_env)


async def setup(params: VenvParams) -> Venv:
    """create a virtual environment"""
    if params.recreate:
        rm_dir(params.dir, 'recreate on')

    cache = _load_cache(params)
    if cache is not None:
        return cache

    base = await find_python(params.python)
    venv_core = await _create_venv(base, params)

    result = Venv(base, venv_core)

    logging.debug(f'write virtualenv config {params.cache}')
    with open(params.cache, mode='wb') as file:
        pickle.dump(result, file)

    return result


def _env_deps_changed(params: VenvParams, venv: 'Venv'):
    return params.python != venv.base.python_name


def _load_cache(venv: VenvParams) -> Optional['Venv']:
    if venv.cache.exists():
        logging.debug(f'load already existing virtualenv at {venv.cache}')
        with open(venv.cache, mode='rb') as file:
            result: Venv = pickle.load(file)
        if not _env_deps_changed(venv, result):
            return result
        rm_dir(venv.dir, 'env core dependencies changed')


async def _create_venv(base_python: Python, venv: VenvParams) -> VenvCore:
    logging.info('create venv %s at %r with %s', venv.name, venv.dir, base_python.version)
    if base_python.major_version < 3:
        venv_core = await _create_venv_python_2(base_python, venv.dir)
    else:
        venv_core = await _create_venv_python_3(base_python, venv.dir)
    return venv_core


async def _create_venv_python_3(base_python: Python, venv_dir: Path) -> VenvCore:
    printer = CmdLineBufferPrinter(limit=2)
    script = Path(__file__).parent / '_venv.py'
    await run(cmd=[base_python.exe, script, venv_dir], stdout=printer)
    executable, bin_path = Path(printer.elements.pop()), Path(printer.elements.pop())
    return VenvCore(venv_dir, bin_path, executable, await site_package(executable))


async def _create_venv_python_2(base_python: Python, venv_dir: Path) -> VenvCore:
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
    return VenvCore(venv_dir, bin_path, executable, await site_package(executable))


async def site_package(executable: Path) -> Path:
    printer = CmdLineBufferPrinter(limit=1)
    await run(cmd=[executable, '-c', 'import site; import json; print(json.dumps(site.getsitepackages()))'],
              stdout=printer)
    return Path(printer.json[-1])
