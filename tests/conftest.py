import asyncio
import os
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Callable, Dict, Optional, Union

import pytest

from toxn.config.cli import OS_ENV_VARS
from toxn.evaluate import ToxConfig, get_event_loop, load_config, execute


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "network: tests that require network access")
    config.addinivalue_line("markers", "venv: tests that require virtual environment creation")


@pytest.yield_fixture()
def event_loop():
    """pytest-asyncio customization"""
    if sys.platform != "win32":
        asyncio.set_event_loop(None)  # see https://github.com/pytest-dev/pytest-asyncio/issues/73
    loop = get_event_loop()
    if sys.platform != "win32":
        # on UNIX we also need to attach the loop to the child watcher for asyncio.subprocess
        policy = asyncio.get_event_loop_policy()
        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(loop)
        policy.set_child_watcher(watcher)
    try:
        yield loop
    finally:
        loop.close()


class Project:

    def __init__(self, monkeypatch, root_dir: Path) -> None:
        self.root_dir: Path = root_dir
        self.conf_obj: Optional[ToxConfig] = None
        self.monkeypatch = monkeypatch

    async def conf(self, *args: str) -> ToxConfig:
        self.conf_obj = await load_config(args)
        return self.conf_obj

    async def run(self, *args: str) -> int:
        from toxn import evaluate

        # noinspection PyShadowingNames
        async def load(args):
            self.conf_obj = await load_config(args)
            return self.conf_obj

        self.monkeypatch.setattr(evaluate, 'load_config', load)
        return await execute(args)

    def clean(self):
        if self.conf_obj is not None:
            shutil.rmtree(str(self.conf_obj.work_dir))


@pytest.fixture(name='project')
def project_fixture(tmpdir: Path, monkeypatch):
    _project = None

    def project_factory(files: Dict[Union[str, Path], str]):
        for file, content in files.items():
            file_path: Path = Path(tmpdir) / (Path(file) if isinstance(file, str) else file)
            folder: Path = file_path.parent
            if not folder.exists():
                os.makedirs(str(folder))
            with open(file_path, 'wt') as file_handler:
                file_handler.write(textwrap.dedent(content))
        monkeypatch.chdir(tmpdir)
        nonlocal _project
        for var in OS_ENV_VARS:
            monkeypatch.delenv(var, raising=False)  # yeah don't use parents config
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
