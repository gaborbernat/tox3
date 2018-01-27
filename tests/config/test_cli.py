from contextlib import contextmanager
from os import getcwd
from pathlib import Path

import pytest

from toxn.config import ToxConfig
from toxn.config.cli import TOX_CONFIG


@contextmanager
def cli_conf(opt: ToxConfig):
    yield opt
    assert opt.build.build_backend is None
    assert opt.build.build_requires == []

    assert opt.default_run_environments == []
    assert opt.environments == []


@pytest.mark.asyncio
async def test_implicit_config_path(conf):
    env = conf('''''')
    config_path = Path(getcwd()) / 'pyproject.toml'
    with cli_conf(await env.conf()) as opt:
        assert opt.config_path == config_path


@pytest.mark.asyncio
async def test_implicit_config_path_children(conf, monkeypatch):
    env = conf('''''')
    cwd = Path(getcwd())
    config_path = Path(cwd) / 'pyproject.toml'
    child = (cwd / 'tmp')
    child.mkdir()
    monkeypatch.chdir(child)
    with cli_conf(await env.conf('--config', str(config_path))) as opt:
        assert opt.config_path == config_path


@pytest.mark.asyncio
async def test_set_config_path_env_from_root(conf, monkeypatch):
    env = conf('''''')
    cwd = Path(getcwd())
    config_path = Path(cwd) / 'pyproject.toml'
    monkeypatch.chdir(cwd.parts[0])
    monkeypatch.setenv(TOX_CONFIG, str(config_path))
    with cli_conf(await env.conf()) as opt:
        assert opt.config_path == config_path


@pytest.mark.asyncio
async def test_set_config_path_cli_from_root(conf, monkeypatch):
    env = conf('''''')
    cwd = Path(getcwd())
    config_path = Path(cwd) / 'pyproject.toml'
    monkeypatch.chdir(cwd.parts[0])
    with cli_conf(await env.conf('--config', str(config_path))) as opt:
        assert opt.config_path == config_path


@pytest.mark.asyncio
async def test_root_no_config_found(conf, monkeypatch):
    env = conf('''''')
    monkeypatch.chdir(Path(getcwd()).parts[0])
    with pytest.raises(ValueError) as error:
        await env.conf()
    assert error.value.args[0] == 'could not locate configuration file'
