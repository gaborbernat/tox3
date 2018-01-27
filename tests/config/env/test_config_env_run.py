import pytest

from toxn.config import ToxConfig


@pytest.mark.asyncio
async def test_posargs_extraction(conf):
    env = conf('''
[tool.toxn.env.py36]
  commands = ["pytest tests <posargs>"]
''')

    conf: ToxConfig = await env.conf()
    assert conf._env('py36').commands == [['pytest', 'tests']]

    conf: ToxConfig = await env.conf('--', '-vv')
    assert conf._env('py36').commands == [['pytest', 'tests', '-vv']]

    conf: ToxConfig = await env.conf('--', '<>', '<>')
    assert conf._env('py36').commands == [['pytest', 'tests', '<>', '<>']]
