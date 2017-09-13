#!/usr/bin/env python
__author__ = 'rohe0002'

#from idp_test import saml2base
from idp_test import SAML2client
from idp_test.check import factory

cli = SAML2client(factory)
cli.run()