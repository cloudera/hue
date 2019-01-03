import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

__sdesc = 'Python PAM module using ctypes, py3/py2'

setup(name             = 'python-pam',
      description      =  __sdesc,
      long_description = read('README.md'),
      py_modules       = ['pam'],
      version          = '1.8.4',
      author           = 'David Ford',
      author_email     = 'david@blue-labs.org',
      maintainer       = 'David Ford',
      maintainer_email = 'david@blue-labs.org',
      url              = 'https://github.com/FirefighterBlu3/python-pam',
      download_url     = 'https://github.com/FirefighterBlu3/python-pam',
      license          = 'License :: OSI Approved :: MIT License',
      platforms        = ['i686','x86_64'],
      classifiers      = [
          'Development Status :: 6 - Mature',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Security',
          'Topic :: System :: Systems Administration :: Authentication/Directory',
          ],
      )
