"""setup.py - build script for parquet-python."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='parquet',
    version='1.3.1',
    description='Python support for Parquet file format',
    long_description_content_type="text/x-rst",
    long_description=readme,
    author='Joe Crobak',
    author_email='joecrow@gmail.com',
    url='https://github.com/jcrobak/parquet-python',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=['parquet'],
    install_requires=[
        'thriftpy2',
    ],
    extras_require={
        ':python_version=="2.7"': [
            "backports.csv",
        ],
        'snappy': [
            'python-snappy',
        ],
    },
    entry_points={
        'console_scripts': [
            'parquet = parquet.__main__:main',
        ]
    },
    package_data={'parquet': ['*.thrift']},
    include_package_data=True,
)
