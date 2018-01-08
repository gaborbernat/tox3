import os
from pathlib import Path
from typing import Dict, Callable

import pytest

from tox3.evaluate import run, load_config, ToxConfig


class Project:

    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir

    async def conf(self, *args: str) -> ToxConfig:
        return await load_config(args)

    async def run(self, *args: str) -> int:
        return await run(args)


@pytest.fixture(name='project')
def project_fixture(tmpdir: Path, monkeypatch):
    def project_factory(files: Dict[Path, str]):
        for file, content in files.items():
            file_path: Path = Path(tmpdir / file)
            dir: Path = file_path.parent
            if not dir.exists():
                os.makedirs(str(dir))
            with open(file_path, 'wt') as file_handler:
                file_handler.write(content)
        monkeypatch.chdir(tmpdir)
        return Project(tmpdir)

    return project_factory


@pytest.fixture(name='conf')
def conf_fixture(project) -> Callable[[str], Project]:
    def conf_factory(conf: str) -> Project:
        return project(files={'pyproject.toml': conf})

    return conf_factory
