from io import StringIO

import pytest

from tox3.evaluate import main
from tox3.config.cli import build_parser


def test_help(capsys):
    code = main(['--help'])
    assert code == 0

    out, err = capsys.readouterr()
    assert not err
    help_message_io = StringIO()
    build_parser().print_help(help_message_io)
    assert out == help_message_io.getvalue()
