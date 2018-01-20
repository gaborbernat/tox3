"""configuration passed via the command line or the environment variables"""
import argparse
import logging
import os
from pathlib import Path
from typing import IO, List, Sequence, Tuple, Union, cast

import configargparse  # type: ignore

import tox3

CONFIG_FILE_NAME = 'pyproject.toml'
TOX_ENV = 'TOX_ENV'


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
        super().__init__(prog, max_help_position=35, width=200)


def build_parser() -> argparse.ArgumentParser:
    parser = configargparse.ArgParser("tox3", formatter_class=Tox3HelpFormatter,
                                      epilog=f'{tox3.__version__} from {tox3.__file__}')
    pre_process_flags(parser)
    parser.add_argument("--version", action="store_true", dest="print_version",
                        help="report version information to stdout")
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), dest='config',
                        default=None, metavar='file', env_var='TOX_CONFIG')
    parser.add_argument("-r", "--recreate", action="store_true", dest="recreate",
                        help="force recreation of virtual environments")
    parser.add_argument('-e', '--envs', dest='environments', metavar='e',
                        help='run only this run environments', nargs="+", type=str, env_var=TOX_ENV)
    parser.add_argument("-l", "--list", action="store_true", dest="list_envs",
                        help="show list of all defined environments (with description if verbose)")
    parser.add_argument('args', nargs='*', help='additional arguments available to command positional substitution')
    return cast(argparse.ArgumentParser, parser)


def pre_process_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--logging', default='%(message)s',
                        help='tools logging format', dest='logging')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbosity', type=str, dest='verbose',
                       help='control log level towards stderr', choices=level_names(),
                       default=logging.getLevelName(logging.INFO))
    group.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                       help='do not print log messages')


def get_logging(argv: Sequence[str]) -> Tuple[str, bool, str]:
    parser = argparse.ArgumentParser(add_help=False)
    pre_process_flags(parser)
    options, _ = parser.parse_known_args(argv)
    return options.verbose, options.quiet, options.logging
