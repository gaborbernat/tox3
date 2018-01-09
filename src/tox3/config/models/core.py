import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional, cast

from ..project import BuildSystem, FileConf
from ..util import Substitute


def _tox_sys_dir() -> Path:
    return Path(Path.home()) / '.tox3'


def _project_sys_dir(root_dir: Path) -> Path:
    at = 0
    temp_dir = Path(_tox_sys_dir())
    while True:
        project_id = hashlib.sha256(f'{root_dir}{at}'.encode('UTF-8')).hexdigest()[:32]
        project_id_folder = temp_dir / project_id
        project_id_file = project_id_folder / '.id'
        reserved = False
        if project_id_file.exists():
            with open(project_id_file, 'rt') as file_handler:
                folder = json.load(file_handler)
                if folder != str(root_dir):
                    logging.debug('%d work dir %s already reserved for %s', at, project_id_folder, folder)
                    reserved = True
        if not reserved:
            if not project_id_folder.exists():
                os.makedirs(str(project_id_folder))
                logging.debug('create work dir %s for %s', project_id_folder, root_dir)
                with open(project_id_file, 'wt') as file_handler:
                    json.dump(str(root_dir), file_handler)
            else:
                logging.debug('work dir %s for %s', project_id_folder, root_dir)
            return project_id_folder


def root_dir(options: argparse.Namespace, work_dir: Optional[Path]) -> Path:
    if work_dir is not None and work_dir.exists():
        return work_dir
    return _project_sys_dir(cast(Path, options.__getattribute__('root_dir')))


class CoreToxConfig(Substitute):

    def __init__(self,
                 options: argparse.Namespace,
                 build_system: BuildSystem,
                 file: FileConf,
                 work_dir: Path) -> None:
        self._options: argparse.Namespace = options
        self._file: FileConf = file
        self._build_system: BuildSystem = build_system
        self._work_dir = work_dir

    @property
    def root_dir(self) -> Path:
        return cast(Path, self._options.__getattribute__('root_dir'))

    @property
    def work_dir(self) -> Path:
        return self._work_dir
