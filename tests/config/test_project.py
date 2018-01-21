from io import StringIO
from pathlib import Path

import pytest

from tox3.config import from_toml


@pytest.mark.asyncio
async def test_load_from_io():
    content = StringIO("""
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools:build_meta'

[tool.tox3]
  envlist = ['py36']
""")
    build, project, filename = await from_toml(content)
    assert build.backend == 'setuptools:build_meta'
    assert build.requires == ['setuptools >= 38.2.4']
    assert project == {'envlist': ['py36']}
    assert filename is None


@pytest.mark.asyncio
async def test_load_from_path(tmpdir):
    filename: Path = Path(tmpdir) / 'test.toml'
    with open(filename, 'wt') as f:
        f.write("""
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools:build_meta'

[tool.tox3]
  envlist = ['py36']
""")
    build, project, config_path = await from_toml(filename)
    assert build.backend == 'setuptools:build_meta'
    assert build.requires == ['setuptools >= 38.2.4']
    assert project == {'envlist': ['py36']}
    assert filename == config_path
