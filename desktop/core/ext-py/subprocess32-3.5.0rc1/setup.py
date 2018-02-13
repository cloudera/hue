#!/usr/bin/env python2

import os
import sys
from setuptools import setup, Extension


def main():
    ext_modules = []
    py_modules = []
    packages = []
    package_dir = {}
    if sys.version_info[0] == 2:  # PY2
        py_modules.append('subprocess32')
        if os.name == 'posix':
            ext = Extension('_posixsubprocess', ['_posixsubprocess.c'],
                            depends=['_posixsubprocess_helpers.c'])
            ext_modules.append(ext)
    else:  # PY3
        # Install a redirect that makes subprocess32 == subprocess on import.
        packages.append('subprocess32')
        package_dir['subprocess32'] = 'python3_redirect'
        sys.stderr.write('subprocess32 == subprocess on Python 3.\n')

    setup(
      name='subprocess32',
      version='3.5.0rc1',
      description='A backport of the subprocess module from Python 3 for use on 2.x.',
      long_description="""\
This is a backport of the subprocess standard library module from
Python 3.2 - 3.5 for use on Python 2.

It includes bugfixes and some new features.  On POSIX systems it is
guaranteed to be reliable when used in threaded applications.
It includes timeout support from Python 3.3 and the run() API from 3.5
but otherwise matches 3.2's API.

It has not been tested by the author on Windows.

On Python 3, it merely redirects the subprocess32 name to subprocess.""",
      license='PSF license',

      maintainer='Gregory P. Smith',
      maintainer_email='greg@krypto.org',
      url='https://github.com/google/python-subprocess32',

      ext_modules=ext_modules,
      py_modules=py_modules,
      packages=packages,
      package_dir=package_dir,

      # We don't actually "support" 3.3+, we just allow installation there as
      # we install a stub redirecting to the standard library subprocess module
      # under the subprocess32 name.
      python_requires='>=2.4, !=3.0.*, !=3.1.*, !=3.2.*, <4',

      classifiers=[
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: BSD',
          'Operating System :: POSIX :: Linux',
          'Operating System :: POSIX :: SunOS/Solaris',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',
      ],
    )


if __name__ == '__main__':
    main()
