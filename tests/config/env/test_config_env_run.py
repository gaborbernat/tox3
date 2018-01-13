import pytest

from tox3.config import ToxConfig


@pytest.mark.asyncio
async def test_posargs_extraction(conf):
    env = conf('''
[tool.tox3.env.py36]
  commands = ["pytest tests <posargs>"]
''')

    conf: ToxConfig = await env.conf()
    assert conf.env('py36').commands == [['pytest', 'tests']]

    conf: ToxConfig = await env.conf('--', '-vv')
    assert conf.env('py36').commands == [['pytest', 'tests', '-vv']]

    conf: ToxConfig = await env.conf('--', '<>', '<>')
    assert conf.env('py36').commands == [['pytest', 'tests', '<>', '<>']]
