try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os

DOC_DIR = 'doc'
DIST_DIR = 'dist'
# For Python 3 compatibility, we can't use execfile; this is 2to3's conversion:
exec(compile(open("src/py4j/version.py").read(),
     "src/py4j/version.py", 'exec'))
VERSION = __version__  # noqa
RELEASE = 'py4j-' + VERSION
JAR_FILE = 'py4j' + VERSION + '.jar'
# Note: please do "ant python-light-release" before doing setup.py sdist.
# Otherwise the jar files won't be created
JAR_FILE_PATH = os.path.join('py4j-java', JAR_FILE)

setup(
    name="py4j",
    packages=['py4j', 'py4j.tests'],
    package_dir={'': 'src'},
    data_files=[('share/py4j', [JAR_FILE_PATH])],
    version=VERSION,
    description='Enables Python programs to dynamically access arbitrary '
                'Java objects',
    long_description='Py4J enables Python programs running in a Python '
                     'interpreter to dynamically '
                     'access Java objects in a Java Virtual Machine. '
                     'Methods are called as if the Java '
                     'objects resided in the Python interpreter and Java '
                     'collections can be accessed '
                     'through standard Python collection methods. Py4J also '
                     'enables Java programs to call back Python objects.',
    url="https://www.py4j.org/",
    author="Barthelemy Dagenais",
    author_email="barthelemy@infobart.com",
    license="BSD License",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Java',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Object Brokering',
    ],
)
