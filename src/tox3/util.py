import asyncio
import logging


async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line.decode())
        else:
            break


async def _stream_subprocess(cmd, stdout_cb, stderr_cb):
    logging.debug('run %s', ' '.join(repr(i) for i in cmd))
    process = await asyncio.create_subprocess_exec(*cmd,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
    await asyncio.wait([
        _read_stream(process.stdout, stdout_cb),
        _read_stream(process.stderr, stderr_cb)
    ])
    return await process.wait()


def print_to_sdtout(line):
    logging.debug(line.rstrip())


def print_to_sdterr(line):
    logging.warning(line.rstrip())


async def run(cmd, stdout=print_to_sdtout, stderr=print_to_sdterr):
    result_code = await _stream_subprocess(cmd, stdout, stderr)
    return result_code
