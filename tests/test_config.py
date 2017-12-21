from pathlib import Path

import pytest

from tox3.config import load


@pytest.mark.asyncio
async def test_our_own_toml():
    our_own_toml = (Path(__file__).parents[1] / 'pyproject.toml').resolve()
    conf = await load(['--config', str(our_own_toml)])
    assert conf.envs == ['env']
    commands = ["python -c 'import sys; print(sys.executable)'",
                """python -c 'import os; print(\"\\n\".join(str(i) for i in os.environ.items()))'"""]
    env = conf.env('env')
    assert conf.env('env') == {'description': 'run the unit tests with pytest under {basepython}',
                               'commands': commands}
