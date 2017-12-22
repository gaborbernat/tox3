import asyncio
import json
import logging
from collections import deque
from functools import partial

import sys


async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line=line.decode())
        else:
            break


async def _stream_subprocess(cmd, stdout_cb, stderr_cb, env, shell=False):
    if shell:
        runner = partial(asyncio.create_subprocess_shell, cmd)
        shell_cmd = cmd
    else:
        runner = partial(asyncio.create_subprocess_exec, *cmd)
        shell_cmd = ' '.join(repr(i) for i in cmd)

    logging.debug('run %s%s', shell_cmd, ' as shell command' if shell else '')
    process = await runner(stdout=asyncio.subprocess.PIPE,
                           stderr=asyncio.subprocess.PIPE,
                           env=env)
    await asyncio.wait([
        _read_stream(process.stdout, stdout_cb),
        _read_stream(process.stderr, stderr_cb)
    ])
    return await process.wait()


def print_to_sdtout(line, level=logging.DEBUG):
    logging.log(level, line.rstrip())


def print_to_sdterr(line, level=logging.DEBUG):
    logging.log(level, line.rstrip())


async def run(cmd, stdout=print_to_sdtout, stderr=print_to_sdterr, env=None, shell=False):
    if shell is False:
        cmd = [i if isinstance(i, str) else str(i) for i in cmd]
    result_code = await _stream_subprocess(cmd, stdout, stderr, env=env, shell=shell)
    return result_code


class Buffer:

    def __init__(self, limit=None, live_print=True):
        self.live_print = live_print
        self.elements = deque(maxlen=limit)

    def __call__(self, line):
        self.elements.append(line.rstrip())
        if self.live_print:
            print_to_sdtout(line)

    @property
    def json(self):
        return json.loads(self.last)

    @property
    def last(self):
        last = self.elements.pop()
        self.elements.append(last)
        return last
