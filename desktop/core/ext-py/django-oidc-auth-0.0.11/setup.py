# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='django-oidc-auth',
    version='0.0.11',
    description='OpenID Connect client for Django applications',
    long_description='WIP',
    author='Lucas S. Magalhães',
    author_email='lucas.sampaio@intelie.com.br',
    packages=find_packages(exclude=['*.tests']),
    include_package_data=True,
    install_requires=[
        'Django>=1.5',
        'South==1.0.2',
        'pyjwkest==0.6.2',
        'requests',
    ],
    zip_safe=True
)
