import pytest

from toxn.config import ToxConfig


@pytest.mark.asyncio
async def test_posargs_extraction(conf):
    task = conf('''
[tool.toxn.task.py36]
  commands = ["pytest tests <posargs>"]
''')

    conf: ToxConfig = await task.conf()
    assert conf.task('py36').commands == [['pytest', 'tests']]

    conf: ToxConfig = await task.conf('--', '-vv')
    assert conf.task('py36').commands == [['pytest', 'tests', '-vv']]

    conf: ToxConfig = await task.conf('--', '<>', '<>')
    assert conf.task('py36').commands == [['pytest', 'tests', '<>', '<>']]


@pytest.mark.asyncio
async def test_posargs_extraction_default(conf):
    task = conf('''
[tool.toxn.task.py36]
  commands = ["pytest tests <posargs: -n 1>"]
''')

    conf: ToxConfig = await task.conf()
    assert conf.task('py36').commands == [['pytest', 'tests', '-n', '1']]

    conf: ToxConfig = await task.conf('--')
    assert conf.task('py36').commands == [['pytest', 'tests']]
