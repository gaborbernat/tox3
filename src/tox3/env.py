import logging
import os
from functools import partial

from tox3.config import RunEnvConfig, BuildEnvConfig
from tox3.util import print_to_sdtout, run
from tox3.venv import Venv


async def run_env(config: RunEnvConfig, build_config: BuildEnvConfig):
    venv = await Venv.from_python(config.python, config.work_dir, config.name, config.recreate)
    extras = config.extras
    package = '{}{}'.format(build_config.built_package, '[{}]'.format(','.join(extras)) if extras else '')
    await venv.pip(deps=[package], batch_name='project package')
    for command in config.commands:
        logging.info('run: %s', command)
        env_vars = environment_variables(venv.bin_path)
        await run(command, env=env_vars, shell=True, stdout=partial(print_to_sdtout, level=logging.INFO))


def environment_variables(bin_path):
    os_env = os.environ.copy()
    paths = os_env.get('PATH', '').split(os.pathsep)
    paths = [bin_path] + paths
    os_env['PATH'] = os.pathsep.join(paths)
    return os_env
