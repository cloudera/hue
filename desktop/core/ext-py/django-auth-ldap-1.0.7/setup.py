#!/usr/bin/env python

from setuptools import setup

setup(
    name="django-auth-ldap",
    version="1.0.7",
    description="Django LDAP authentication backend",
    long_description="""This is a Django authentication backend that authenticates against an LDAP service. Configuration can be as simple as a single distinguished name template, but there are many rich configuration options for working with users, groups, and permissions.
    
This package requires at least Python 2.3, Django 1.0, and python-ldap 2.0. Documentation can be found at http://packages.python.org/django-auth-ldap/.
    """,
    url="http://bitbucket.org/psagers/django-auth-ldap/",
    author="Peter Sagerson",
    author_email="psagers_pypi@ignorare.net",
    license="BSD",
    packages=["django_auth_ldap"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["django", "ldap", "authentication", "auth"],
)
