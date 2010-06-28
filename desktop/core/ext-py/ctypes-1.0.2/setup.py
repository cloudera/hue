#!/usr/bin/env python
#
# $Id: setup.py 54355 2007-03-13 20:25:50Z thomas.heller $
#
#

### Begin Desktop modification:
### ctypes already exists in python 2.5 and later
import sys
if sys.version_info >= (2, 5):
  print "ctypes should already be installed; skipping."
  sys.exit(0)
### End desktop modification.

"""ctypes is a Python package to create and manipulate C data types in
Python, and to call functions in dynamic link libraries/shared
dlls. It allows wrapping these libraries in pure Python.
"""

LIBFFI_SOURCES='source/libffi'

__version__ = "1.0.2"

################################################################

##from ez_setup import use_setuptools
##use_setuptools()

import os, sys

if sys.version_info < (2, 3):
    raise Exception, "ctypes %s requires Python 2.3 or better" % __version__

from distutils.core import setup, Extension, Command
import distutils.core
from distutils.errors import DistutilsOptionError
from distutils.command import build_py, build_ext, clean
from distutils.command import install_data
from distutils.dir_util import mkpath
from distutils.util import get_platform
from distutils.cygwinccompiler import Mingw32CCompiler

################################################################
# Manipulate the environment for the build process.
#
if get_platform() in ["solaris-2.9-sun4u", "linux-x86_64"]:
    os.environ["CFLAGS"] = "-fPIC"

if sys.platform == "win32" and "64 bit (AMD64)" in sys.version:
    os.environ["DISTUTILS_USE_SDK"] = "1"

################################################################
# Additional and overridden distutils commands
#
class test(Command):
    # Original version of this class posted
    # by Berthold Hoellmann to distutils-sig@python.org
    description = "run tests"

    user_options = [
        ('tests=', 't',
         "comma-separated list of packages that contain test modules"),
        ('use-resources=', 'u',
         "resources to use - resource names are defined by tests"),
        ('refcounts', 'r',
         "repeat tests to search for refcount leaks (requires 'sys.gettotalrefcount')"),
        ]

    boolean_options = ["refcounts"]

    def initialize_options(self):
        self.build_base = 'build'
        self.use_resources = ""
        self.refcounts = False
        self.tests = "ctypes.test"

    # initialize_options()

    def finalize_options(self):
        if self.refcounts and not hasattr(sys, "gettotalrefcount"):
            raise DistutilsOptionError("refcount option requires Python debug build")
        self.tests = self.tests.split(",")
        self.use_resources = self.use_resources.split(",")

    # finalize_options()

    def run(self):
        self.run_command('build')

        import ctypes.test
        ctypes.test.use_resources.extend(self.use_resources)

        for name in self.tests:
            package = __import__(name, globals(), locals(), ['*'])
            print "Testing package", name, (sys.version, sys.platform, os.name)
            ctypes.test.run_tests(package,
                                  "test_*.py",
                                  self.verbose,
                                  self.refcounts)

    # run()

# class test


class my_build_py(build_py.build_py):
    def find_package_modules (self, package, package_dir):
        """We extend distutils' build_py.find_package_modules() method
        to include all modules found in the platform specific root
        package directory into the 'ctypes' root package."""
        import glob, sys
        result = build_py.build_py.find_package_modules(self, package, package_dir)
        if package == 'ctypes':
            for pathname in glob.glob(os.path.join(sys.platform, "*.py")):
                modname = os.path.splitext(os.path.basename(pathname))[0]
                result.append(('ctypes', modname, pathname))
        return result

def find_file_in_subdir(dirname, filename):
    # if <filename> is in <dirname> or any subdirectory thereof,
    # return the directory name, else None
    for d, _, names in os.walk(dirname):
        if filename in names:
            return d
    return None

class my_build_ext(build_ext.build_ext):
    def finalize_options(self):
        if self.debug is None:
            import imp
            self.debug = ('_d.pyd', 'rb', imp.C_EXTENSION) in imp.get_suffixes()
        build_ext.build_ext.finalize_options(self)

    # First configure a libffi library, then build the _ctypes extension.
    def build_extensions(self):
        self.configure_libffi()

        # Add .S (preprocessed assembly) to C compiler source extensions.
        self.compiler.src_extensions.append('.S')
        if sys.platform == "win32":
            if isinstance(self.compiler, Mingw32CCompiler):
                # Windows lowercases the extensions, it seems, before
                # determining how to compile a file.  So, even if win32.S
                # is in sources, we have to add '.s'.
                self.compiler.src_extensions.append('.s')
                for ext in self.extensions:
                    if ext.name == "_ctypes":
                        ext.sources.remove("source/libffi_msvc/win32.c")
            else:
                for ext in self.extensions:
                    if ext.name == "_ctypes":
                        ext.sources.remove("source/libffi_msvc/win32.S")

                        # This should be refactored, so that we can
                        # add amd64.asm to the sources, and
                        # my_build_ext does the rest.
                        if "64 bit (AMD64)" in sys.version:

                            ext.sources.remove("source/libffi_msvc/win32.c")
                            ext.depends.append("source/libffi_msvc/win64.obj")
                            ext.extra_objects.append("source/libffi_msvc/win64.obj")

                            from distutils.dep_util import newer_group
                            if newer_group(["source/libffi_msvc/win64.asm"],
                                           "source/libffi_msvc/win64.obj",
                                           missing="newer") or self.force:
                                cmd = "ml64.exe /nologo /c /Zi /Fosource/libffi_msvc/win64.obj " + \
                                      "source/libffi_msvc/win64.asm"
                                print self.build_temp
                                print cmd
                                os.system(cmd)

                    ext.extra_link_args = []

        build_ext.build_ext.build_extensions(self)

    def fix_extension(self, ffi_dir):
        fficonfigfile = os.path.join(ffi_dir, 'fficonfig.py')
        if not os.path.exists(fficonfigfile):
            return 0

        incdir = find_file_in_subdir(os.path.join(ffi_dir, "include"), "ffi.h")
        if not incdir:
            return 0
        incdir_2 = find_file_in_subdir(ffi_dir, "fficonfig.h")
        if not incdir_2:
            return 0

        fficonfig = {}
        execfile(fficonfigfile, globals(), fficonfig)
        srcdir = os.path.join(fficonfig['ffi_srcdir'], 'src')

        for ext in self.extensions:
            if ext.name == "_ctypes":
                ext.include_dirs.append(incdir)
                ext.include_dirs.append(incdir_2)
                ext.include_dirs.append(srcdir)
                ext.sources.extend(fficonfig['ffi_sources'])
                if fficonfig['ffi_cflags'].strip():
                    ext.extra_compile_args.extend(
                        fficonfig['ffi_cflags'].split())
        return 1

    def configure_libffi(self):
        if sys.platform == "win32":
            return
        if LIBFFI_SOURCES == None:
            return
        src_dir = os.path.abspath(LIBFFI_SOURCES)

        # Building libffi in a path containing spaces doesn't work:
        self.build_temp = self.build_temp.replace(" ", "")

        build_dir = os.path.join(self.build_temp, 'libffi')

        if not self.force and self.fix_extension(build_dir):
            return

        mkpath(build_dir)
        config_args = []

        # Pass empty CFLAGS because we'll just append the resulting CFLAGS
        # to Python's; -g or -O2 is to be avoided.
        cmd = "cd %s && env CFLAGS='' '%s/configure' %s" \
              % (build_dir, src_dir, " ".join(config_args))

        print 'Configuring static FFI library:'
        print cmd
        res = os.system(cmd)
        if res:
            print "Failed"
            sys.exit(res)

        assert self.fix_extension(build_dir), "Could not find libffi after building it"

# Since we mangle the build_temp dir, we must also do this in the clean command.
class my_clean(clean.clean):
    def run(self):
        self.build_temp = self.build_temp.replace(" ", "")
        clean.clean.run(self)

class my_install_data(install_data.install_data):
    """A custom install_data command, which will install it's files
    into the standard directories (normally lib/site-packages).
    """
    def finalize_options(self):
        if self.install_dir is None:
            installobj = self.distribution.get_command_obj('install')
            self.install_dir = installobj.install_lib
        print 'Installing data files to %s' % self.install_dir
        install_data.install_data.finalize_options(self)

################################################################
# Specify the _ctypes extension
#
kw = {}
# common source files
kw["sources"] = ["source/_ctypes.c",
                 "source/callbacks.c",
                 "source/callproc.c",
                 "source/stgdict.c",
                 "source/cfield.c",
                 "source/malloc_closure.c"]

# common header file
kw["depends"] = ["source/ctypes.h"]

if sys.platform == "win32":
    kw["sources"].extend([
        # types.c is no longer needed, ffi_type defs are in cfield.c
        "source/libffi_msvc/ffi.c",
        "source/libffi_msvc/prep_cif.c",
        # All except one of these will be removed, in my_build_ext,
        # depending on the compiler used:
        "source/libffi_msvc/win32.c",
        "source/libffi_msvc/win32.S",
        ])
    extra_compile_args = []

    # Extra arguments passed to linker from MinGW,
    # will be removed, in my_build_ext, if compiler <> MinGW
    extra_link_args = []

    # In MinGW32, the first linker option should be:
    #    -Xlinker --enable-stdcall-fixup
    # but here this option is split into two options to
    # force distutils not to surroud the entire option
    # with double quotes as it sees a space in it. So:

    extra_link_args.extend(["-Xlinker", "--enable-stdcall-fixup",

    # In MinGW32, the --kill-at linker option forces MinGW to
    # remove the @XY decoration from function names, hence making
    # the stdcall functions of _ctypes_test and those tested in
    # test_cfuns.py behave similarly to the one compiled in MSVC.

                            "-Wl,--kill-at"])

    extensions = [Extension("_ctypes",
                            extra_compile_args = extra_compile_args,
                            extra_link_args = extra_link_args,
                            export_symbols=["DllGetClassObject,PRIVATE",
                                            "DllCanUnloadNow,PRIVATE"],
                            libraries=["ole32", "user32", "oleaut32", "uuid"],
                            include_dirs=["source/libffi_msvc"],
                            **kw),
                  Extension("_ctypes_test",
                            extra_compile_args = extra_compile_args,
                            extra_link_args = extra_link_args,
                            libraries=["oleaut32", "user32"],
                            sources=["source/_ctypes_test.c"],
                            include_dirs=["source/libffi_msvc"],
                            )
                  ]
    if kw.has_key("depends"):
        kw["depends"].extend(["source/libffi_msvc/ffi.h",
                              "source/libffi_msvc/fficonfig.h",
                              "source/libffi_msvc/ffitarget.h",
                              "source/libffi_msvc/ffi_common.h"])
else:
    include_dirs = []
    library_dirs = []
    extra_link_args = []
    if sys.platform == "darwin":
        kw["sources"].append("source/darwin/dlfcn_simple.c")
        extra_link_args.extend(['-read_only_relocs', 'warning'])
        include_dirs.append("source/darwin")
    elif sys.platform == "sunos5":
        extra_link_args.extend(['-mimpure-text'])

    extensions = [Extension("_ctypes",
                            include_dirs=include_dirs,
                            library_dirs=library_dirs,
                            extra_link_args=extra_link_args,
                            **kw),
                  Extension("_ctypes_test",
                            sources=["source/_ctypes_test.c"])
                  ]
################################################################
# the ctypes package
#
packages = ["ctypes",
            "ctypes.macholib",
            "ctypes.test"]

################################################################
# pypi classifiers
#
classifiers = [
    'Development Status :: 4 - Beta',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ]

################################################################
# main section
#
##from ce import ce_install_lib

if __name__ == '__main__':
    setup(name="ctypes",
##          entry_points = {"console_scripts" : ["xml2py = ctypes.wrap.xml2py:main",
##                                               "h2xml = ctypes.wrap.h2xml:main"]},
          ext_modules = extensions,
          packages = packages,

          classifiers = classifiers,

          version=__version__,
          description="create and manipulate C data types in Python, call functions in shared libraries",
          long_description = __doc__,
          author="Thomas Heller",
          author_email="theller@ctypes.org",
          license="MIT License",
          url="http://starship.python.net/crew/theller/ctypes/",
          platforms=["windows", "Linux", "MacOS X", "Solaris", "FreeBSD"],
          download_url="http://sourceforge.net/project/showfiles.php?group_id=71702",

          cmdclass = {'test': test, 'build_py': my_build_py, 'build_ext': my_build_ext,
                      'clean': my_clean, 'install_data': my_install_data,
##                      'ce_install_lib': ce_install_lib
                      },

          )

## Local Variables:
## compile-command: "python setup.py build"
## End:
