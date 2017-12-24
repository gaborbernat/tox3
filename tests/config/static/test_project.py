from typing import TextIO

import pytest

from tox3.config import from_toml


@pytest.mark.asyncio
async def load_from_io():
    content = TextIO("""
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools:build_meta'

[tool.tox3]
  envlist = ['py36']
""")
    build, project = await from_toml(content)
    assert build.backend == 'setuptools:build_meta'
    assert build.requires == ['setuptools >= 38.2.4']
    assert project == {'envlist': ['py36']}
