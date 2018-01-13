"""parse the project file"""
import logging
from pathlib import Path
from typing import Any, Dict, IO, List, NamedTuple, Optional, Tuple, Union

import toml  # type: ignore

FileConf = Dict[str, Any]


class BuildSystem(NamedTuple):
    requires: List[str]
    backend: Optional[str]


async def from_toml(config_file: Union[Path, IO[str]]) -> Tuple[BuildSystem, FileConf]:
    logging.debug('load config file %s', config_file)
    file_conf = toml.load(str(config_file) if isinstance(config_file, Path) else config_file)

    build_backend: Optional[str] = None
    build_requires: List[str] = []
    build_system = file_conf.get('build-system')
    if isinstance(build_system, dict):
        requires = build_system.get('requires')
        if isinstance(requires, list) and all(isinstance(i, str) for i in requires):
            build_requires = requires
        backend = build_system.get('build-backend')
        if isinstance(backend, str):
            build_backend = backend
    build_system = BuildSystem(build_requires, build_backend)

    tox_config_raw: Dict[str, Any] = dict()
    if 'tool' in file_conf and 'tox3' in file_conf['tool']:
        tox_config_raw = file_conf['tool']['tox3']
    return build_system, tox_config_raw
