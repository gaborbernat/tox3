import logging
from typing import Any, Dict, List, Tuple

from tox3.config.models.env import EnvConfig
from tox3.config.models.venv import Install


def install_params(batch_name: str, packages: List[str], config: EnvConfig,
                   develop: bool = False) -> Install:
    return Install(batch_name, packages, config.install_command, develop)


class EnvLogging(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """

    def process(self, msg: str, kwargs: Any) -> Tuple[str, Dict[str, Any]]:
        env = self.extra.get('env')  # type: ignore
        if env is None:
            env_info = ''
        else:
            env_info = f'[{env}]'
        return f"{env_info}{msg}", kwargs
