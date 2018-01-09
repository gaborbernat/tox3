"""configuration passed via the command line or the environment variables"""
import argparse
import logging
import os
from pathlib import Path
from typing import Tuple, Sequence

import tox3
from .util import VERBOSITY_TO_LOG_LEVEL


async def parse(argv: Sequence[str]) -> argparse.Namespace:
    parser = build_parser()
    options: argparse.Namespace = parser.parse_args(argv)

    # noinspection PyUnresolvedReferences
    if isinstance(options.config, Path):
        # noinspection PyUnresolvedReferences
        options.root_dir = options.config.parents[0]
    else:
        # noinspection PyUnresolvedReferences
        options.root_dir = Path(options.config.name).parents[0]

    logging.debug('CLI flags %r', options)
    return options


class Tox3HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):

    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=35, width=200)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("tox3", formatter_class=Tox3HelpFormatter,
                                     epilog=f'{tox3.__version__} from {tox3.__file__}')
    pre_process_flags(parser)
    parser.add_argument("--version", action="store_true", dest="print_version",
                        help="report version information to stdout")
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), dest='config',
                        default=(Path(os.getcwd()) / 'pyproject.toml'), metavar='file')
    parser.add_argument("-r", "--recreate", action="store_true", dest="recreate",
                        help="force recreation of virtual environments")
    parser.add_argument('-e', '--envs', dest='environments', metavar='e',
                        help='run only this run environments', nargs="+", type=str)
    parser.add_argument("-l", "--list", action="store_true", dest="list_envs",
                        help="show list of all defined environments (with description if verbose)")
    return parser


def pre_process_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--logging', default='%(message)s',
                        help='tools logging format', dest='logging')
    levels = ', '.join('{} -> {}'.format(c, logging.getLevelName(l)) for c, l in sorted(VERBOSITY_TO_LOG_LEVEL.items()))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbosity', action='count', dest='verbose',
                       help='control log level towards stderr (may be passed multiple times - {})'.format(levels),
                       default=0)
    group.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                       help='do not print log messages')


def get_logging(argv: Sequence[str]) -> Tuple[bool, bool, str]:
    parser = argparse.ArgumentParser(add_help=False)
    pre_process_flags(parser)
    options, _ = parser.parse_known_args(argv)
    return options.verbose, options.quiet, options.logging
