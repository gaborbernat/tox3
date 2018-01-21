"""parse the project file"""
import logging
from pathlib import Path
from typing import Any, Dict, IO, List, NamedTuple, Optional, Tuple, Union

import toml  # type: ignore

ConfDict = Dict[str, Any]


class BuildSystem(NamedTuple):
    requires: List[str]
    backend: Optional[str]


async def from_toml(config_object: Union[Path, IO[str]]) -> Tuple[BuildSystem, ConfDict, Optional[Path]]:
    config_path: Optional[Path] = None
    if isinstance(config_object, Path):
        config_path = config_object
    else:
        name = getattr(config_object, 'name', None)
        if name:
            config_path = Path(name)

    logging.debug('load config file %s', config_path)
    file_conf = toml.load(str(config_object) if isinstance(config_object, Path) else config_object)

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

    conf_dict: ConfDict = dict()
    if 'tool' in file_conf and 'tox3' in file_conf['tool']:
        conf_dict = file_conf['tool']['tox3']
    return build_system, conf_dict, config_path
