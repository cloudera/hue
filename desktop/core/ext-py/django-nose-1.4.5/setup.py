"""django-nose packaging."""
from __future__ import unicode_literals
import os
from codecs import open
from setuptools import setup, find_packages


def get_long_description(title):
    """Create the long_description from other files."""
    ROOT = os.path.abspath(os.path.dirname(__file__))

    readme = open(os.path.join(ROOT, 'README.rst'), 'r', 'utf8').read()
    body_tag = ".. Omit badges from docs"
    readme_body_start = readme.index(body_tag)
    assert readme_body_start
    readme_body = readme[readme_body_start + len(body_tag):]

    changelog = open(os.path.join(ROOT, 'changelog.rst'), 'r', 'utf8').read()
    old_tag = ".. Omit older changes from package"
    changelog_body_end = changelog.index(old_tag)
    assert changelog_body_end
    changelog_body = changelog[:changelog_body_end]

    bars = '=' * len(title)
    long_description = """
%(bars)s
%(title)s
%(bars)s
%(readme_body)s

%(changelog_body)s

_(Older changes can be found in the full documentation)._
""" % locals()
    return long_description


setup(
    name='django-nose',
    version='1.4.5',
    description='Makes your Django tests simple and snappy',
    long_description=get_long_description('django-nose'),
    author='Jeff Balogh',
    author_email='me@jeffbalogh.org',
    maintainer='Erik Rose',
    maintainer_email='erikrose@grinchcentral.com',
    url='http://github.com/django-nose/django-nose',
    license='BSD',
    packages=find_packages(exclude=['testapp', 'testapp/*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['nose>=1.2.1'],
    test_suite='testapp.runtests.runtests',
    # This blows up tox runs that install django-nose into a virtualenv,
    # because it causes Nose to import django_nose.runner before the Django
    # settings are initialized, leading to a mess of errors. There's no reason
    # we need FixtureBundlingPlugin declared as an entrypoint anyway, since you
    # need to be using django-nose to find the it useful, and django-nose knows
    # about it intrinsically.
    # entry_points="""
    #    [nose.plugins.0.10]
    #    fixture_bundler = django_nose.fixture_bundling:FixtureBundlingPlugin
    #    """,
    keywords='django nose django-nose',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing'
    ]
)
