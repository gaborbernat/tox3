import logging
import sys
from functools import partial
from os import getcwd
from pathlib import Path
from typing import MutableMapping, Optional

from tox3.config import BuildEnvConfig, RunEnvConfig
from tox3.config.models.venv import VEnvCreateParam
from tox3.env.util import EnvLogging, change_dir, install_params
from tox3.util import Loggers, list_to_cmd, print_to_sdtout, run
from tox3.venv import VEnv, setup as setup_venv, strip_env_vars


async def run_env(config: RunEnvConfig, build_config: BuildEnvConfig) -> int:
    logger = EnvLogging(logging.getLogger(__name__), {'env': config.envname})

    env = await setup_venv(VEnvCreateParam(config.recreate, config.work_dir, config.name, config.python, logger))
    config.venv = env

    await env_setup(build_config, config, env)
    result = 0

    env_vars = strip_env_vars(env.params.bin_path)
    clean_env_vars(env_vars, config, logger)

    with change_dir(config.changedir, logger):
        for command in config.commands:
            logger.info('cmd: %s in %s', list_to_cmd(command), getcwd())
            result = await run(command, logger=logger,
                               stdout=partial(print_to_sdtout, level=logging.INFO), env=env_vars, shell=True,
                               exit_on_fail=False)
            if result:
                break
    return result


def global_pass_env():
    pass_env = {"PATH", "PIP_INDEX_URL", "LANG", "LANGUAGE", "LD_LIBRARY_PATH"}
    if sys.platform == "win32":
        pass_env.add("SYSTEMDRIVE")  # needed for pip6
        pass_env.add("SYSTEMROOT")  # needed for python's crypto module
        pass_env.add("PATHEXT")  # needed for discovering executables
        pass_env.add("COMSPEC")  # needed for distutils cygwincompiler
        pass_env.add("TEMP")
        pass_env.add("TMP")
        pass_env.add("NUMBER_OF_PROCESSORS")  # for `multiprocessing.cpu_count()` on Windows (prior to Python 3.4).
        pass_env.add("PROCESSOR_ARCHITECTURE")  # platform.machine()
        pass_env.add("USERPROFILE")  # needed for `os.path.expanduser()`
        pass_env.add("MSYSTEM")  # fixes #429
    else:
        pass_env.add("TMPDIR")
    return pass_env


PASS_ENV_ALWAYS = global_pass_env()


def clean_env_vars(env: MutableMapping[str, str], config: RunEnvConfig, logger: Loggers):
    for key in list(env.keys()):
        if key in PASS_ENV_ALWAYS or key in config.pass_env:
            continue
        logger.debug('remove env var %s=%r', key, env[key])
        del env[key]
    for key, value in config.set_env.items():
        logger.debug('set env var %s=%r', key, value)
        env[key] = value


async def env_setup(build_config: BuildEnvConfig,
                    config: RunEnvConfig,
                    env: VEnv) -> None:
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
    if build_config.skip is False:
        if config.usedevelop:
            project_package: Optional[Path] = config.root_dir
        else:
            project_package = build_config.built_package
        package = '{}{}'.format(project_package, '[{}]'.format(','.join(extras)) if extras else '')
        await env.install(install_params(f'project',
                                         [package],
                                         config,
                                         config.usedevelop))
