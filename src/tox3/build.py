"""build the project"""
import logging
import os
import shutil

from tox3.config import BuildEnvConfig
from tox3.util import PrintAndKeepLastLine, run
from tox3.venv import Venv


async def create_install_package(config: BuildEnvConfig):
    build_dir = config.work_dir / '.build'
    out_dir = build_dir / 'dist'

    if out_dir.exists():
        logging.debug('clean package destination %r', out_dir)
        shutil.rmtree(out_dir)

    os.makedirs(out_dir, exist_ok=True)

    for path in [config.root_dir / 'dist',
                 config.root_dir / '.eggs']:
        if path.exists():
            logging.debug('clean %r', path)
            shutil.rmtree(path)

    env = Venv(build_dir, 'env')

    cwd = os.getcwd()
    try:
        logging.debug('change cwd to %r', config.root_dir)
        os.chdir(config.root_dir)

        logging.info('clean package dir')

        await run([env.executable, 'setup.py', 'clean', '--all'])
        await env.pip(config.build_requires, batch_name='build requires')

        printer = PrintAndKeepLastLine()

        script = f"""
import {config.build_backend} as build
import json
build_requires = build.get_requires_for_build_wheel(None)
print(json.dumps(build_requires))
        """
        result = await run([env.executable, '-c', script], stdout=printer)

        if not result and printer.last:
            await env.pip(printer.json, batch_name='setup requires')
        else:
            logging.error('could not build package')
            raise SystemExit(-1)

        logging.info('build package %r', config.root_dir)
        script = f"""
import {config.build_backend} as build
basename = build.build_wheel("{str(out_dir)}")
print(basename)
"""
        result = await run([env.executable, '-c', script], stdout=printer)
        if not result and printer.last:
            config.built_package = out_dir / printer.last
            logging.info('built %s', config.built_package)
        else:
            logging.error('could not build package')
            raise SystemExit(-1)
    finally:
        logging.debug('change cwd back to %r', cwd)
        os.chdir(cwd)
