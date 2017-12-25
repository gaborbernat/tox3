import asyncio
import json
import logging
import shutil
from collections import deque
from datetime import datetime
from functools import partial
from pathlib import Path


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
    start = datetime.now()
    process = await runner(stdout=asyncio.subprocess.PIPE,
                           stderr=asyncio.subprocess.PIPE,
                           env=env)
    await asyncio.wait([
        _read_stream(process.stdout, stdout_cb),
        _read_stream(process.stderr, stderr_cb)
    ])
    result = None
    try:
        result = await process.wait()
        return result
    except BaseException as e:
        result = e
        raise
    finally:
        end = datetime.now()
        logging.debug('ran in %s with %r %s%s', end - start,
                      result, shell_cmd, ' as shell command' if shell else '')


def print_to_sdtout(line, level=logging.DEBUG):
    logging.log(level, line.rstrip())


def print_to_sdterr(line, level=logging.DEBUG):
    logging.log(level, line.rstrip())


async def run(cmd, stdout=print_to_sdtout, stderr=print_to_sdterr, env=None, shell=False, exit_on_fail=True):
    if shell is False:
        cmd = [i if isinstance(i, str) else str(i) for i in cmd]
    result_code = await _stream_subprocess(cmd, stdout, stderr, env=env, shell=shell)
    if exit_on_fail and result_code != 0:
        raise SystemExit(-1)
    return result_code


class CmdLineBufferPrinter:

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


def rm_dir(folder: Path, msg: str) -> None:
    if folder.exists():
        logging.debug('%s => remove %r', msg, folder)
        shutil.rmtree(str(folder))
