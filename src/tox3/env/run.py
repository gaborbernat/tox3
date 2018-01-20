import datetime
import logging
import re
import sys
from functools import partial
from pathlib import Path
from typing import Iterable, List, MutableMapping, Optional, Pattern, Set

from tox3.config import BuildEnvConfig, RunEnvConfig
from tox3.config.models.venv import VEnvCreateParam
from tox3.env.util import EnvLogging, change_dir, install_params
from tox3.util import Loggers, human_timedelta, list_to_cmd, print_to_sdtout, run
from tox3.venv import VEnv, setup as setup_venv, strip_env_vars


async def run_env(config: RunEnvConfig, build_config: BuildEnvConfig) -> int:
    start = datetime.datetime.now()
    logger = EnvLogging(logging.getLogger(__name__), {'env': config.envname})
    result = 0
    try:
        logger.info('start setup')
        env = await setup_venv(VEnvCreateParam(config.recreate, config.work_dir, config.name, config.python, logger))
        config.venv = env

        await env_setup(build_config, config, env)

        env_vars = strip_env_vars(env.params.bin_path)
        clean_env_vars(env_vars, config, logger)

        with change_dir(config.change_dir, logger):
            logger.info('setup in %s', human_timedelta(datetime.datetime.now() - start))
            for command in config.commands:
                logger.info('%s$ %s', config.change_dir, list_to_cmd(command))
                result = await run(command, logger=logger,
                                   stdout=partial(print_to_sdtout, level=logging.INFO),
                                   stderr=partial(print_to_sdtout, level=logging.ERROR),
                                   env=env_vars, shell=True,
                                   exit_on_fail=False)
                if result:
                    break
        return result
    finally:
        logger.info('done in %s with %s', human_timedelta(datetime.datetime.now() - start), result)


def global_pass_env() -> Set[str]:
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


PASS_ENV_ALWAYS: Set[str] = global_pass_env()


class EnvFilter:
    def __init__(self, pass_env: Iterable[str]) -> None:
        self.static = set(PASS_ENV_ALWAYS)
        self.patterns: List[Pattern[str]] = []
        for env in pass_env:
            if '*' in env:
                _pattern: Pattern[str] = re.compile(env.replace('*', '.*'))
                self.patterns.append(_pattern)
            else:
                self.static.add(env)

    def keep(self, key: str) -> bool:
        return key in self.static or any(pattern.match(key) for pattern in self.patterns)


def clean_env_vars(env: MutableMapping[str, str], config: RunEnvConfig, logger: Loggers) -> None:
    env_filter = EnvFilter(config.pass_env)
    for key in list(env.keys()):
        if env_filter.keep(key):
            logger.debug('keep env var %s=%r', key, env[key])
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
    if build_config.skip is False and config.install_build:
        if config.use_develop:
            project_package: Optional[Path] = config.root_dir
        else:
            project_package = build_config.built_package
        package = '{}{}'.format(project_package, '[{}]'.format(','.join(extras)) if extras else '')
        await env.install(install_params(f'project',
                                         [package],
                                         config,
                                         config.use_develop))
