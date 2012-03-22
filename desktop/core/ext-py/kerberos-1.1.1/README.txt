=========================================================
PyKerberos Package

Copyright (c) 2006-2008 Apple Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

=========================================================

This Python package is a high-level wrapper for Kerberos (GSSAPI) operations.
The goal is to avoid having to build a module that wraps the entire Kerberos.framework,
and instead offer a limited set of functions that do what is needed for client/server
Kerberos authentication based on <http://www.ietf.org/rfc/rfc4559.txt>.

Much of the C-code here is adapted from Apache's mod_auth_kerb-5.0rc7.

========
CONTENTS
========

    src/               : directory in which C source code resides.
    setup.py           : Python distutils extension build script.
    config/            : directory of useful Kerberos config files.
      edu.mit.Kerberos : example Kerberos .ini file.
    README.txt         : this file!
    kerberos.py        : Python api documentation/stub implementation.

=====
BUILD
=====

In this directory, run:

    python setup.py build

=======
TESTING
=======

You must have a valid Kerberos setup on the test machine and you should ensure that you have valid
Kerberos tickets for any client authentication being done (run 'klist' on the command line).
Additionally, for the server: it must have been configured as a valid Kerberos service with the Kerbersos server
for its realm - this usually requires running kadmin on the server machine to add the principal and generate a keytab
entry for it (run 'sudo klist -k' to see the currently available keytab entries).

Make sure that PYTHONPATH includes the appropriate build/lib.xxxx directory.
Then run test.py with suitable command line arguments:

    python test.py -u userid -p password -s service
    
    -u : user id for basic authenticate
    -p : password for basic authenticate
    -s : service principal for GSSAPI authentication (defaults to 'http@host.example.com')

===========
Python APIs
===========

See kerberos.py.
