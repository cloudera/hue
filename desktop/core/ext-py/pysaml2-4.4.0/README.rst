*************************
PySAML2 - SAML2 in Python
*************************

:Author: Roland Hedberg
:Version: 4.0.4

.. image:: https://api.travis-ci.org/rohe/pysaml2.png?branch=master
    :target: https://travis-ci.org/rohe/pysaml2

.. image:: https://img.shields.io/pypi/pyversions/pysaml2.svg
    :target: https://pypi.python.org/pypi/pysaml2

.. image:: https://img.shields.io/pypi/v/pysaml2.svg
    :target: https://pypi.python.org/pypi/pysaml2

.. image:: https://img.shields.io/pypi/dm/pysaml2.svg
    :target: https://pypi.python.org/pypi/pysaml2

.. image:: https://landscape.io/github/rohe/pysaml2/master/landscape.svg?style=flat
    :target: https://landscape.io/github/rohe/pysaml2/master


PySAML2 is a pure python implementation of SAML2. It contains all
necessary pieces for building a SAML2 service provider or an identity provider.
The distribution contains examples of both.
Originally written to work in a WSGI environment there are extensions that
allow you to use it with other frameworks.

Testing
=======
PySAML2 uses the `pytest <http://doc.pytest.org/en/latest/>`_ framework for
testing. To run the tests on your system's version of python 

1. Create and activate a `virtualenv <https://virtualenv.pypa.io/en/stable/>`_.
2. Inside the virtualenv, install the dependencies needed for testing :code:`pip install -r tests/test_requirements.txt`
3. Run the tests :code:`py.test tests`

To run tests in multiple python environments, you can use
`pyenv <https://github.com/yyuu/pyenv>`_ with `tox <https://tox.readthedocs.io/en/latest/>`_.
