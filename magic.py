from pathlib import Path

from tox3.__main__ import main

if __name__ == '__main__':
    our_own_toml = (Path(__file__).parents[0] / 'pyproject.toml').resolve()
    result = main(['-vvv', '--config', str(our_own_toml)])
