from functools import partial
import logging

from tox3.config import BuildEnvConfig, RunEnvConfig
from tox3.config.models.venv import VEnvCreateParam
from tox3.env.util import install_params
from tox3.util import print_to_sdtout, run
from tox3.venv import VEnv, setup as setup_venv, strip_env_vars


async def run_env(config: RunEnvConfig, build_config: BuildEnvConfig) -> None:
    env = await setup_venv(VEnvCreateParam(config.recreate, config.work_dir, config.name, config.python))
    config.venv = env

    await env_setup(build_config, config, env)

    env_vars = strip_env_vars(env.params.bin_path)
    for command in config.commands:
        logging.info('[%s] run: %s', config.name, command)
        await run(command, env=env_vars, shell=True, stdout=partial(print_to_sdtout, level=logging.INFO),
                  exit_on_fail=False)


async def env_setup(build_config: BuildEnvConfig, config: RunEnvConfig, env: VEnv):
    if config.install_build_requires:
        await env.install(install_params(f'build requires ({build_config.build_type})',
                                         build_config.build_requires,
                                         config))

    if not build_config.build_wheel or config.install_for_build_requires:
        await env.install(install_params(f'for build requires ({build_config.build_type})',
                                         build_config.for_build_requires,
                                         config))

    if config.deps:
        await env.install(install_params(f'deps',
                                         config.deps,
                                         config))

    extras = config.extras
    package = '{}{}'.format(build_config.built_package, '[{}]'.format(','.join(extras)) if extras else '')
    await env.install(install_params(f'project',
                                     [package],
                                     config,
                                     config.usedevelop))
