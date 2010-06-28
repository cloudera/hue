#
# Imports
#

import os
import sys
import glob

from distutils.core import setup, Extension

if sys.version_info < (2, 4, 0):
    raise ValueError, 'Versions of Python before 2.4 are not supported'

#
# Macros and libraries
#
#   The `macros` dict determines the macros that will be defined when
#   the C extension is compiled.  Each value should be either 0 or 1.
#   (An undefined macro is assumed to have value 0.)  `macros` is only
#   used on Unix platforms.
#
#   The `libraries` dict determines the libraries to which the C
#   extension will be linked.  This should probably be either `['rt']`
#   if you need `librt` or else `[]`.
#
# Meaning of macros
#
#   HAVE_SEM_OPEN
#     Set this to 1 if you have `sem_open()`.  This enables the use of
#     posix named semaphores which are necessary for the
#     implementation of the synchronization primitives on Unix.  If
#     set to 0 then the only way to create synchronization primitives
#     will be via a manager (e.g. "m = Manager(); lock = m.Lock()").
#     
#   HAVE_SEM_TIMEDWAIT
#     Set this to 1 if you have `sem_timedwait()`.  Otherwise polling
#     will be necessary when waiting on a semaphore using a timeout.
#     
#   HAVE_FD_TRANSFER
#     Set this to 1 to compile functions for transferring file
#     descriptors between processes over an AF_UNIX socket using a
#     control message with type SCM_RIGHTS.  On Unix the pickling of 
#     of socket and connection objects depends on this feature.
#
#     If you get errors about missing CMSG_* macros then you should
#     set this to 0.
# 
#   HAVE_BROKEN_SEM_GETVALUE
#     Set to 1 if `sem_getvalue()` does not work or is unavailable.
#     On Mac OSX it seems to return -1 with message "[Errno 78]
#     Function not implemented".
#
#   HAVE_BROKEN_SEM_UNLINK
#     Set to 1 if `sem_unlink()` is unnecessary.  For some reason this
#     seems to be the case on Cygwin where `sem_unlink()` is missing
#     from semaphore.h.
#

if sys.platform == 'win32':             # Windows
    macros = dict()
    libraries = ['ws2_32']
    
elif sys.platform == 'darwin':          # Mac OSX
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=0,
        HAVE_FD_TRANSFER=1,
        HAVE_BROKEN_SEM_GETVALUE=1
        )
    libraries = []

elif sys.platform == 'cygwin':          # Cygwin
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=1,
        HAVE_FD_TRANSFER=0,
        HAVE_BROKEN_SEM_UNLINK=1
        )
    libraries = []
    
else:                                   # Linux and other unices
    macros = dict(
        HAVE_SEM_OPEN=1,
        HAVE_SEM_TIMEDWAIT=1,
        HAVE_FD_TRANSFER=1
        )
    libraries = ['rt']

#macros['Py_DEBUG'] = 1

#
# Print configuration info
#

print 'Macros:'

for name, value in sorted(macros.iteritems()):
    print '\t%s = %r' % (name, value)

print '\nLibraries:\n\t%r\n' % libraries

#
# Compilation of `_processing` extension
#

if sys.platform == 'win32':
    sources = [
        'src/processing.c',
        'src/semaphore.c',
        'src/pipe_connection.c',
        'src/socket_connection.c',
        'src/win_functions.c'
        ]

else:
    sources = [
        'src/processing.c',
        'src/socket_connection.c'
        ]

    if macros.get('HAVE_SEM_OPEN', False):
        sources.append('src/semaphore.c')

ext_modules = [
    Extension(
        'processing._processing',
        sources=sources,
        libraries=libraries,
        define_macros=macros.items(),
        depends=glob.glob('src/*.h') + ['setup.py']
        )
    ]

#
# Get version number
#

for line in open('lib/__init__.py'):
    if line.startswith('__version__'):
        version = line.split()[-1].strip("'").strip('"')
        break
else:
    raise ValueError, '"__version__" not found in "__init__.py"'

#
# Get `long_description` from `README.txt`
#

readme = open('README.txt', 'rU').read()
start_string = ':Licence:       BSD Licence\n\n'
end_string = '.. raw:: html'
start = readme.index(start_string) + len(start_string)
end = readme.index(end_string)
readme = readme[start:end]
long_description = readme.replace('<./', '<http://pyprocessing.berlios.de/')

#
# Packages
#

packages = [
    'processing',
    'processing.dummy',
    ]

package_dir = {
    'processing': 'lib',
    'processing.doc': 'doc',
    'processing.tests': 'tests',
    'processing.examples': 'examples'
    }

package_data = {
    'processing.doc': ['*.html', '*.css', '../*.html']
    }

INSTALL_EXTRA = True

if INSTALL_EXTRA:
    # install test files and html documentation
    packages.extend([
        'processing.tests',
        'processing.examples',
        'processing.doc'
        ])

#
# Setup
#

setup(
    name='processing',
    version=version,
    description=('Package for using processes which mimics ' +
                 'the threading module'),
    long_description=long_description,
    packages=packages,
    package_dir=package_dir,
    package_data=package_data,
    ext_modules=ext_modules,
    author='R Oudkerk',
    author_email='roudkerk at users.berlios.de',
    url='http://developer.berlios.de/projects/pyprocessing',
    license='BSD Licence',
    platforms='Unix and Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ]
    )

#
# Check for ctypes
#

try:
    import ctypes
except ImportError:
    print >>sys.stderr, '''
WARNING: ctypes is not available which means that the use of shared
memory for storing data will not be supported.  (ctypes is not
included with Python 2.4, but can be intsalled separately.)
'''
