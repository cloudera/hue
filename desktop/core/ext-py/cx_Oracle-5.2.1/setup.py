"""Distutils script for cx_Oracle.

Windows platforms:
    python setup.py build --compiler=mingw32 install

Unix platforms
    python setup.py build install

"""

import distutils.command
try:
    import distutils.command.bdist_msi
except ImportError:
    distutils.command.bdist_msi = None
try:
    import distutils.command.bdist_wininst
except ImportError:
    distutils.command.bdist_wininst = None
import distutils.command.bdist_rpm
import distutils.command.build
import distutils.core
import distutils.dist
import distutils.util
import os
import re
import struct
import sys
import glob

from distutils.errors import DistutilsSetupError

# if setuptools is detected, use it to add support for eggs
try:
    from setuptools import setup, Extension
except:
    from distutils.core import setup
    from distutils.extension import Extension

# define build constants
BUILD_VERSION = "5.2.1"

# define the list of files to be included as documentation for Windows
dataFiles = None
if sys.platform in ("win32", "cygwin"):
    baseName = "cx_Oracle-doc"
    dataFiles = [ (baseName,
            [ "BUILD.txt", "README.txt"]) ]
    for dir in ("samples", "test"):
        files = []
        fullDirName = "%s/%s" % (baseName, dir)
        for name in os.listdir(dir):
            if name.startswith("."):
                continue
            if os.path.isdir(os.path.join(dir, name)):
                continue
            fullName = "%s/%s" % (dir, name)
            files.append(fullName)
        dataFiles.append((fullDirName, files))

# define the list of files to be included as documentation for bdist_rpm
docFiles = "README.txt BUILD.txt samples test"

# method for checking a potential Oracle home
def CheckOracleHome(directoryToCheck):
    global oracleHome, oracleVersion, oracleLibDir
    import os
    import struct
    import sys
    if sys.platform in ("win32", "cygwin"):
        subDirs = ["bin"]
        filesToCheck = [
                ("12c", "oraocci12.dll"),
                ("11g", "oraocci11.dll"),
                ("10g", "oraocci10.dll")
        ]
    elif sys.platform == "darwin":
        subDirs = ["lib"]
        filesToCheck = [
                ("12c", "libclntsh.dylib.12.1"),
                ("11g", "libclntsh.dylib.11.1"),
                ("10g", "libclntsh.dylib.10.1")
        ]
    else:
        if struct.calcsize("P") == 4:
            subDirs = ["lib", "lib32"]
        else:
            subDirs = ["lib", "lib64"]
        filesToCheck = [
                ("12c", "libclntsh.so.12.1"),
                ("11g", "libclntsh.so.11.1"),
                ("10g", "libclntsh.so.10.1")
        ]
    for version, baseFileName in filesToCheck:
        fileName = os.path.join(directoryToCheck, baseFileName)
        if os.path.exists(fileName):
            if os.path.basename(directoryToCheck).lower() == "bin":
                oracleHome = os.path.dirname(directoryToCheck)
            else:
                oracleHome = directoryToCheck
            oracleLibDir = directoryToCheck
            oracleVersion = version
            return True
        for subDir in subDirs:
            fileName = os.path.join(directoryToCheck, subDir, baseFileName)
            if os.path.exists(fileName):
                oracleHome = directoryToCheck
                oracleLibDir = os.path.join(directoryToCheck, subDir)
                oracleVersion = version
                return True
            dirName = os.path.dirname(directoryToCheck)
            fileName = os.path.join(dirName, subDir, baseFileName)
            if os.path.exists(fileName):
                oracleHome = dirName
                oracleLibDir = os.path.join(dirName, subDir)
                oracleVersion = version
                return True
    oracleHome = oracleVersion = oracleLibDir = None
    return False

# Look for the highest version Instant Client "basic" or "basiclite" RPM
# Newer Instant Client dirs have the form:
#    /usr/lib/oracle/12.1/client[64]/lib
# Older Instant Client dirs have the form:
#    /usr/lib/oracle/10.2.0.5/client[64]/lib
def FindInstantClientRPMLib():
    versions = []
    for path in glob.glob(os.path.join(rpmBaseLibDir, "[0-9.]*")):
        versions.append(os.path.basename(path))
    versions.sort(key = lambda x: [int(s) for s in x.split(".")])
    versions.reverse()
    for version in versions:
        path = os.path.join(rpmBaseLibDir, version, rpmClientDir, "lib")
        if os.path.exists(path) and CheckOracleHome(path):
            return path

# If the lib dir appears to be an Instant Client RPM dir, then look only
# for matching SDK headers
def FindInstantClientRPMInclude(libDir):
    version = os.path.basename(os.path.dirname(os.path.dirname(libDir)))
    includeDir = os.path.join("/usr/include/oracle", version, rpmClientDir)
    if os.path.isfile(os.path.join(includeDir, "oci.h")):
        return [includeDir]
    raise DistutilsSetupError("cannot locate Oracle Instant Client " \
            "SDK RPM header files")

# define Linux Instant Client RPM path components
# Assume 64 bit builds if the platform is 64 bit
rpmBaseLibDir = "/usr/lib/oracle"
if struct.calcsize("P") == 4:
    rpmClientDir = "client"
else:
    rpmClientDir = "client64"
instantClientRPMLib = None

# try to determine the Oracle home
userOracleHome = os.environ.get("ORACLE_HOME", os.environ.get("ORACLE_INSTANTCLIENT_HOME"))
if userOracleHome is not None:
    if not CheckOracleHome(userOracleHome):
        messageFormat = "Oracle home (%s) does not refer to an " \
                "10g, 11g or 12c installation."
        raise DistutilsSetupError(messageFormat % userOracleHome)
else:
    for path in os.environ["PATH"].split(os.pathsep):
        if CheckOracleHome(path):
            break
    if oracleHome is None and sys.platform.startswith("linux"):
        instantClientRPMLib = FindInstantClientRPMLib()
    if oracleHome is None:
        print >>sys.stderr, "cannot locate an Oracle software installation. skipping"
        sys.exit(0)

# define some variables
if sys.platform == "win32":
    libDirs = [os.path.join(oracleHome, "bin"), oracleHome,
            os.path.join(oracleHome, "oci", "lib", "msvc"),
            os.path.join(oracleHome, "sdk", "lib", "msvc")]
    possibleIncludeDirs = ["oci/include", "rdbms/demo", "sdk/include"]
    includeDirs = []
    for dir in possibleIncludeDirs:
        path = os.path.normpath(os.path.join(oracleHome, dir))
        if os.path.isdir(path):
            includeDirs.append(path)
    if not includeDirs:
        message = "cannot locate Oracle include files in %s" % oracleHome
        raise DistutilsSetupError(message)
    libs = ["oci"]
elif sys.platform == "cygwin":
    includeDirs = ["/usr/include", "rdbms/demo", "rdbms/public", \
            "network/public", "oci/include"]
    libDirs = ["bin", "lib"]
    for i in range(len(includeDirs)):
        includeDirs[i] = os.path.join(oracleHome, includeDirs[i])
    for i in range(len(libDirs)):
        libDirs[i] = os.path.join(oracleHome, libDirs[i])
    libs = ["oci"]
else:
    libDirs = [oracleLibDir]
    libs = ["clntsh"]
    if instantClientRPMLib is not None:
        includeDirs = FindInstantClientRPMInclude(instantClientRPMLib)
    else:
        possibleIncludeDirs = ["rdbms/demo", "rdbms/public", "network/public",
                "sdk/include"]
        if sys.platform == "darwin":
            possibleIncludeDirs.append("plsql/public")
        includeDirs = []
        for dir in possibleIncludeDirs:
            path = os.path.join(oracleHome, dir)
            if os.path.isdir(path):
                includeDirs.append(path)
        if not includeDirs:
            path = os.path.join(oracleLibDir, "include")
            if os.path.isdir(path):
                includeDirs.append(path)
        if not includeDirs:
            path = re.sub("lib(64)?", "include", oracleHome)
            if os.path.isdir(path):
                includeDirs.append(path)
        if not includeDirs:
            raise DistutilsSetupError("cannot locate Oracle include files")

# NOTE: on HP-UX Itanium with Oracle 10g you need to add the library "ttsh10"
# to the list of libraries along with "clntsh"; since I am unable to test, I'll
# leave this as a comment until someone can verify when this is required
# without making other cases where sys.platform == "hp-ux11" stop working

# setup extra link and compile args
extraCompileArgs = ["-DBUILD_VERSION=%s" % BUILD_VERSION]
extraLinkArgs = []
if sys.platform == "aix4":
    extraCompileArgs.append("-qcpluscmt")
elif sys.platform == "aix5":
    extraCompileArgs.append("-DAIX5")
elif sys.platform == "cygwin":
    extraCompileArgs.append("-mno-cygwin")
    extraLinkArgs.append("-Wl,--enable-runtime-pseudo-reloc")
elif sys.platform == "darwin":
    extraLinkArgs.append("-shared-libgcc")

# force the inclusion of an RPATH linker directive if desired; this will
# eliminate the need for setting LD_LIBRARY_PATH but it also means that this
# location will be the only location searched for the Oracle client library
if "FORCE_RPATH" in os.environ or instantClientRPMLib:
    extraLinkArgs.append("-Wl,-rpath,%s" % oracleLibDir)

# tweak distribution full name to include the Oracle version
class Distribution(distutils.dist.Distribution):

    def get_fullname_with_oracle_version(self):
        name = self.metadata.get_fullname()
        return "%s-%s" % (name, oracleVersion)


# tweak the RPM build command to include the Python and Oracle version
class bdist_rpm(distutils.command.bdist_rpm.bdist_rpm):

    def run(self):
        distutils.command.bdist_rpm.bdist_rpm.run(self)
        specFile = os.path.join(self.rpm_base, "SPECS",
                "%s.spec" % self.distribution.get_name())
        queryFormat = "%{name}-%{version}-%{release}.%{arch}.rpm"
        command = "rpm -q --qf '%s' --specfile %s" % (queryFormat, specFile)
        origFileName = os.popen(command).read()
        parts = origFileName.split("-")
        parts.insert(2, oracleVersion)
        parts.insert(3, "py%s%s" % sys.version_info[:2])
        newFileName = "-".join(parts)
        self.move_file(os.path.join("dist", origFileName),
        os.path.join("dist", newFileName))


# tweak the build directories to include the Oracle version
class build(distutils.command.build.build):

    def finalize_options(self):
        import distutils.util
        import os
        import sys
        platSpecifier = ".%s-%s-%s" % \
                (distutils.util.get_platform(), sys.version[0:3],
                 oracleVersion)
        if self.build_platlib is None:
            self.build_platlib = os.path.join(self.build_base,
                    "lib%s" % platSpecifier)
        if self.build_temp is None:
            self.build_temp = os.path.join(self.build_base,
                    "temp%s" % platSpecifier)
        distutils.command.build.build.finalize_options(self)

class test(distutils.core.Command):
    description = "run the test suite for the extension"
    user_options = []

    def finalize_options(self):
        pass

    def initialize_options(self):
        pass

    def run(self):
        self.run_command("build")
        buildCommand = self.distribution.get_command_obj("build")
        sys.path.insert(0, os.path.abspath("test"))
        sys.path.insert(0, os.path.abspath(buildCommand.build_lib))
        if sys.version_info[0] < 3:
            execfile(os.path.join("test", "test.py"))
        else:
            fileName = os.path.join("test", "test3k.py")
            exec(open(fileName).read())

commandClasses = dict(build = build, bdist_rpm = bdist_rpm, test = test)

# tweak the Windows installer names to include the Oracle version
if distutils.command.bdist_msi is not None:

    class bdist_msi(distutils.command.bdist_msi.bdist_msi):

        def run(self):
            origMethod = self.distribution.get_fullname
            self.distribution.get_fullname = \
                    self.distribution.get_fullname_with_oracle_version
            distutils.command.bdist_msi.bdist_msi.run(self)
            self.distribution.get_fullname = origMethod

    commandClasses["bdist_msi"] = bdist_msi

if distutils.command.bdist_wininst is not None:

    class bdist_wininst(distutils.command.bdist_wininst.bdist_wininst):

        def run(self):
            origMethod = self.distribution.get_fullname
            self.distribution.get_fullname = \
                    self.distribution.get_fullname_with_oracle_version
            distutils.command.bdist_wininst.bdist_wininst.run(self)
            self.distribution.get_fullname = origMethod

    commandClasses["bdist_wininst"] = bdist_wininst

# define classifiers for the package index
classifiers = [
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database"
]

# setup the extension
extension = Extension(
        name = "cx_Oracle",
        include_dirs = includeDirs,
        libraries = libs,
        library_dirs = libDirs,
        extra_compile_args = extraCompileArgs,
        extra_link_args = extraLinkArgs,
        sources = ["cx_Oracle.c"],
        depends = ["Buffer.c", "Callback.c", "Connection.c", "Cursor.c",
                "CursorVar.c", "DateTimeVar.c", "Environment.c", "Error.c",
                "ExternalLobVar.c", "ExternalObjectVar.c", "IntervalVar.c",
                "LobVar.c", "LongVar.c", "NumberVar.c", "ObjectType.c",
                "ObjectVar.c", "SessionPool.c", "StringVar.c",
                "Subscription.c", "TimestampVar.c", "Transforms.c",
                "Variable.c"])

# perform the setup
setup(
        name = "cx_Oracle",
        version = BUILD_VERSION,
        distclass = Distribution,
        description = "Python interface to Oracle",
        data_files = dataFiles,
        cmdclass = commandClasses,
        options = dict(bdist_rpm = dict(doc_files = docFiles)),
        long_description = \
            "Python interface to Oracle conforming to the Python DB API 2.0 "
            "specification.\n"
            "See http://www.python.org/topics/database/DatabaseAPI-2.0.html.",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://cx-oracle.sourceforge.net",
        ext_modules = [extension],
        keywords = "Oracle",
        license = "Python Software Foundation License",
        classifiers = classifiers)

