import subprocess
import sys
from io import StringIO

from tox3.config.cli import build_parser


def test_help():
    output = subprocess.check_output([sys.executable, '-m', 'tox3', '--help'], universal_newlines=True)
    help_message_io = StringIO()
    build_parser().print_help(help_message_io)
    assert output == help_message_io.getvalue()
