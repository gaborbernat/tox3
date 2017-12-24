from pathlib import Path

import pytest

from tox3.config import load


@pytest.mark.asyncio
async def test_our_own_toml():
    our_own_toml = (Path(__file__).parents[2] / 'pyproject.toml').resolve()
    conf = await load(['--config', str(our_own_toml)])
    assert conf.envs == ['py36']
    py36 = conf.env('py36')
    assert py36.description == 'run the unit tests with pytest under {basepython}'
    assert py36.commands == ['pytest tests']
