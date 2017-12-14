#!/usr/bin/env python
from setuptools import setup

setup(
    name='djangomako',
    version='1.0.1',
    packages=['djangomako'],
    install_requires=['Mako==1.0.7'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url='https://github.com/ahmedaljazzar/django-mako',
    license='MIT License',
    author='Ahmed Jazzar',
    author_email='me@ahmedjazzar.com',
    description='The simple, elegant Django Mako library',
)
