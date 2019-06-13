from __future__ import print_function

import os
import sys
import glob

import setuptools
import setuptools.command.test

from distutils import sysconfig
from distutils.errors import (
    CCompilerError,
    DistutilsExecError,
    DistutilsPlatformError
)
HERE = os.path.dirname(os.path.abspath(__file__))

ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)
if sys.platform == 'win32' and sys.version_info >= (2, 6):
    # distutils.msvc9compiler can raise IOError if the compiler is missing
    ext_errors += (IOError, )

is_jython = sys.platform.startswith('java')
is_pypy = hasattr(sys, 'pypy_version_info')
is_py3k = sys.version_info[0] == 3

BUILD_WARNING = """

-----------------------------------------------------------------------
WARNING: The C extensions could not be compiled
-----------------------------------------------------------------------

Maybe you do not have a C compiler installed on this system?
The reason was:
%s

This is just a warning as most of the functionality will work even
without the updated C extension.  It will simply fallback to the
built-in _multiprocessing module.  Most notably you will not be able to use
FORCE_EXECV on POSIX systems.  If this is a problem for you then please
install a C compiler or fix the error(s) above.
-----------------------------------------------------------------------

"""

# -*- py3k -*-
extras = {}

# -*- Distribution Meta -*-

import re
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
re_doc = re.compile(r'^"""(.+?)"""')
rq = lambda s: s.strip("\"'")


def add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)), )


def add_version(m):
    v = list(map(rq, m.groups()[0].split(', ')))
    return (('VERSION', '.'.join(v[0:4]) + ''.join(v[4:])), )


def add_doc(m):
    return (('doc', m.groups()[0]), )

pats = {re_meta: add_default,
        re_vers: add_version,
        re_doc: add_doc}
here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, 'billiard/__init__.py'))
try:
    meta = {}
    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()


if sys.version_info < (2, 7):
    raise ValueError('Versions of Python before 2.7 are not supported')

if sys.platform == 'win32':  # Windows
    macros = dict()
    libraries = ['ws2_32']
elif sys.platform.startswith('darwin'):  # macOS
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=0,
        HAVE_FD_TRANSFER=1,
        HAVE_BROKEN_SEM_GETVALUE=1
    )
    libraries = []
elif sys.platform.startswith('cygwin'):  # Cygwin
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=1,
        HAVE_FD_TRANSFER=0,
        HAVE_BROKEN_SEM_UNLINK=1
    )
    libraries = []
elif sys.platform in ('freebsd4', 'freebsd5', 'freebsd6'):
    # FreeBSD's P1003.1b semaphore support is very experimental
    # and has many known problems. (as of June 2008)
    macros = dict(                  # FreeBSD 4-6
        HAVE_SEM_OPEN=0,
        HAVE_SEM_TIMEDWAIT=0,
        HAVE_FD_TRANSFER=1,
    )
    libraries = []
elif re.match('^(gnukfreebsd(8|9|10|11)|freebsd(7|8|9|0))', sys.platform):
    macros = dict(                  # FreeBSD 7+ and GNU/kFreeBSD 8+
        HAVE_SEM_OPEN=bool(
            sysconfig.get_config_var('HAVE_SEM_OPEN') and not
            bool(sysconfig.get_config_var('POSIX_SEMAPHORES_NOT_ENABLED'))
        ),
        HAVE_SEM_TIMEDWAIT=1,
        HAVE_FD_TRANSFER=1,
    )
    libraries = []
elif sys.platform.startswith('openbsd'):
    macros = dict(                  # OpenBSD
        HAVE_SEM_OPEN=0,            # Not implemented
        HAVE_SEM_TIMEDWAIT=0,
        HAVE_FD_TRANSFER=1,
    )
    libraries = []
else:                                   # Linux and other unices
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=1,
        HAVE_FD_TRANSFER=1,
    )
    libraries = ['rt']

if sys.platform == 'win32':
    multiprocessing_srcs = [
        'Modules/_billiard/multiprocessing.c',
        'Modules/_billiard/semaphore.c',
        'Modules/_billiard/win32_functions.c',
    ]
else:
    multiprocessing_srcs = [
        'Modules/_billiard/multiprocessing.c',
    ]

    if macros.get('HAVE_SEM_OPEN', False):
        multiprocessing_srcs.append('Modules/_billiard/semaphore.c')

long_description = open(os.path.join(HERE, 'README.rst')).read()

# -*- Installation Requires -*-

py_version = sys.version_info
is_jython = sys.platform.startswith('java')
is_pypy = hasattr(sys, 'pypy_version_info')


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), 'requirements', f)).readlines()]))


def _is_build_command(argv=sys.argv, cmds=('install', 'build', 'bdist')):
    for arg in argv:
        if arg.startswith(cmds):
            return arg


class pytest(setuptools.command.test.test):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        setuptools.command.test.test.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.pytest_args))


def run_setup(with_extensions=True):
    extensions = []
    if with_extensions:
        extensions = [
            setuptools.Extension(
                '_billiard',
                sources=multiprocessing_srcs,
                define_macros=macros.items(),
                libraries=libraries,
                include_dirs=['Modules/_billiard'],
                depends=glob.glob('Modules/_billiard/*.h') + ['setup.py'],
            ),
        ]
        if sys.platform == 'win32':
            extensions.append(
                setuptools.Extension(
                    '_winapi',
                    sources=multiprocessing_srcs,
                    define_macros=macros.items(),
                    libraries=libraries,
                    include_dirs=['Modules/_billiard'],
                    depends=glob.glob('Modules/_billiard/*.h') + ['setup.py'],
                ),
            )
    packages = setuptools.find_packages(exclude=['ez_setup', 't', 't.*'])
    setuptools.setup(
        name='billiard',
        version=meta['VERSION'],
        description=meta['doc'],
        long_description=long_description,
        packages=packages,
        ext_modules=extensions,
        author=meta['author'],
        author_email=meta['author_email'],
        keywords='multiprocessing pool process',
        maintainer=meta['maintainer'],
        maintainer_email=meta['contact'],
        url=meta['homepage'],
        zip_safe=False,
        license='BSD',
        tests_require=reqs('test.txt'),
        cmdclass={'test': pytest},
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: C',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: Jython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'License :: OSI Approved :: BSD License',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Distributed Computing',
        ],
        **extras
    )

try:
    run_setup(not (is_jython or is_pypy or is_py3k))
except BaseException:
    if _is_build_command(sys.argv):
        import traceback
        print(BUILD_WARNING % '\n'.join(traceback.format_stack()),
              file=sys.stderr)
        run_setup(False)
    else:
        raise
