from os import getcwd
from pathlib import Path

import pytest

from tox3.config import ToxConfig


@pytest.mark.parametrize('explicit', [False, True])
@pytest.mark.asyncio
async def test_project_source(conf, explicit, monkeypatch):
    monkeypatch.delenv('TOXENV', raising=False)
    env = conf('''''')
    args = [] if explicit is False else ['--config', str(Path(getcwd()) / 'pyproject.toml')]

    conf: ToxConfig = await env.conf(*args)

    assert conf.build.build_backend is None
    assert conf.build.build_requires == []

    assert conf.envs == []
    assert conf.all_envs == []
