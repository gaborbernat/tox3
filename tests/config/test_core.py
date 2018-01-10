import pytest

from tox3.config import ToxConfig


@pytest.mark.asyncio
async def test_conf_twice_same_work_dir(conf):
    env = conf('''''')
    conf: ToxConfig = await env.conf()
    next_conf: ToxConfig = await env.conf()
    assert conf.work_dir == next_conf.work_dir
    assert conf.work_dir.exists()


@pytest.mark.asyncio
async def test_custom_work_dir(conf):
    env = conf(f'''
    [tool.tox3]
    work_dir=".tox3"
    ''')
    conf: ToxConfig = await env.conf()
    assert conf.work_dir == conf.root_dir / '.tox3'
    assert conf.work_dir.exists()
