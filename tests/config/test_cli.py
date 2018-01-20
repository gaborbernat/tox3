from os import getcwd
from pathlib import Path

import pytest

from tox3.config import ToxConfig
from tox3.config.cli import TOX_ENV


@pytest.mark.parametrize('explicit', [False, True])
@pytest.mark.asyncio
async def test_project_source(conf, explicit, monkeypatch):
    monkeypatch.delenv(TOX_ENV, raising=False)
    env = conf('''''')
    args = [] if explicit is False else ['--config', str(Path(getcwd()) / 'pyproject.toml')]

    conf: ToxConfig = await env.conf(*args)

    assert conf.build.build_backend is None
    assert conf.build.build_requires == []

    assert conf.default_run_environments == []
    assert conf.environments == []
