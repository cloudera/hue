#!/usr/bin/env python

"""
setup.py file for SWIG example
"""

from setuptools import setup, Extension

sasl_module = Extension('_saslwrapper',
                           sources=['sasl/saslwrapper.cpp', "sasl/saslwrapper_wrap.cxx"],
                           include_dirs=["sasl"],
                           libraries=["sasl2"],
                           language="c++",
                           )
dist = setup (name = 'sasl',
       version = '0.1.1',
       url = "http://github.com/toddlipcon/python-sasl/tree/master",
       maintainer = "Todd Lipcon",
       maintainer_email = "todd@cloudera.com",
       description = """Cyrus-SASL bindings for Python""",
       ext_modules = [sasl_module],
       py_modules = ["sasl.saslwrapper"],
       include_package_data = True,
       )

