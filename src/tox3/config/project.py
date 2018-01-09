"""parse the project file"""
import logging
from pathlib import Path
from typing import IO, Union, Tuple, Dict, Any, List
from typing import NamedTuple

import toml  # type: ignore

FileConf = Dict[str, Any]


class BuildSystem(NamedTuple):
    requires: List[str]
    backend: str


async def from_toml(config_file: Union[Path, IO[str]]) -> Tuple[BuildSystem, FileConf]:
    logging.debug('load config file %s', config_file)
    file_conf = toml.load(str(config_file) if isinstance(config_file, Path) else config_file)
    build_system = BuildSystem(file_conf['build-system']['requires'],
                               file_conf['build-system']['build-backend'])
    tox_config_raw = file_conf['tool']['tox3']
    return build_system, tox_config_raw
