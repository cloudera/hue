import logging
import socket
from subprocess import PIPE
from subprocess import Popen
import sys
import time
import traceback

import requests

from saml2test.check import CRITICAL


logger = logging.getLogger(__name__)

__author__ = "rolandh"


class FatalError(Exception):
    pass


class CheckError(Exception):
    pass


class HTTP_ERROR(Exception):
    pass


class Unknown(Exception):
    pass


class OperationError(Exception):
    pass


class ContextFilter(logging.Filter):
    """
    This is a filter which injects time laps information into the log.
    """

    def start(self):
        self.start = time.time()

    def filter(self, record):
        record.delta = time.time() - self.start
        return True


def start_script(path, *args):
    popen_args = [path]
    popen_args.extend(args)
    return Popen(popen_args, stdout=PIPE, stderr=PIPE)


def stop_script_by_name(name):
    import os
    import signal
    import subprocess

    p = subprocess.Popen(["ps", "-A"], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if name in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)


def stop_script_by_pid(pid):
    import os
    import signal

    os.kill(pid, signal.SIGKILL)


def get_page(url):
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text
    else:
        raise HTTP_ERROR(resp.status)


def exception_trace(tag, exc, log=None):
    message = traceback.format_exception(*sys.exc_info())

    try:
        _exc = f"Exception: {exc}"
    except UnicodeEncodeError:
        _exc = f"Exception: {exc.message.encode('utf-8', 'replace')}"

    return {"status": CRITICAL, "message": _exc, "content": "".join(message)}


def ip_addresses():
    return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
