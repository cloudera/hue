import re
from os import path
from setuptools import setup


# read() and find_version() taken from jezdez's python apps, ex:
# https://github.com/jezdez/django_compressor/blob/develop/setup.py


def read(*parts):
    return open(path.join(path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-timezone-field',
    version=find_version('timezone_field', '__init__.py'),
    author='Mike Fogel',
    author_email='mike@fogel.ca',
    description=(
        'A Django app providing database and form fields for '
        'pytz timezone objects.'
    ),
    long_description=read('README.rst'),
    url='http://github.com/mfogel/django-timezone-field/',
    license='BSD',
    packages=[
        'timezone_field',
    ],
    install_requires=['django>=1.8', 'pytz'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'Framework :: Django',
    ],
)
