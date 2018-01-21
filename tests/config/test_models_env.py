import pytest

from tox3.config import ToxConfig


@pytest.mark.asyncio
async def test_recreate(conf):
    env = conf(f'''
        [tool.tox3.env.extra]
        ''')

    conf: ToxConfig = await env.conf()
    assert conf.build.recreate is False
    assert conf.env('extra').recreate is False

    conf: ToxConfig = await env.conf('-r')
    assert conf.build.recreate is True
    assert conf.env('extra').recreate is True

    conf: ToxConfig = await env.conf('--recreate')
    assert conf.build.recreate is True
    assert conf.env('extra').recreate is True


@pytest.mark.asyncio
async def test_python_custom(conf):
    env = conf(f'''
    [tool.tox3.env]
    python="magic"
    [tool.tox3.env.extra]
    ''')
    conf: ToxConfig = await env.conf()
    assert conf.build.python == 'magic'
    assert conf.env('extra').python == 'magic'


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
    [tool.tox3.env.{env_name}]
    ''')
    conf: ToxConfig = await env.conf()
    assert conf.build.python == 'python'
    assert conf.env(env_name).python == python
