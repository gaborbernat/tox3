"""configuration objects

these are a join of user provided inputs:
- cli
- environment variable
- tox config file
and generated by the running of these tool (referred to as state).
"""
from pathlib import Path
from typing import IO, Sequence, Union

from toxn.config.models.core import root_dir
from .cli import parse
from toxn.config.models.task.run import RunTaskConfig
from .models.toxn import ToxConfig
from .project import BuildSystem, ConfDict, from_toml
from .util import Substitute


async def load(argv: Sequence[str]) -> ToxConfig:
    options = await parse(argv)
    config_object: Union[Path, IO[str]] = getattr(options, 'config')
    build_system, conf_dict, conf_path = await from_toml(config_object)

    work_dir_conf = Path(conf_dict['work_dir']) if 'work_dir' in conf_dict else None
    work_dir = root_dir(options, work_dir_conf)

    return ToxConfig(options, build_system, conf_dict, conf_path, work_dir)


__all__ = ('ToxConfig', 'RunTaskConfig', 'BuildTaskConfig', 'load')
