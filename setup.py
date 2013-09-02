try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='parquet',
    version='1.0',
    description='Python support for Parquet file format',
    author='Joe Crobak',
    author_email='joecrow@gmail.com',
    packages=[ 'parquet' ],
    install_requires=[
        'thrift',
    ],
    extras_require = {
        'snappy support': ['python-snappy']
    },
    entry_points={
        'console_scripts': [
            'parquet = parquet.__main__:main',
        ]
    },
)