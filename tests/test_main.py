from io import StringIO

import pytest

from tox3.__main__ import main
from tox3.config.static.cli import build_parser


def test_help(capsys):
    with pytest.raises(SystemExit) as exit:
        main(['--help'])
    assert exit.value.code == 0

    out, err = capsys.readouterr()
    assert not err
    help_message_io = StringIO()
    build_parser().print_help(help_message_io)
    assert out == help_message_io.getvalue()
