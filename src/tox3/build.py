"""build the project"""
import logging
import os
import shutil
from contextlib import contextmanager
from pathlib import Path

from .config import BuildEnvConfig
from .util import CmdLineBufferPrinter, run, rm_dir
from .venv import setup as setup_venv, VenvParams, Venv


@contextmanager
def change_dir(to_dir):
    cwd = os.getcwd()
    logging.debug('change cwd to %r', to_dir)
    os.chdir(to_dir)
    try:
        yield
    finally:
        logging.debug('change cwd to %r', to_dir)
        os.chdir(cwd)


async def create_install_package(config: BuildEnvConfig):
    name = '_build'
    env = await setup_venv(VenvParams(config.recreate, config.work_dir, name, config.python))
    await env.pip(config.build_requires, batch_name='build requires')

    out_dir = await _make_and_clean_out_dir(env)

    with change_dir(config.root_dir):
        config.for_build_requires = await _get_requires_for_build(env, config.build_type,
                                                                  config.build_backend_base,
                                                                  config.build_backend_full)
        await env.pip(config.for_build_requires, batch_name=f'for build requires ({config.build_type})')
        await _clean(config, env.core.executable)
        result = await _build(env, out_dir, config.build_type,
                              config.build_backend_base, config.build_backend_full)
        config.built_package = result
        await _clean(config, env.core.executable)


async def _build(env: Venv, out_dir: Path, build_type: str, build_backend_base: str, build_backend_full: str):
    printer = CmdLineBufferPrinter(limit=1)
    script = f"""
import sys
import {build_backend_base}        
basename = {build_backend_full}.build_{build_type}(sys.argv[1])
print(basename)
"""
    await run([env.core.executable, '-c', script, out_dir], stdout=printer)
    result = out_dir / printer.last
    logging.info('built %s', result)
    return result


async def _get_requires_for_build(env: Venv, build_type: str, build_backend_base: str, build_backend_full: str):
    printer = CmdLineBufferPrinter(limit=1)
    script = f"""
import {build_backend_base}        
import json
for_build_requires = {build_backend_full}.get_requires_for_build_{build_type}(None)
print(json.dumps(for_build_requires))
        """
    await run([str(env.core.executable), '-c', script], stdout=printer)
    return printer.json


async def _make_and_clean_out_dir(env: Venv):
    out_dir = env.core.root_dir / '.out'
    if out_dir.exists():
        if not out_dir.is_dir():
            rm_dir(out_dir, 'package destination is a file')
        else:
            for _ in out_dir.iterdir():
                rm_dir(out_dir, 'package destination is not empty')
                break
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


async def _clean(config, executable):
    logging.info('clean package dir')

    await run([str(executable), 'setup.py', 'clean', '--all'])

    for path in [config.root_dir / 'dist',
                 config.root_dir / '.eggs']:
        if path.exists():
            logging.debug('clean %r', path)
            shutil.rmtree(path)
