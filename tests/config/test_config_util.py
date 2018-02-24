from os import getcwd
from pathlib import Path

import pytest

from toxn.config import ToxConfig
from toxn.config.util import substitute


@pytest.mark.asyncio
async def test_work_dir_root_dir(conf):
    env = conf('''
    [tool.toxn]
    work_dir = ".tox"
    default_tasks = ["<root_dir>", "<work_dir>"]
    ''')
    conf: ToxConfig = await env.conf()

    cwd = Path(getcwd())
    assert conf.work_dir == cwd / '.tox'

    assert conf.tasks == [str(conf.root_dir), str(conf.work_dir)]


@pytest.mark.asyncio
async def test_substitute_env_invalid():
    assert substitute(None, '<env>') == '<env>'


@pytest.mark.asyncio
async def test_substitute_env_key(monkeypatch):
    monkeypatch.setenv('FOOBAR', '1')
    assert substitute(None, '<env:FOOBAR>') == '1'


@pytest.mark.asyncio
async def test_substitute_env_key_default(monkeypatch):
    monkeypatch.delenv('FOOBAR', raising=False)
    assert substitute(None, '<env:FOOBAR:2>') == '2'


@pytest.mark.asyncio
async def test_substitute_env_key_no_default(monkeypatch):
    monkeypatch.delenv('FOOBAR', raising=False)
    assert substitute(None, '<env:FOOBAR>') == ''
