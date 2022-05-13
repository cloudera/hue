from setuptools import setup, find_packages
from io import open

setup(
    name='django-debug-toolbar',
    version='1.3.2',
    description='A configurable set of panels that display various debug '
                'information about the current request/response.',
    long_description=open('README.rst', encoding='utf-8').read(),
    author='Rob Hudson',
    author_email='rob@cogit8.org',
    url='https://github.com/django-debug-toolbar/django-debug-toolbar',
    download_url='https://pypi.python.org/pypi/django-debug-toolbar',
    license='BSD',
    packages=find_packages(exclude=('tests.*', 'tests', 'example')),
    install_requires=[
        'django>=1.4.2',
        'sqlparse',
    ],
    include_package_data=True,
    zip_safe=False,                 # because we're including static files
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
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
