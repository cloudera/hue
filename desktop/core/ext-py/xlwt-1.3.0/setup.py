import os
from setuptools import setup, find_packages
from xlwt import __VERSION__

DESCRIPTION = (
    'Library to create spreadsheet files compatible with '
    'MS Excel 97/2000/XP/2003 XLS files, '
    'on any platform, with Python 2.6, 2.7, 3.3+'
    )

CLASSIFIERS = [
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'License :: OSI Approved :: BSD License',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Office/Business :: Financial :: Spreadsheet',
    'Topic :: Database',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    ]

KEYWORDS = (
    'xls excel spreadsheet workbook worksheet pyExcelerator'
    )

setup(
    name='xlwt',
    version=__VERSION__,
    maintainer='John Machin',
    maintainer_email='sjmachin@lexicon.net',
    url='http://www.python-excel.org/',
    download_url='https://pypi.python.org/pypi/xlwt',
    description=DESCRIPTION,
    long_description=open(os.path.join(
        os.path.dirname(__file__), 'README.rst')
    ).read(),
    license='BSD',
    platforms='Platform Independent',
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True
)
