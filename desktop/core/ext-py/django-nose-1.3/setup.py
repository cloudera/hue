import os
from setuptools import setup, find_packages


ROOT = os.path.abspath(os.path.dirname(__file__))

setup(
    name='django-nose',
    version='1.3',
    description='Makes your Django tests simple and snappy',
    long_description=open(os.path.join(ROOT, 'README.rst')).read(),
    author='Jeff Balogh',
    author_email='me@jeffbalogh.org',
    maintainer='Erik Rose',
    maintainer_email='erikrose@grinchcentral.com',
    url='http://github.com/django-nose/django-nose',
    license='BSD',
    packages=find_packages(exclude=['testapp', 'testapp/*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['nose>=1.2.1', 'Django>=1.4'],
    tests_require=['south>=0.7'],
    # This blows up tox runs that install django-nose into a virtualenv,
    # because it causes Nose to import django_nose.runner before the Django
    # settings are initialized, leading to a mess of errors. There's no reason
    # we need FixtureBundlingPlugin declared as an entrypoint anyway, since you
    # need to be using django-nose to find the it useful, and django-nose knows
    # about it intrinsically.
    #entry_points="""
    #    [nose.plugins.0.10]
    #    fixture_bundler = django_nose.fixture_bundling:FixtureBundlingPlugin
    #    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing'
    ]
)
