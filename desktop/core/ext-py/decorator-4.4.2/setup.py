from setuptools import setup

dic = dict(__file__=None)
exec(open('src/decorator.py').read(), dic)  # extract the __version__
VERSION = dic['__version__']


if __name__ == '__main__':
    setup(name='decorator',
          version=VERSION,
          description='Decorators for Humans',
          long_description=open('README.rst').read(),
          author='Michele Simionato',
          author_email='michele.simionato@gmail.com',
          url='https://github.com/micheles/decorator',
          license="new BSD License",
          package_dir={'': 'src'},
          py_modules=['decorator'],
          keywords="decorators generic utility",
          platforms=["All"],
          python_requires='>=2.6, !=3.0.*, !=3.1.*',
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 2',
                       'Programming Language :: Python :: 2.6',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 3',
                       'Programming Language :: Python :: 3.2',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Programming Language :: Python :: Implementation :: CPython',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
          test_suite='tests',
          zip_safe=False)
