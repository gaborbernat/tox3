from os import getcwd
from pathlib import Path

import pytest

from tox3.config import ToxConfig


@pytest.mark.asyncio
async def test_work_dir_root_dir(conf):
    env = conf('''
    [tool.tox3]
    work_dir = ".tox"
    envlist = ["<root_dir>", "<work_dir>"]
    
    ''')
    conf: ToxConfig = await env.conf()

    cwd = Path(getcwd())
    assert conf.work_dir == cwd / '.tox'

    assert conf.environments == [str(conf.root_dir), str(conf.work_dir)]
