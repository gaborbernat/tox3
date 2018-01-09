import os
from pathlib import Path
import shutil
from typing import Callable, Dict, Optional

import pytest

from tox3.evaluate import ToxConfig, load_config, run


class Project:

    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir
        self.conf_obj: Optional[ToxConfig] = None

    async def conf(self, *args: str) -> ToxConfig:
        self.conf_obj = await load_config(args)
        return self.conf_obj

    async def run(self, *args: str) -> int:
        return await run(args)

    def clean(self):
        if self.conf_obj is not None:
            shutil.rmtree(str(self.conf_obj.work_dir))


@pytest.fixture(name='project')
def project_fixture(tmpdir: Path, monkeypatch):
    _project = None

    def project_factory(files: Dict[Path, str]):
        for file, content in files.items():
            file_path: Path = Path(tmpdir / file)
            dir: Path = file_path.parent
            if not dir.exists():
                os.makedirs(str(dir))
            with open(file_path, 'wt') as file_handler:
                file_handler.write(content)
        monkeypatch.chdir(tmpdir)
        nonlocal _project
        _project = Project(tmpdir)
        return _project

    try:
        yield project_factory
    finally:
        if _project is not None:
            _project.clean()


@pytest.fixture(name='conf')
def conf_fixture(project) -> Callable[[str], Project]:
    def conf_factory(conf: str) -> Project:
        return project(files={'pyproject.toml': conf})

    return conf_factory
