.. _example_idp:

An extremly simple example of a SAML2 identity provider.
========================================================

There are 2 example IDPs in the project's example directory:
* idp2 has a static definition of users:
 * user attributes are defined in idp_user.py
 * the password is defined in the PASSWD dict in idp.py
* idp2_repoze is using repoze.who middleware to perform authentication and attribute retrieval

Configuration
-------------
Entity configuration is described in "Configuration of pysaml2 entities"
Server parameters like host and port and various command line parameters are
defined in the main part of idp.py

Setup:
******

The folder [your path]/pysaml2/example/idp2 contains a file named idp_conf.py.example

Take the file named idp_conf.py.example and rename it idp_conf.py

Generate a metadata file based in the configuration file (idp_conf.py) by using the command::

    make_metadata.py idp_conf.py > idp.xml


Run IDP:
********

Open a Terminal::

    cd [your path]/pysaml2/example/idp2
    python idp.py idp_conf

Note that you should not have the .py extension on the idp_conf.py while running the program
