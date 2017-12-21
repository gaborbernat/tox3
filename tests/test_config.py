from pathlib import Path

from tox3.config import load_config


def test_our_own_toml():
    our_own_toml = (Path(__file__).parents[1] / 'pyproject.toml').resolve()
    conf = load_config(our_own_toml)
    assert conf.envs == ['py35', 'py36']
    assert conf.env('py35') == {'description': 'run the unit tests with pytest under {basepython}',
                                'commands': ["python -c 'print(3.5)'",
                                             'pytest']}
    assert conf.env('py36') == {'description': 'run the unit tests with pytest under {basepython}',
                                'commands': ['pytest']}
