import logging
import os
from functools import partial

from tox3.config import RunEnvConfig, BuildEnvConfig
from tox3.util import print_to_sdtout, run
from tox3.venv import setup as setup_venv, VenvParams


async def run_env(config: RunEnvConfig, build_config: BuildEnvConfig):
    env = await setup_venv(VenvParams(config.recreate, config.work_dir, config.name, config.python))
    if not config.build_wheel:
        await env.pip(build_config.for_build_requires, batch_name=f'for build requires ({config.build_type})')

    extras = config.extras
    package = '{}{}'.format(build_config.built_package, '[{}]'.format(','.join(extras)) if extras else '')
    await env.pip(deps=[package], batch_name='project package')
    for command in config.commands:
        logging.info('run: %s', command)
        env_vars = environment_variables(env.core.bin_path)
        await run(command, env=env_vars, shell=True, stdout=partial(print_to_sdtout, level=logging.INFO),
                  exit_on_fail=False)


def environment_variables(bin_path):
    os_env = os.environ.copy()
    paths = os_env.get('PATH', '').split(os.pathsep)
    paths = [str(bin_path)] + paths
    os_env['PATH'] = os.pathsep.join(paths)
    return os_env
