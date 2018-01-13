import pytest

from tox3.config import ToxConfig
from tox3.config.cli import TOX_ENV


@pytest.mark.asyncio
async def test_pytest(conf, monkeypatch):
    monkeypatch.delenv(TOX_ENV, raising=False)
    env = conf('''
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools.build_meta'

[tool.tox3]
  envlist = ['py36']

[tool.tox3.env]
  basepython = 'python3.6'

[tool.tox3.env.py36]
  deps = ["pytest"]
  description = 'run the unit tests with pytest'
  commands = ["pytest tests"]
[tool.tox3.env.dev]
  commands = [""]
''')
    conf: ToxConfig = await env.conf()

    assert conf.build.build_backend == 'setuptools.build_meta'
    assert conf.build.build_requires == ['setuptools >= 38.2.4']

    assert conf.envs == ['py36']
    assert conf.all_envs == ['py36', 'dev']

    py36 = conf.env('py36')
    assert py36.description == 'run the unit tests with pytest'
    assert py36.commands == [['pytest', 'tests']]

    dev = conf.env('dev')
    assert dev.description is None
    assert dev.commands == []
    assert dev.deps == []
