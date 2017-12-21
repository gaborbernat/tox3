import argparse
import os
import subprocess
import sys
import venv
from typing import List

from tox3.config import load_config, Config


class EnvB(venv.EnvBuilder):
    executable = None

    def post_setup(self, context):
        self.executable = context.env_exe


def _run(args):
    process = subprocess.Popen(args,
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(line)
    for line in iter(process.stderr.readline, b''):
        sys.stderr.write(line)
    process.communicate()


def create_install_package(config: Config):
    build_dir = config.workdir / '.build'
    env_dir = build_dir / 'env'
    out_dir = build_dir / 'dist'
    venv.create(env_dir, with_pip=True)
    env_build = EnvB(with_pip=True)
    env_build.create(env_dir)
    _run([env_build.executable, '-m', 'pip', 'install', *config.build_requires])
    SCRIPT = f'import {config.build_backend} as build; build.build_wheel("{str(out_dir)}")'

    cwd = os.getcwd()
    try:
        os.chdir(config.root_dir)
        _run([env_build.executable, '-c', SCRIPT])
    finally:
        os.chdir(cwd)


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
