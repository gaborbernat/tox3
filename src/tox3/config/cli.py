import argparse
import logging
import os
from pathlib import Path
from typing import List

VERBOSITY_TO_LOG_LEVEL = {0: logging.ERROR,
                          1: logging.WARN,
                          2: logging.INFO,
                          3: logging.DEBUG}


def parse(args: List[str]):
    parser = build_parser()
    args = parser.parse_args(args)
    logging.debug('CLI flags %r', args)
    return args


def build_parser():
    parser = argparse.ArgumentParser("tox3")
    pre_process_flags(parser)
    parser.add_argument("--version", action="store_true", dest="print_version",
                        help="report version information to stdout")
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), dest='config',
                        default=(Path(os.getcwd()) / 'pyproject.toml'))
    parser.add_argument("-r", "--recreate", action="store_true", dest="recreate",
                        help="force recreation of virtual environments")
    parser.add_argument('-e', '--environments', help='run only this run environments', nargs="+", type=str)
    parser.add_argument("-l", "--list", action="store_true", dest="list_envs",
                        help="show list of all defined environments (with description if verbose)")
    return parser


def pre_process_flags(parser):
    parser.add_argument('--logging', default='%(levelname)s %(message)s',
                        help='tools logging format', dest='logging')
    levels = ', '.join('{} -> {}'.format(c, logging.getLevelName(l)) for c, l in sorted(VERBOSITY_TO_LOG_LEVEL.items()))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbosity', action='count', dest='verbose',
                       help='control log level towards stderr (may be passed multiple times - {})'.format(levels),
                       default=0)
    group.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                       help='do not print log messages')


def get_logging(argv):
    parser = argparse.ArgumentParser(add_help=False)
    pre_process_flags(parser)
    options, _ = parser.parse_known_args(argv)
    return options.verbose, options.quiet, options.logging
