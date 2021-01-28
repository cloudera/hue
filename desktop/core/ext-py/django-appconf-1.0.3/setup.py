import codecs
import re
from os import path
from setuptools import setup


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-appconf',
    version=find_version('appconf', '__init__.py'),
    description='A helper class for handling configuration defaults '
                'of packaged apps gracefully.',
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    license='BSD',
    url='https://django-appconf.readthedocs.io/',
    packages=['appconf'],
    install_requires=['django', 'six'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
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
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    project_urls={
        'Source': 'https://github.com/django-compressor/django-appconf',
    }
)
