# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from sphinx_celery import conf

globals().update(conf.build_config(
    'amqp', __file__,
    project='py-amqp',
    description='Python Promises',
    version_dev='2.4',
    version_stable='2.3',
    canonical_url='https://amqp.readthedocs.io',
    webdomain='celeryproject.org',
    github_project='celery/py-amqp',
    author='Ask Solem & contributors',
    author_name='Ask Solem',
    copyright='2016',
    publisher='Celery Project',
    html_logo='images/celery_128.png',
    html_favicon='images/favicon.ico',
    html_prepend_sidebars=['sidebardonations.html'],
    extra_extensions=[],
    include_intersphinx={'python', 'sphinx'},
    apicheck_package='amqp',
    apicheck_ignore_modules=['amqp'],
))
