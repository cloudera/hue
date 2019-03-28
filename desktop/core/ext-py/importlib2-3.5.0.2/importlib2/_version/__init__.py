"""importlib2 version (and helpers)."""

import os.path


DATA_DIR = os.path.abspath(os.path.dirname(__file__))


# Where the actual importlib2 "version" is stored:
RELEASE_FILE = os.path.join(DATA_DIR, 'RELEASE')

# The Python on which importlib2 is based (set by pull_cpython.py in
# the "clean-cpython" branch):
PY_VERSION_FILE = os.path.join(DATA_DIR, 'ORIGINAL_PY_VERSION')
PY_REVISION_FILE = os.path.join(DATA_DIR, 'ORIGINAL_PY_REVISION')


#################################################
# generate the actual version string

# See http://www.python.org/dev/peps/pep-0440/#public-version-identifiers.

with open(PY_VERSION_FILE) as _py_version_file:
    PY_VERSION = _py_version_file.read().strip()
with open(RELEASE_FILE) as _release_file:
    RELEASE = _release_file.read().strip()
VERSION = '{}.{}'.format(PY_VERSION, RELEASE)
