#-*- coding: ISO-8859-1 -*-
# setup.py: the distutils script
#
# Copyright (C) 2004-2007 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import glob, os, re, sys
import urllib
import zipfile

from distutils.core import setup, Extension, Command
from distutils.command.build import build
from distutils.command.build_ext import build_ext

import cross_bdist_wininst

# If you need to change anything, it should be enough to change setup.cfg.

sqlite = "sqlite"

sources = ["src/module.c", "src/connection.c", "src/cursor.c", "src/cache.c",
           "src/microprotocols.c", "src/prepare_protocol.c", "src/statement.c",
           "src/util.c", "src/row.c"]

include_dirs = []
library_dirs = []
libraries = []
runtime_library_dirs = []
extra_objects = []
define_macros = []

long_description = \
"""Python interface to SQLite 3

pysqlite is an interface to the SQLite 3.x embedded relational database engine.
It is almost fully compliant with the Python database API version 2.0 also
exposes the unique features of SQLite."""

if sys.platform != "win32":
    define_macros.append(('MODULE_NAME', '"pysqlite2.dbapi2"'))
else:
    define_macros.append(('MODULE_NAME', '\\"pysqlite2.dbapi2\\"'))

class DocBuilder(Command):
    description = "Builds the documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os, shutil
        try:
            shutil.rmtree("build/doc")
        except OSError:
            pass
        os.makedirs("build/doc")
        rc = os.system("sphinx-build doc/sphinx build/doc")
        if rc != 0:
            print "Is sphinx installed? If not, try 'sudo easy_install sphinx'."

AMALGAMATION_ROOT = "amalgamation"

def get_amalgamation():
    """Download the SQLite amalgamation if it isn't there, already."""
    if os.path.exists(AMALGAMATION_ROOT):
        return
    os.mkdir(AMALGAMATION_ROOT)
    print "Downloading amalgation."

    # find out what's current amalgamation ZIP file
    download_page = urllib.urlopen("http://sqlite.org/download.html").read()
    pattern = re.compile("(sqlite-amalgamation.*?\.zip)")
    download_file = pattern.findall(download_page)[0]
    amalgamation_url = "http://sqlite.org/" + download_file

    # and download it
    urllib.urlretrieve(amalgamation_url, "tmp.zip")

    zf = zipfile.ZipFile("tmp.zip")
    files = ["sqlite3.c", "sqlite3.h"]
    for fn in files:
        print "Extracting", fn
        outf = open(AMALGAMATION_ROOT + os.sep + fn, "wb")
        outf.write(zf.read(fn))
        outf.close()
    zf.close()
    os.unlink("tmp.zip")

class AmalgamationBuilder(build):
    description = "Build a statically built pysqlite using the amalgamtion."

    def __init__(self, *args, **kwargs):
        MyBuildExt.amalgamation = True
        build.__init__(self, *args, **kwargs)

class MyBuildExt(build_ext):
    amalgamation = False

    def build_extension(self, ext):
        if self.amalgamation:
            get_amalgamation()
            ext.define_macros.append(("SQLITE_ENABLE_FTS3", "1"))   # build with fulltext search enabled
            ext.sources.append(os.path.join(AMALGAMATION_ROOT, "sqlite3.c"))
            ext.include_dirs.append(AMALGAMATION_ROOT)
        build_ext.build_extension(self, ext)

    def __setattr__(self, k, v):
        # Make sure we don't link against the SQLite library, no matter what setup.cfg says
        if self.amalgamation and k == "libraries":
            v = None
        self.__dict__[k] = v

def get_setup_args():

    PYSQLITE_VERSION = None

    version_re = re.compile('#define PYSQLITE_VERSION "(.*)"')
    f = open(os.path.join("src", "module.h"))
    for line in f:
        match = version_re.match(line)
        if match:
            PYSQLITE_VERSION = match.groups()[0]
            PYSQLITE_MINOR_VERSION = ".".join(PYSQLITE_VERSION.split('.')[:2])
            break
    f.close()

    if not PYSQLITE_VERSION:
        print "Fatal error: PYSQLITE_VERSION could not be detected!"
        sys.exit(1)

    data_files = [("pysqlite2-doc",
                        glob.glob("doc/*.html") \
                      + glob.glob("doc/*.txt") \
                      + glob.glob("doc/*.css")),
                   ("pysqlite2-doc/code",
                        glob.glob("doc/code/*.py"))]

    py_modules = ["sqlite"]
    setup_args = dict(
            name = "pysqlite",
            version = PYSQLITE_VERSION,
            description = "DB-API 2.0 interface for SQLite 3.x",
            long_description=long_description,
            author = "Gerhard Haering",
            author_email = "gh@ghaering.de",
            license = "zlib/libpng license",
            platforms = "ALL",
            url = "http://oss.itsystementwicklung.de/trac/pysqlite",
            download_url = "http://oss.itsystementwicklung.de/download/pysqlite/%s/%s/" % \
                (PYSQLITE_MINOR_VERSION, PYSQLITE_VERSION),


            # Description of the modules and packages in the distribution
            package_dir = {"pysqlite2": "pysqlite2"},
            packages = ["pysqlite2", "pysqlite2.test"],
            scripts=[],
            data_files = data_files,

            ext_modules = [Extension( name="pysqlite2._sqlite",
                                      sources=sources,
                                      include_dirs=include_dirs,
                                      library_dirs=library_dirs,
                                      runtime_library_dirs=runtime_library_dirs,
                                      libraries=libraries,
                                      extra_objects=extra_objects,
                                      define_macros=define_macros
                                      )],
            classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Topic :: Database :: Database Engines/Servers",
            "Topic :: Software Development :: Libraries :: Python Modules"],
            cmdclass = {"build_docs": DocBuilder}
            )

    setup_args["cmdclass"].update({"build_docs": DocBuilder, "build_ext": MyBuildExt, "build_static": AmalgamationBuilder, "cross_bdist_wininst": cross_bdist_wininst.bdist_wininst})
    return setup_args

def main():
    setup(**get_setup_args())

if __name__ == "__main__":
    main()
