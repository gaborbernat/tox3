from pathlib import Path

from tox3.__main__ import main


def test_build_ourselves():
    our_own_toml = (Path(__file__).parents[1] / 'pyproject.toml').resolve()
    main(['--config', str(our_own_toml)])
