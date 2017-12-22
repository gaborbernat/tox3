import asyncio
import json
import logging
from collections import deque
from functools import partial


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
    result_code = await _stream_subprocess(cmd, stdout, stderr, env=env, shell=shell)
    return result_code


class PrintAndKeepLastLine:

    def __init__(self, limit):
        self.elements = deque(maxlen=limit)

    def __call__(self, line):
        self.elements.append(line.rstrip())
        print_to_sdtout(line)

    @property
    def json(self):
        return json.loads(self.last)

    @property
    def last(self):
        last = self.elements.pop()
        self.elements.append(last)
        return last
