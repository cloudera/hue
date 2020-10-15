"""Low-Level GSSAPI Bindings

The low-level API presents a series of methods designed
to closely mimic the C API presented in RFC 2744 and
associated RFCs.

In this API, classes are simply thin wrappers around C
constructs, and generally lack instance methods.  However,
classes will automatically free associated memory (so the
release_xyz methods are not necessary to call).

The core RFC 2744 components are organized into the following
submodules:

    gssapi.raw.names -- Names

    gssapi.raw.creds -- Credentials

    gssapi.raw.sec_contexts -- Security Contexts

    gssapi.raw.message -- Message encryption, decryption, etc

    gssapi.raw.misc -- Miscellaneous functions

    gssapi.raw.types -- Miscellaneous types (enums, etc)

    gssapi.raw.exceptions -- Exceptions

Additionally, a number of extensions may be present.  All extensions
are in modules of the form `gssapi.raw.ext_xyz`.

All available functions and classes can be accessed directly from this
module (`gssapi.raw`) -- it is unneccessary to directly import submodules.
"""


import pkgutil
import importlib

from gssapi.raw import _enum_extensions

# NB(directxman12): the enum extensions must be imported BEFORE ANYTHING ELSE!
for modinf in pkgutil.iter_modules(_enum_extensions.__path__):
    name = modinf[1]
    importlib.import_module('{0}._enum_extensions.{1}'.format(__name__, name))

del pkgutil
del importlib

from gssapi.raw.creds import *  # noqa
from gssapi.raw.message import *  # noqa
from gssapi.raw.misc import *  # noqa
from gssapi.raw.exceptions import *  # noqa
from gssapi.raw.names import *  # noqa
from gssapi.raw.sec_contexts import *  # noqa
from gssapi.raw.oids import *  # noqa
from gssapi.raw.types import *  # noqa
from gssapi.raw.chan_bindings import *  # noqa

# optional S4U support
try:
    from gssapi.raw.ext_s4u import *  # noqa
except ImportError:
    pass  # no s4u support in the system's GSSAPI library

# optional cred store support
try:
    from gssapi.raw.ext_cred_store import *  # noqa
except ImportError:
    pass

# optional RFC 5587 support
try:
    from gssapi.raw.ext_rfc5587 import *  # noqa
except ImportError:
    pass

# optional RFC 5588 support
try:
    from gssapi.raw.ext_rfc5588 import *  # noqa
except ImportError:
    pass

# optional RFC 5801 support
try:
    from gssapi.raw.ext_rfc5801 import *  # noqa
except ImportError:
    pass

try:
    from gssapi.raw.ext_cred_imp_exp import *  # noqa
except ImportError:
    pass

# optional KRB5 mech support
try:
    import gssapi.raw.mech_krb5  # noqa
except ImportError:
    pass

# optional password support
try:
    from gssapi.raw.ext_password import *  # noqa
    from gssapi.raw.ext_password_add import *  # noqa
except ImportError:
    pass

# optional DCE (IOV/AEAD) support
try:
    from gssapi.raw.ext_dce import *  # noqa
    # optional IOV MIC support (requires DCE support)
    from gssapi.raw.ext_iov_mic import *  # noqa
except ImportError:
    pass

# optional RFC 6680 support
try:
    from gssapi.raw.ext_rfc6680 import *  # noqa
    from gssapi.raw.ext_rfc6680_comp_oid import *  # noqa
except ImportError:
    pass

# optional Global Grid Forum support
try:
    from gssapi.raw.ext_ggf import *  # noqa
except ImportError:
    pass

# optional set_cred_option support
try:
    from gssapi.raw.ext_set_cred_opt import *  # noqa
except ImportError:
    pass
