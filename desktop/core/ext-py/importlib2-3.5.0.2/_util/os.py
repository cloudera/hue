from __future__ import absolute_import

from contextlib import contextmanager
import os
import os.path


def suffix(path):
    return os.path.splitext(path)[-1]


# XXX Build into a DirStack class.
def pushd(dirname):
    cwd = os.getcwd()
    os.chdir(dirname)
    @contextmanager
    def restore():
        try:
            yield cwd
        finally:
            os.chdir(cwd)
    return restore()
