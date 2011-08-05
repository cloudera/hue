import os, sys
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
from distutils.cmd import Command
from distutils.command.build import build

if (sys.version_info >= (2, 6, 0)):
    sys.stderr.write("Skipping building ssl-1.15 because" +
                     "it is a built-in module in Python" +
                     "2.6 and later.\n")
    sys.exit(0)
elif (sys.version_info < (2, 3, 5)):
    sys.stderr.write("Warning:  This code has not been tested "
                     + "with versions of Python less than 2.3.5.\n")

class Test (Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run (self):

        """Run the regrtest module appropriately"""

        # figure out where the _ssl2 extension will be put
        b = build(self.distribution)
        b.initialize_options()
        b.finalize_options()
        extdir = os.path.abspath(b.build_platlib)

        # now set up the load path
        topdir = os.path.dirname(os.path.abspath(__file__))
        localtestdir = os.path.join(topdir, "test")
        sys.path.insert(0, topdir)        # for ssl package
        sys.path.insert(0, localtestdir)  # for test module
        sys.path.insert(0, extdir)        # for _ssl2 extension

        # make sure the network is enabled
        import test.test_support
        test.test_support.use_resources = ["network"]

        # and load the test and run it
        os.chdir(localtestdir)
        the_module = __import__("test_ssl", globals(), locals(), [])
        # Most tests run to completion simply as a side-effect of
        # being imported.  For the benefit of tests that can't run
        # that way (like test_threaded_import), explicitly invoke
        # their test_main() function (if it exists).
        indirect_test = getattr(the_module, "test_main", None)
        if indirect_test is not None:
            indirect_test()


def find_file(filename, std_dirs, paths):
    """Searches for the directory where a given file is located,
    and returns a possibly-empty list of additional directories, or None
    if the file couldn't be found at all.

    'filename' is the name of a file, such as readline.h or libcrypto.a.
    'std_dirs' is the list of standard system directories; if the
        file is found in one of them, no additional directives are needed.
    'paths' is a list of additional locations to check; if the file is
        found in one of them, the resulting list will contain the directory.
    """

    # Check the standard locations
    for dir in std_dirs:
        f = os.path.join(dir, filename)
        print 'looking for', f
        if os.path.exists(f): return []

    # Check the additional directories
    for dir in paths:
        f = os.path.join(dir, filename)
        print 'looking for', f
        if os.path.exists(f):
            return [dir]

    # Not found anywhere
    return None

def find_library_file(compiler, libname, std_dirs, paths):
    result = compiler.find_library_file(std_dirs + paths, libname)
    if result is None:
        return None

    # Check whether the found file is in one of the standard directories
    dirname = os.path.dirname(result)
    for p in std_dirs:
        # Ensure path doesn't end with path separator
        p = p.rstrip(os.sep)
        if p == dirname:
            return [ ]

    # Otherwise, it must have been in one of the additional directories,
    # so we have to figure out which one.
    for p in paths:
        # Ensure path doesn't end with path separator
        p = p.rstrip(os.sep)
        if p == dirname:
            return [p]
    else:
        assert False, "Internal error: Path not found in std_dirs or paths"


def find_ssl():

    # Detect SSL support for the socket module (via _ssl)
    from distutils.ccompiler import new_compiler

    compiler = new_compiler()
    inc_dirs = compiler.include_dirs + ['/usr/include']

    search_for_ssl_incs_in = [
                          '/usr/local/ssl/include',
                          '/usr/contrib/ssl/include/'
                         ]
    ssl_incs = find_file('openssl/ssl.h', inc_dirs,
                         search_for_ssl_incs_in
                         )
    if ssl_incs is not None:
        krb5_h = find_file('krb5.h', inc_dirs,
                           ['/usr/kerberos/include'])
        if krb5_h:
            ssl_incs += krb5_h

    ssl_libs = find_library_file(compiler, 'ssl',
                                 ['/usr/lib'],
                                 ['/usr/local/lib',
                                  '/usr/local/ssl/lib',
                                  '/usr/contrib/ssl/lib/'
                                 ] )

    if (ssl_incs is not None and ssl_libs is not None):
        return ssl_incs, ssl_libs, ['ssl', 'crypto']

    raise Exception("No SSL support found")

if (sys.version_info >= (2, 5, 1)):
    socket_inc = "./ssl/2.5.1"
else:
    socket_inc = "./ssl/2.3.6"

link_args = []
if sys.platform == 'win32':

    # Assume the openssl libraries from GnuWin32 are installed in the
    # following location:
    gnuwin32_dir = os.environ.get("GNUWIN32_DIR", r"C:\Utils\GnuWin32")

    # Set this to 1 for a dynamic build (depends on openssl DLLs)
    # Dynamic build is about 26k, static is 670k
    dynamic = int(os.environ.get("SSL_DYNAMIC", 0))

    ssl_incs = [os.environ.get("C_INCLUDE_DIR") or os.path.join(gnuwin32_dir, "include")]
    ssl_libs = [os.environ.get("C_LIB_DIR") or os.path.join(gnuwin32_dir, "lib")]
    libs = ['ssl', 'crypto', 'wsock32']
    if not dynamic:
	libs = libs + ['gdi32', 'gw32c', 'ole32', 'uuid']
        link_args = ['-static']
else:
    ssl_incs, ssl_libs, libs = find_ssl()

testdir = os.path.join(get_python_lib(False), "test")                                 

setup(name='ssl',
      version='1.15',
      description='SSL wrapper for socket objects (2.3, 2.4, 2.5 compatible)',
      long_description=
"""
The old socket.ssl() support for TLS over sockets is being
superseded in Python 2.6 by a new 'ssl' module.  This package
brings that module to older Python releases, 2.3.5 and up (it may
also work on older versions of 2.3, but we haven't tried it).

It's quite similar to the 2.6 ssl module.  There's no stand-alone
documentation for this package; instead, just use the development
branch documentation for the SSL module at
http://docs.python.org/dev/library/ssl.html.

Version 1.0 had a problem with Python 2.5.1 -- the structure of
the socket object changed from earlier versions.

Version 1.1 was missing various package metadata information.

Version 1.2 added more package metadata, and support for
ssl.get_server_certificate(), and the PEM-to-DER encode/decode
routines.  Plus integrated Paul Moore's patch to setup.py for
Windows.  Plus added support for asyncore, and asyncore HTTPS
server test.

Version 1.3 fixed a bug in the test suite.

Version 1.4 incorporated use of -static switch.

Version 1.5 fixed bug in Python version check affecting build on
Python 2.5.0.

Version 1.7 (and 1.6) fixed some bugs with asyncore support (recv and
send not being called on the SSLSocket class, wrong semantics for
sendall).

Version 1.8 incorporated some code from Chris Stawarz to handle
sockets which are set to non-blocking before negotiating the SSL
session.

Version 1.9 makes ssl.SSLError a subtype of socket.error.

Version 1.10 fixes a bug in sendall().

Version 1.11 includes the MANIFEST file, and by default will turne
unexpected EOFs occurring during a read into a regular EOF.  It also
removes the code for SSLFileStream, to use the regular socket module's
_fileobject instead.

Version 1.12 fixes the bug in SSLSocket.accept() reported by Georg
Brandl, and adds a test case for that fix.

Version 1.13 fixes a bug in calling do_handshake() automatically
on non-blocking sockets.  Thanks to Giampaolo Rodola.  Now includes
real asyncore test case.

Version 1.14 incorporates some fixes to naming (rename "recv_from" to
"recvfrom" and "send_to" to "sendto"), and a fix to the asyncore test
case to unregister the connection handler when the connection is
closed.  It also exposes the SSL shutdown via the "unwrap" method
on an SSLSocket.  It exposes "subjectPublicKey" in the data received
from a peer cert.

Version 1.15 fixes a bug in write retries, where the output buffer has
changed location because of garbage collection during the interim.
It also provides the new flag, PROTOCOL_NOSSLv2, which selects SSL23,
but disallows actual use of SSL2.

Authorship: A cast of dozens over the years have written the Python
SSL support, including Marc-Alan Lemburg, Robin Dunn, GvR, Kalle
Svensson, Skip Montanaro, Mark Hammond, Martin von Loewis, Jeremy
Hylton, Andrew Kuchling, Georg Brandl, Bill Janssen, Chris Stawarz,
Neal Norwitz, and many others.  Thanks to Paul Moore, David Bolen and
Mark Hammond for help with the Windows side of the house.  And it's
all based on OpenSSL, which has its own cast of dozens!

""",

      license='Python (MIT-like)',
      author='See long_description for details',
      author_email='python.ssl.maintainer@gmail.com',
      url='http://docs.python.org/dev/library/ssl.html',
      cmdclass={'test': Test},
      packages=['ssl'],
      ext_modules=[Extension('ssl._ssl2', ['ssl/_ssl2.c'],
                             include_dirs = ssl_incs + [socket_inc],
                             library_dirs = ssl_libs,
                             libraries = libs,
                             extra_link_args = link_args)],
      data_files=[(testdir, ['test/test_ssl.py',
                             'test/keycert.pem',
                             'test/badcert.pem',
                             'test/badkey.pem',
                             'test/nullcert.pem'])],
      )
