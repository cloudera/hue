#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) AB Strakt 2001, All rights reserved
# Copyright (C) Jean-Paul Calderone 2008-2010, All rights reserved
#

"""
Installation script for the OpenSSL module
"""

import sys, os
from distutils.core import Extension, setup
from distutils.errors import DistutilsFileError
from distutils.command.build_ext import build_ext

# XXX Deduplicate this
__version__ = '0.13'

crypto_src = ['OpenSSL/crypto/crypto.c', 'OpenSSL/crypto/x509.c',
              'OpenSSL/crypto/x509name.c', 'OpenSSL/crypto/pkey.c',
              'OpenSSL/crypto/x509store.c', 'OpenSSL/crypto/x509req.c',
              'OpenSSL/crypto/x509ext.c', 'OpenSSL/crypto/pkcs7.c',
              'OpenSSL/crypto/pkcs12.c', 'OpenSSL/crypto/netscape_spki.c',
              'OpenSSL/crypto/revoked.c', 'OpenSSL/crypto/crl.c',
              'OpenSSL/util.c']
crypto_dep = ['OpenSSL/crypto/crypto.h', 'OpenSSL/crypto/x509.h',
              'OpenSSL/crypto/x509name.h', 'OpenSSL/crypto/pkey.h',
              'OpenSSL/crypto/x509store.h', 'OpenSSL/crypto/x509req.h',
              'OpenSSL/crypto/x509ext.h', 'OpenSSL/crypto/pkcs7.h',
              'OpenSSL/crypto/pkcs12.h', 'OpenSSL/crypto/netscape_spki.h',
              'OpenSSL/crypto/revoked.h', 'OpenSSL/crypto/crl.h',
              'OpenSSL/util.h']
rand_src = ['OpenSSL/rand/rand.c', 'OpenSSL/util.c']
rand_dep = ['OpenSSL/util.h']
ssl_src = ['OpenSSL/ssl/connection.c', 'OpenSSL/ssl/context.c', 'OpenSSL/ssl/ssl.c',
           'OpenSSL/util.c']
ssl_dep = ['OpenSSL/ssl/connection.h', 'OpenSSL/ssl/context.h', 'OpenSSL/ssl/ssl.h',
           'OpenSSL/util.h']

IncludeDirs = None
LibraryDirs = None

# Add more platforms here when needed
if os.name == 'nt' or sys.platform == 'win32':

    Libraries = ['Ws2_32']



    class BuildExtension(build_ext):
        """
        A custom command that semiautomatically finds dependencies required by
        PyOpenSSL.
        """

        user_options = (build_ext.user_options +
                        [("with-openssl=", None,
                          "directory where OpenSSL is installed")])
        with_openssl = None
        openssl_dlls = ()
        openssl_mingw = False


        def finalize_options(self):
            """
            Update build options with details about OpenSSL.
            """
            build_ext.finalize_options(self)
            if self.with_openssl is None:
                self.find_openssl()
            self.find_openssl_dlls()
            self.add_openssl_compile_info()


        def find_openssl(self):
            """
            Find OpenSSL's install directory.
            """
            potentials = []
            dirs = os.environ.get("PATH").split(os.pathsep)
            for d in dirs:
                if os.path.exists(os.path.join(d, "openssl.exe")):
                    ssldir, bin = os.path.split(d)
                    if not bin:
                        ssldir, bin = os.path.split(ssldir)
                    potentials.append(ssldir)
                    childdirs = os.listdir(ssldir)
                    if "lib" in childdirs and "include" in childdirs:
                        self.with_openssl = ssldir
                        return
            if potentials:
                raise DistutilsFileError(
                    "Only found improper OpenSSL directories: %r" % (
                        potentials,))
            else:
                raise DistutilsFileError("Could not find 'openssl.exe'")


        def find_openssl_dlls(self):
            """
            Find OpenSSL's shared libraries.
            """
            self.openssl_dlls = []
            self.find_openssl_dll("libssl32.dll", False)
            if self.openssl_dlls:
                self.openssl_mingw = True
            else:
                self.find_openssl_dll("ssleay32.dll", True)
            self.find_openssl_dll("libeay32.dll", True)
            # add zlib to the mix if it looks like OpenSSL
            # was linked with a private copy of it
            self.find_openssl_dll("zlib1.dll", False)


        def find_openssl_dll(self, name, required):
            """
            Find OpenSSL's shared library and its path after installation.
            """
            dllpath = os.path.join(self.with_openssl, "bin", name)
            if not os.path.exists(dllpath):
                if required:
                    raise DistutilsFileError("could not find '%s'" % name)
                else:
                    return
            newpath = os.path.join(self.build_lib, "OpenSSL", name)
            self.openssl_dlls.append((dllpath, newpath))


        def add_openssl_compile_info(self):
            """
            Set up various compile and link parameters.
            """
            if self.compiler == "mingw32":
                if self.openssl_mingw:
                    # Library path and library names are sane when OpenSSL is
                    # built with MinGW .
                    libdir = "lib"
                    libs = ["eay32", "ssl32"]
                else:
                    libdir = ""
                    libs = []
                    # Unlike when using the binary installer, which creates
                    # an atypical shared library name 'ssleay32', so we have
                    # to use this workaround.
                    if self.link_objects is None:
                        self.link_objects = []
                    for dllpath, _ in self.openssl_dlls:
                        dllname = os.path.basename(dllpath)
                        libname = os.path.splitext(dllname)[0] + ".a"
                        libpath = os.path.join(self.with_openssl,
                                               "lib", "MinGW", libname)
                        self.link_objects.append(libpath)
            else:
                libdir = "lib"
                libs = ["libeay32", "ssleay32"]
            self.include_dirs.append(os.path.join(self.with_openssl, "include"))
            self.library_dirs.append(os.path.join(self.with_openssl, libdir))
            self.libraries.extend(libs)


        def run(self):
            """
            Build extension modules and copy shared libraries.
            """
            build_ext.run(self)
            for dllpath, newpath in self.openssl_dlls:
                self.copy_file(dllpath, newpath)


        def get_outputs(self):
            """
            Return a list of file paths built by this comand.
            """
            output = [pathpair[1] for pathpair in self.openssl_dlls]
            output.extend(build_ext.get_outputs(self))
            return output



else:
    Libraries = ['ssl', 'crypto']
    BuildExtension = build_ext



def mkExtension(name):
    modname = 'OpenSSL.' + name
    src = globals()[name.lower() + '_src']
    dep = globals()[name.lower() + '_dep']
    return Extension(modname, src, libraries=Libraries, depends=dep,
                     include_dirs=IncludeDirs, library_dirs=LibraryDirs)


setup(name='pyOpenSSL', version=__version__,
      packages = ['OpenSSL'],
      package_dir = {'OpenSSL': 'OpenSSL'},
      ext_modules = [mkExtension('crypto'), mkExtension('rand'),
                     mkExtension('SSL')],
      py_modules  = ['OpenSSL.__init__', 'OpenSSL.tsafe',
                     'OpenSSL.version', 'OpenSSL.test.__init__',
                     'OpenSSL.test.util',
                     'OpenSSL.test.test_crypto',
                     'OpenSSL.test.test_rand',
                     'OpenSSL.test.test_ssl'],
      zip_safe = False,
      cmdclass = {"build_ext": BuildExtension},
      description = 'Python wrapper module around the OpenSSL library',
      author = 'Martin Sjögren, AB Strakt',
      author_email = 'msjogren@gmail.com',
      maintainer = 'Jean-Paul Calderone',
      maintainer_email = 'exarkun@twistedmatrix.com',
      url = 'http://pyopenssl.sourceforge.net/',
      license = 'APL2',
      long_description = """\
High-level wrapper around a subset of the OpenSSL library, includes
 * SSL.Connection objects, wrapping the methods of Python's portable
   sockets
 * Callbacks written in Python
 * Extensive error-handling mechanism, mirroring OpenSSL's error codes
...  and much more ;)"""
     )
