"""build the project"""
import json
import logging
import os
import shutil
import venv

from tox3.config import Config
from tox3.util import print_to_sdtout, run


class EnvB(venv.EnvBuilder):
    executable = None

    def post_setup(self, context):
        self.executable = context.env_exe


async def create_install_package(config: Config):
    build_dir = config.work_dir / '.build'
    env_dir = build_dir / 'env'
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

    logging.info('create virtual environment for package build in %r', env_dir)
    venv.create(env_dir, with_pip=True)
    env_build = EnvB(with_pip=True)
    env_build.create(env_dir)
    logging.info('virtual environment executable at %r', env_build.executable)

    cwd = os.getcwd()
    try:
        logging.debug('change cwd to %r', config.root_dir)
        os.chdir(config.root_dir)

        logging.info('clean package dir')
        await run([env_build.executable, 'setup.py', 'clean', '--all'])

        logging.info('pip install build requires %r', config.build_requires)
        await run([env_build.executable, '-m', 'pip', 'install', *config.build_requires])

        last_stdout = None

        def store_last_stdout(line):
            nonlocal last_stdout
            print_to_sdtout(line)
            last_stdout = line

        script = f"""
import {config.build_backend} as build
import json
build_requires = build.get_requires_for_build_wheel(None)
print(json.dumps(build_requires))
        """
        result = await run([env_build.executable, '-c', script], stdout=store_last_stdout)
        if not result and last_stdout:
            build_package_requires = json.loads(last_stdout)
            logging.info('pip install build run requires %r', build_package_requires)
            await run([env_build.executable, '-m', 'pip', 'install', *build_package_requires])
        else:
            logging.error('could not build package')
            raise SystemExit(-1)

        logging.info('build package %r', config.root_dir)
        script = f"""
import {config.build_backend} as build
basename = build.build_wheel("{str(out_dir)}")
print(basename)
"""
        result = await run([env_build.executable, '-c', script], stdout=store_last_stdout)
        if not result and last_stdout:
            config.built_package = out_dir / last_stdout
            logging.info('built %s', config.built_package)
        else:
            logging.error('could not build package')
            raise SystemExit(-1)
    finally:
        logging.debug('change cwd back to %r', cwd)
        os.chdir(cwd)
