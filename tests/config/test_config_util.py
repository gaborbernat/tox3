from os import getcwd
from pathlib import Path

import pytest

from toxn.config import ToxConfig


@pytest.mark.asyncio
async def test_work_dir_root_dir(conf):
    env = conf('''
    [tool.toxn]
    work_dir = ".tox"
    envlist = ["<root_dir>", "<work_dir>"]
    
    ''')
    conf: ToxConfig = await env.conf()

    cwd = Path(getcwd())
    assert conf.work_dir == cwd / '.tox'

    assert conf.tasks == [str(conf.root_dir), str(conf.work_dir)]
