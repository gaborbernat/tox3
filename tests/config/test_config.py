import pytest


@pytest.mark.asyncio
async def test_pytest(project):
    env = project({'pyproject.toml': '''
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools.build_meta'

[tool.tox3]
  envlist = ['py36']

[tool.tox3.env]
  basepython = 'python3.6'
  deps = ["pytest"]
  description = 'run the unit tests with pytest'

[tool.tox3.env.py36]
  commands = ["pytest tests"]
'''})
    conf = await env.conf()
    assert conf.envs == ['py36']
    py36 = conf.env('py36')
    assert py36.description == 'run the unit tests with pytest'
    assert py36.commands == ['pytest tests']
