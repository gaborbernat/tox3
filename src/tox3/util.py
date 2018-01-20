import asyncio
import json
import logging
import shlex
import shutil
import subprocess
import sys
from collections import deque
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any, Callable, Deque, Iterable, List, Mapping, Optional, Union, cast

Cmd = Iterable[Union[str, Path]]
Loggers = Union[logging.LoggerAdapter, logging.Logger]


class CmdLineBufferPrinter:

    def __init__(self, limit: Optional[int] = None, live_print: bool = True) -> None:
        self.live_print: bool = live_print
        self.elements: Deque[str] = deque(maxlen=limit) if limit is not None else deque()

    def __call__(self, logger: Loggers, line: str) -> None:
        self.elements.append(line.rstrip())
        if self.live_print:
            print_to_sdtout(logger, line)

    @property
    def json(self) -> Any:
        return json.loads(self.last)

    @property
    def last(self) -> str:
        last = self.elements.pop()
        self.elements.append(last)
        return last


StreamCallback = Union[Callable[[Loggers, str], Any], CmdLineBufferPrinter]


async def _read_stream(stream: Optional[asyncio.streams.StreamReader],
                       logger: Loggers,
                       callback: StreamCallback) -> None:
    if stream is not None:
        while True:
            line = await stream.readline()
            if line:
                callback(logger, line.decode())
            else:
                break


async def _stream_subprocess(cmd: List[str], logger: Loggers,
                             stdout_cb: StreamCallback, stderr_cb: StreamCallback,
                             env: Optional[Mapping[str, str]], shell: bool = False) -> int:
    shell_cmd = list_to_cmd(cmd)
    if shell:
        runner = partial(asyncio.create_subprocess_shell, shell_cmd)
    else:
        runner = partial(asyncio.create_subprocess_exec, *cmd)

    logger.debug('[run] %s%s', shell_cmd, ' as shell command' if shell else '')
    start = datetime.now()
    process = await runner(stdout=asyncio.subprocess.PIPE,
                           stderr=asyncio.subprocess.PIPE,
                           stdin=None,
                           env=env)
    handlers = [_read_stream(process.stdout, logger, stdout_cb),
                _read_stream(process.stderr, logger, stderr_cb)]
    await asyncio.wait(handlers)
    result_repr: Optional[str] = None
    try:
        result = await process.wait()
        result_repr = repr(result)
        return result
    except BaseException as e:
        result_repr = repr(e)
        raise
    finally:
        end = datetime.now()
        logger.debug('[ran] in %s with %s %s%s', end - start,
                     result_repr, shell_cmd, ' as shell command' if shell else '')


def print_to_sdtout(logger: Loggers, line: str, level: int = logging.DEBUG) -> None:
    logger.log(level, line.rstrip())


def print_to_sdterr(logger: Loggers, line: str, level: int = logging.DEBUG) -> None:
    logger.log(level, line.rstrip())


async def run(cmd: Cmd, logger: Loggers,
              stdout: StreamCallback = print_to_sdtout, stderr: StreamCallback = print_to_sdterr,
              env: Optional[Mapping[str, str]] = None, shell: bool = False, exit_on_fail: bool = True) -> int:
    if logger is None:
        logging.getLogger()
    type_safe_cmd: List[str] = [i if isinstance(i, str) else str(i) for i in cmd]
    result_code = await _stream_subprocess(type_safe_cmd, logger, stdout, stderr, env=env, shell=shell)
    if exit_on_fail and result_code != 0:
        raise SystemExit(-1)
    return result_code


def rm_dir(folder: Path, msg: str, logger: Loggers) -> None:
    if folder.exists():
        logger.debug('%s => remove %r', msg, folder)
        shutil.rmtree(str(folder))


def list_to_cmd(args: List[str]) -> str:
    if sys.platform == 'win32':
        converter = subprocess.list2cmdline
        package_list = cast(str, converter(args))
    else:
        package_list = ' '.join(shlex.quote(arg) for arg in args)
    return package_list


def human_timedelta(arg: timedelta) -> str:
    result = ''
    if arg.days:
        result += f' {timedelta.days} days'
    result += f' {arg.seconds}.{arg.microseconds} seconds'
    return result[1:]
