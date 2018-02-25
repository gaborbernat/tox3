import pytest

from toxn.config import ToxConfig


@pytest.mark.asyncio
async def test_pytest(conf):
    env = conf('''
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools.build_meta'

[tool.toxn]
default_tasks = ['py36']

[tool.toxn.task]
python = 'python3.6'

[tool.toxn.task.py36]
deps = ["pytest"]
description = 'run the unit tests with pytest'
commands = ["pytest tests"]

[tool.toxn.task.dev]
commands = [""]
''')
    conf: ToxConfig = await env.conf()

    assert conf.build.build_backend == 'setuptools.build_meta'
    assert conf.build.build_requires == ['setuptools >= 38.2.4']

    assert conf.default_tasks == ['py36']
    assert conf.tasks == ['py36', 'dev']

    py36 = conf.task_of('py36')
    assert py36.description == 'run the unit tests with pytest'
    assert py36.commands == [['pytest', 'tests']]

    dev = conf.task_of('dev')
    assert dev.description is None
    assert dev.commands == []
    assert dev.deps == []


@pytest.mark.asyncio
async def test_refer_to_task(conf):
    env = conf('''
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools.build_meta'

[tool.toxn.task.py36]
deps = ["pytest"]
description = 'run the unit tests with pytest'
commands = ["pytest tests"]

[tool.toxn.task.py27]
deps = "<task.py36.deps>"
''')
    conf: ToxConfig = await env.conf()
    py27 = conf.task_of('py27')
    py36 = conf.task_of('py36')
    left = py27.deps
    right = py36.deps
    assert left == right
