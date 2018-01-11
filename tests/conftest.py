import asyncio
import os
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Callable, Dict, Optional, Union

import pytest

from tox3.evaluate import ToxConfig, load_config, run


class Project:

    def __init__(self, monkeypatch, root_dir: Path) -> None:
        self.root_dir: Path = root_dir
        self.conf_obj: Optional[ToxConfig] = None
        self.monkeypatch = monkeypatch

    async def conf(self, *args: str) -> ToxConfig:
        self.conf_obj = await load_config(args)
        return self.conf_obj

    async def run(self, *args: str) -> int:
        from tox3 import evaluate

        # noinspection PyShadowingNames
        async def load(args):
            self.conf_obj = await load_config(args)
            return self.conf_obj

        self.monkeypatch.setattr(evaluate, 'load_config', load)
        return await run(args)

    def clean(self):
        if self.conf_obj is not None:
            shutil.rmtree(str(self.conf_obj.work_dir))


@pytest.yield_fixture()
def event_loop():
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()  # on windows IO needs this
    else:
        loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name='project')
def project_fixture(tmpdir: Path, monkeypatch):
    _project = None

    def project_factory(files: Dict[Union[str, Path], str]):
        for file, content in files.items():
            file_path: Path = Path(tmpdir) / (Path(file) if isinstance(file, str) else file)
            dir: Path = file_path.parent
            if not dir.exists():
                os.makedirs(str(dir))
            with open(file_path, 'wt') as file_handler:
                file_handler.write(textwrap.dedent(content))
        monkeypatch.chdir(tmpdir)
        nonlocal _project
        _project = Project(monkeypatch, tmpdir)
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
