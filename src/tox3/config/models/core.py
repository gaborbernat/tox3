import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional, cast

from ..project import ConfDict
from ..util import Substitute


def _tox_sys_dir() -> Path:
    return Path(Path.home()) / '.tox3'


def _project_sys_dir(root_dir: Path) -> Path:
    at = 0
    temp_dir = Path(_tox_sys_dir())
    while True:
        hash = hashlib.sha256(f'{root_dir}{at}'.encode('UTF-8')).hexdigest()
        folder_name = root_dir.name[:12]
        project_id = '{}_{}'.format(folder_name, hash[:32 - len(folder_name) - 1])
        project_id_folder = temp_dir / project_id
        project_id_file = project_id_folder / '.id'
        reserved = False
        if project_id_file.exists():
            with open(project_id_file, 'rt') as file_handler:
                folder = json.load(file_handler)
                if folder != str(root_dir):
                    logging.debug('%d work dir %s already reserved for %s',  # pragma: no cover
                                  at, project_id_folder, folder)  # pragma: no cover
                    reserved = True  # pragma: no cover
        if not reserved:
            if not project_id_folder.exists():
                os.makedirs(str(project_id_folder))
                logging.debug('create work dir %s for %s', project_id_folder, root_dir)
                with open(project_id_file, 'wt') as file_handler:
                    json.dump(str(root_dir), file_handler)
            else:
                logging.debug('work dir %s for %s', project_id_folder, root_dir)
            return project_id_folder


def root_dir(cli: argparse.Namespace, work_dir: Optional[Path]) -> Path:
    if work_dir is not None:
        if not work_dir.is_absolute():
            work_dir = work_dir.absolute()
        if not work_dir.exists():
            os.makedirs(str(work_dir))
        return work_dir
    return _project_sys_dir(cast(Path, getattr(cli, 'root_dir')))


class CommonToxConfig(Substitute):
    """configuration elements present in all configuration objects"""

    def __init__(self,
                 options: argparse.Namespace,
                 file: ConfDict) -> None:
        self._cli: argparse.Namespace = options
        self._config_dict: ConfDict = file

    @property
    def root_dir(self) -> Path:
        """the root directory of the project

        :note: read only
        """
        return cast(Path, getattr(self._cli, 'root_dir'))
