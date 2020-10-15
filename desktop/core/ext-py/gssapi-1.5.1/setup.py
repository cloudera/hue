#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup
from setuptools import Distribution
from setuptools.command.sdist import sdist
from setuptools.extension import Extension
import platform
import re
import sys
import os


SKIP_CYTHON_FILE = '__dont_use_cython__.txt'

if os.path.exists(SKIP_CYTHON_FILE):
    print("In distributed package, building from C files...", file=sys.stderr)
    SOURCE_EXT = 'c'
else:
    try:
        from Cython.Build import cythonize
        print("Building from Cython files...", file=sys.stderr)
        SOURCE_EXT = 'pyx'
    except ImportError:
        print("Cython not found, building from C files...",
              file=sys.stderr)
        SOURCE_EXT = 'c'

get_output = None

try:
    import commands
    get_output = commands.getoutput
except ImportError:
    import subprocess

    def _get_output(*args, **kwargs):
        res = subprocess.check_output(*args, shell=True, **kwargs)
        decoded = res.decode('utf-8')
        return decoded.strip()

    get_output = _get_output

# get the compile and link args
link_args = os.environ.get('GSSAPI_LINKER_ARGS', None)
compile_args = os.environ.get('GSSAPI_COMPILER_ARGS', None)
osx_has_gss_framework = False
if sys.platform == 'darwin':
    mac_ver = [int(v) for v in platform.mac_ver()[0].split('.')]
    osx_has_gss_framework = (mac_ver >= [10, 7, 0])

if link_args is None:
    if osx_has_gss_framework:
        link_args = '-framework GSS'
    elif os.environ.get('MINGW_PREFIX'):
        link_args = '-lgss'
    else:
        link_args = get_output('krb5-config --libs gssapi')

if compile_args is None:
    if osx_has_gss_framework:
        compile_args = '-framework GSS -DOSX_HAS_GSS_FRAMEWORK'
    elif os.environ.get('MINGW_PREFIX'):
        compile_args = '-fPIC'
    else:
        compile_args = get_output('krb5-config --cflags gssapi')

link_args = link_args.split()
compile_args = compile_args.split()

# add in the extra workarounds for different include structures
try:
    prefix = get_output('krb5-config gssapi --prefix')
except Exception:
    print("WARNING: couldn't find krb5-config; assuming prefix of %s"
          % str(sys.prefix))
    prefix = sys.prefix
gssapi_ext_h = os.path.join(prefix, 'include/gssapi/gssapi_ext.h')
if os.path.exists(gssapi_ext_h):
    compile_args.append("-DHAS_GSSAPI_EXT_H")

# ensure that any specific directories are listed before any generic system
# directories inserted by setuptools
library_dirs = [arg[2:] for arg in link_args if arg.startswith('-L')]
link_args = [arg for arg in link_args if not arg.startswith('-L')]

ENABLE_SUPPORT_DETECTION = \
    (os.environ.get('GSSAPI_SUPPORT_DETECT', 'true').lower() == 'true')

if ENABLE_SUPPORT_DETECTION:
    import ctypes.util

    main_lib = os.environ.get('GSSAPI_MAIN_LIB', None)
    main_path = ""
    if main_lib is None and osx_has_gss_framework:
        main_lib = ctypes.util.find_library('GSS')
    elif os.environ.get('MINGW_PREFIX'):
        main_lib = os.environ.get('MINGW_PREFIX')+'/bin/libgss-3.dll'
    elif main_lib is None:
        for opt in link_args:
            if opt.startswith('-lgssapi'):
                main_lib = 'lib%s.so' % opt[2:]

            # To support Heimdal on Debian, read the linker path.
            if opt.startswith('-Wl,/'):
                main_path = opt[4:] + "/"

    if main_lib is None:
        raise Exception("Could not find main GSSAPI shared library.  Please "
                        "try setting GSSAPI_MAIN_LIB yourself or setting "
                        "ENABLE_SUPPORT_DETECTION to 'false'")

    GSSAPI_LIB = ctypes.CDLL(main_path + main_lib)


# add in the flag that causes us not to compile from Cython when
# installing from an sdist
class sdist_gssapi(sdist):
    def run(self):
        if not self.dry_run:
            with open(SKIP_CYTHON_FILE, 'w') as flag_file:
                flag_file.write('COMPILE_FROM_C_ONLY')

            sdist.run(self)

            os.remove(SKIP_CYTHON_FILE)


DONT_CYTHONIZE_FOR = ('clean',)


class GSSAPIDistribution(Distribution, object):
    def run_command(self, command):
        self._last_run_command = command
        Distribution.run_command(self, command)

    @property
    def ext_modules(self):
        if SOURCE_EXT != 'pyx':
            return getattr(self, '_ext_modules', None)

        if getattr(self, '_ext_modules', None) is None:
            return None

        if getattr(self, '_last_run_command', None) in DONT_CYTHONIZE_FOR:
            return self._ext_modules

        if getattr(self, '_cythonized_ext_modules', None) is None:
            self._cythonized_ext_modules = cythonize(self._ext_modules)

        return self._cythonized_ext_modules

    @ext_modules.setter
    def ext_modules(self, mods):
        self._cythonized_ext_modules = None
        self._ext_modules = mods

    @ext_modules.deleter
    def ext_modules(self):
        del self._ext_modules
        del self._cythonized_ext_modules


# detect support
def main_file(module):
    return Extension('gssapi.raw.%s' % module,
                     extra_link_args=link_args,
                     extra_compile_args=compile_args,
                     library_dirs=library_dirs,
                     sources=['gssapi/raw/%s.%s' % (module, SOURCE_EXT)])


ENUM_EXTS = []


def extension_file(module, canary):
    if ENABLE_SUPPORT_DETECTION and not hasattr(GSSAPI_LIB, canary):
        print('Skipping the %s extension because it '
              'is not supported by your GSSAPI implementation...' % module)
        return None
    else:
        enum_ext_path = 'gssapi/raw/_enum_extensions/ext_%s.%s' % (module,
                                                                   SOURCE_EXT)
        if os.path.exists(enum_ext_path):
            ENUM_EXTS.append(
                Extension('gssapi.raw._enum_extensions.ext_%s' % module,
                          extra_link_args=link_args,
                          extra_compile_args=compile_args,
                          sources=[enum_ext_path],
                          library_dirs=library_dirs,
                          include_dirs=['gssapi/raw/']))

        return Extension('gssapi.raw.ext_%s' % module,
                         extra_link_args=link_args,
                         extra_compile_args=compile_args,
                         library_dirs=library_dirs,
                         sources=['gssapi/raw/ext_%s.%s' % (module,
                                                            SOURCE_EXT)])


def gssapi_modules(lst):
    # filter out missing files
    res = [mod for mod in lst if mod is not None]

    # add in supported mech files
    MECHS_SUPPORTED = os.environ.get('GSSAPI_MECHS', 'krb5').split(',')
    for mech in MECHS_SUPPORTED:
        res.append(Extension('gssapi.raw.mech_%s' % mech,
                             extra_link_args=link_args,
                             extra_compile_args=compile_args,
                             library_dirs=library_dirs,
                             sources=['gssapi/raw/mech_%s.%s' % (mech,
                                                                 SOURCE_EXT)]))

    # add in any present enum extension files
    res.extend(ENUM_EXTS)

    return res


long_desc = re.sub('\.\. role:: \w+\(code\)\s*\n\s*.+', '',
                   re.sub(r':(python|bash|code):', '',
                          re.sub(r'\.\. code-block:: \w+', '::',
                                 open('README.txt').read())))

install_requires = [
    'decorator',
    'six >= 1.4.0'
]
if sys.version_info < (3, 4):
    install_requires.append('enum34')

setup(
    name='gssapi',
    version='1.5.1',
    author='The Python GSSAPI Team',
    author_email='sross@redhat.com',
    packages=['gssapi', 'gssapi.raw', 'gssapi.raw._enum_extensions',
              'gssapi.tests'],
    description='Python GSSAPI Wrapper',
    long_description=long_desc,
    license='LICENSE.txt',
    url="https://github.com/pythongssapi/python-gssapi",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Cython',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    distclass=GSSAPIDistribution,
    cmdclass={'sdist': sdist_gssapi},
    ext_modules=gssapi_modules([
        main_file('misc'),
        main_file('exceptions'),
        main_file('creds'),
        main_file('names'),
        main_file('sec_contexts'),
        main_file('types'),
        main_file('message'),
        main_file('oids'),
        main_file('cython_converters'),
        main_file('chan_bindings'),
        extension_file('s4u', 'gss_acquire_cred_impersonate_name'),
        extension_file('cred_store', 'gss_store_cred_into'),
        extension_file('rfc5587', 'gss_indicate_mechs_by_attrs'),
        extension_file('rfc5588', 'gss_store_cred'),
        extension_file('rfc5801', 'gss_inquire_saslname_for_mech'),
        extension_file('cred_imp_exp', 'gss_import_cred'),
        extension_file('dce', 'gss_wrap_iov'),
        extension_file('iov_mic', 'gss_get_mic_iov'),
        extension_file('ggf', 'gss_inquire_sec_context_by_oid'),
        extension_file('set_cred_opt', 'gss_set_cred_option'),

        # see ext_rfc6680_comp_oid for more information on this split
        extension_file('rfc6680', 'gss_display_name_ext'),
        extension_file('rfc6680_comp_oid', 'GSS_C_NT_COMPOSITE_EXPORT'),

        # see ext_password{,_add}.pyx for more information on this split
        extension_file('password', 'gss_acquire_cred_with_password'),
        extension_file('password_add', 'gss_add_cred_with_password'),
    ]),
    keywords=['gssapi', 'security'],
    install_requires=install_requires
)
