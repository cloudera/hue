#!/bin/sh
rm -f saml2*
sphinx-apidoc -F -o ../docs/ ../src/saml2
make clean
make html
