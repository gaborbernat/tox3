"""configuration passed via the command line or the environment variables"""
import argparse
import logging
import os
from pathlib import Path
from typing import IO, List, Sequence, Tuple, Union, cast

import configargparse  # type: ignore

import toxn

CONFIG_FILE_NAME = 'pyproject.toml'

TOX_ENV = 'TOX_ENV'
TOX_CONFIG = 'TOX_CONFIG'
OS_ENV_VARS = [TOX_ENV, TOX_CONFIG]

# actions that can be performed upon invoking tox
ACTIONS = ['run', 'list', 'list-bare', 'list-default-bare']  # actions that can be performed upon invoking tox


def level_names() -> List[str]:
    return [logging.getLevelName(x) for x in range(1, 101) if not logging.getLevelName(x).startswith('Level')]


def find_config(config: Union[None, Path, IO[str]]) -> Union[Path, IO[str]]:
    if config is not None:
        return config
    cur_dir = Path(os.getcwd()) / 'dummy'
    for parent in cur_dir.parents:
        candidate = parent / CONFIG_FILE_NAME
        if candidate.exists():
            return candidate
    raise ValueError('could not locate configuration file')


async def parse(argv: Sequence[str]) -> argparse.Namespace:
    parser = build_parser()
    options: argparse.Namespace = parser.parse_args(argv)

    options.config = find_config(getattr(options, 'config'))
    if isinstance(options.config, Path):
        options.root_dir = options.config.parents[0]
    else:
        options.root_dir = Path(options.config.name).parents[0]

    logging.debug('CLI flags %r', options)
    return options


class Tox3HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=35, width=255)


def build_parser() -> argparse.ArgumentParser:
    parser = configargparse.ArgParser("toxn", formatter_class=Tox3HelpFormatter,
                                      epilog=f'{toxn.__version__} from {toxn.__file__}')
    pre_process_flags(parser)
    parser.add_argument("--version", action="store_true", dest="print_version",
                        help="report version information to stdout")
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), dest='config',
                        default=None, metavar='file', env_var=TOX_CONFIG,
                        help='the pyproject.toml config file to use (determines the root directory)')
    parser.add_argument("-r", "--recreate", action="store_true", dest="recreate",
                        help="force recreation of virtual environments")
    parser.add_argument('-e', '--envs', dest='environments', metavar='e',
                        help='run only this run environments', nargs="+", type=str, env_var=TOX_ENV)
    parser.add_argument('args', nargs='*', help='additional arguments passed to commands as positional substitution')
    parser.add_argument('-a', '--action', choices=ACTIONS, help='action to perform once configuration loaded',
                        default='run')
    parser.add_argument('-p', '--parallel', dest='run_parallel', action="store_true",
                        help='run tox environments in parallel')
    return cast(argparse.ArgumentParser, parser)


def pre_process_flags(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbosity', type=str, dest='verbose',
                       help='stderr output log level', choices=level_names(),
                       default=logging.getLevelName(logging.INFO))
    group.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                       help='do not print log messages')
    parser.add_argument('--logging', default='%(message)s',
                        help='logging format, '
                             'see https://docs.python.org/3/library/logging.html#logrecord-attributes',
                        dest='logging')


def get_logging(argv: Sequence[str]) -> Tuple[str, bool, str]:
    parser = argparse.ArgumentParser(add_help=False)
    pre_process_flags(parser)
    options, _ = parser.parse_known_args(argv)
    return options.verbose, options.quiet, options.logging
