import argparse
import sys
import venv
from typing import List

from tox3.config import load_config, Config


def create_install_package(config: Config):
    build_dir = config.workdir / '.build'
    env_dir = build_dir / 'env'
    venv.create(env_dir, with_pip=True)




def main(args: List[str]):
    parser = argparse.ArgumentParser("tox3")
    parser.add_argument('--config', type=argparse.FileType('r'))
    args = parser.parse_args(args)
    config = load_config(args.config)
    create_install_package(config)
    print('')
    for env_name in config.envs:
        print(f'{env_name} => {config.env(env_name)}')


def build_package():
    pass


if __name__ == '__main__':
    main(sys.argv[1])
