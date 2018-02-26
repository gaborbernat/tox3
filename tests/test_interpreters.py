import logging
import sys

import pytest

from toxn.task.interpreters import Requirement, find_interpreter


def test_existing_interpreters():
    req = Requirement('python == 3')  # some Python 3
    req = Requirement('python == 3.6')  # exactly Python 3.6.0 or later
    req = Requirement('python >=  3.7.0a+4')  # at least alpha four for Python 3.7
    req = Requirement('python <3')  # less than Python 3
    req = Requirement('python <3, >= 2.6, != 2.7.12')  # 2.6 <= python < 3, but not 2.7.12
    req = Requirement('pypy <3')  # less than pypy 3


@pytest.mark.asyncio
async def test_file_url_interpreter_works():
    requirement = Requirement(f"python@file://localhost{sys.executable}; python=='2.7'")
    python = await find_interpreter(requirement, logging.getLogger())
    assert str(python.exe) == sys.executable
    assert python.version_info == sys.version_info
    assert python.version == sys.version
