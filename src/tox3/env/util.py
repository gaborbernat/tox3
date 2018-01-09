from typing import List

from tox3.config.models.env import EnvConfig
from tox3.config.models.venv import Install


def install_params(batch_name: str, packages: List[str], config: EnvConfig, develop: bool = False) -> Install:
    return Install(batch_name, packages, config.install_command, develop)
