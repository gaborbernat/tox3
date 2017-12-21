from pathlib import Path

from tox3.__main__ import main


def test_build_ourselves():
    our_own_toml = (Path(__file__).parents[1] / 'pyproject.toml').resolve()
    result = main(['-vvv', '--config', str(our_own_toml)])
    assert result == 0
