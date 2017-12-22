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
    parser = argparse.ArgumentParser("tox3")
    pre_process_flags(parser)
    parser.add_argument('--config', type=argparse.FileType('r'), default=None)
    parser.add_argument('-r', '--recreate', action='store_true', default=False,
                        help='recreate the virtual environmentF')
    parser.add_argument('-e', '--environments', help='run only this run environments', nargs="+", type=str)
    args = parser.parse_args(args)

    if args.config is None:
        args.config = Path(os.getcwd()) / 'pyproject.toml'
    logging.debug('CLI flags %r', args)
    return args


def pre_process_flags(parser):
    levels = ', '.join('{} -> {}'.format(c, logging.getLevelName(l)) for c, l in sorted(VERBOSITY_TO_LOG_LEVEL.items()))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbosity', action='count', dest='verbose',
                       help='control log level towards stderr (may be passed multiple times - {})'.format(levels),
                       default=0)
    group.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                       help='do not print log messages')


def get_verbose(argv):
    parser = argparse.ArgumentParser(add_help=False)
    pre_process_flags(parser)
    options, _ = parser.parse_known_args(argv)
    return options.verbose, options.quiet
