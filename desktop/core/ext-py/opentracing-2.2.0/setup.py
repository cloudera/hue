from setuptools import setup


setup(
    name='opentracing',
    version='2.2.0',
    author='The OpenTracing Authors',
    author_email='opentracing@googlegroups.com',
    description='OpenTracing API for Python. See documentation at http://opentracing.io',
    long_description='\n'+open('README.rst').read(),
    license='Apache License 2.0',
    url='https://github.com/opentracing/opentracing-python',
    keywords=['opentracing'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['opentracing'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    extras_require={
        'tests': [
            'doubles',
            'flake8',
            'flake8-quotes',
            'mock',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'Sphinx',
            'sphinx_rtd_theme',

            'six>=1.10.0,<2.0',
            'gevent',
            'tornado<6',
        ],
        ':python_version == "2.7"': ['futures'],
    },
)
