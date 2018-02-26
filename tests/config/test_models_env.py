import pytest

from toxn.config import ToxConfig


@pytest.mark.asyncio
async def test_recreate(conf):
    env = conf(f'''
        [tool.toxn.task.extra]
        ''')

    conf: ToxConfig = await env.conf()
    assert conf.build.recreate is False
    assert conf.task_of('extra').recreate is False

    conf: ToxConfig = await env.conf('-r')
    assert conf.build.recreate is True
    assert conf.task_of('extra').recreate is True

    conf: ToxConfig = await env.conf('--recreate')
    assert conf.build.recreate is True
    assert conf.task_of('extra').recreate is True


@pytest.mark.asyncio
async def test_python_custom(conf):
    env = conf(f'''
    [tool.toxn.task]
    python="magic"
    [tool.toxn.task.extra]
    ''')
    conf: ToxConfig = await env.conf()
    assert conf.build.python_requires == 'magic'
    assert conf.task_of('extra').python_requires == 'magic'


@pytest.mark.parametrize('env_name, python', [
    ('py27', 'python2.7'),
    ('py36', 'python3.6'),
    ('py310', 'python3.10'),
    ('py2', 'python2'),
    ('py3', 'python3'),
    ('py', 'python'),
])
@pytest.mark.asyncio
async def test_python_implicit(conf, env_name, python):
    env = conf(f'''
    [tool.toxn.task.{env_name}]
    ''')
    conf: ToxConfig = await env.conf()
    assert conf.build.python_requires == 'python'
    assert conf.task_of(env_name).python_requires == python
