"""High-Level GSSAPI Bindings

The high-level API contains three main classes, which represent
the primary abstractions that GSSAPI provides:

    Name (see gssapi.names)

    Credentials (see gssapi.creds)

    SecurityContext (see gssapi.sec_contexts)

Additionally, a number of helper classes shared with the low-level API
exist as well:

    Enums (see gssapi.raw.types) --
        NameType, RequirementFlag, AddressType, MechType

    IntEnumFlagSet (see gssapi.raw.types)

    OID (see gssapi.raw.oids)

Note:

    Classes in the high-level API inherit from the corresponding
    classes in the low-level API, and thus may be passed in to
    low-level API functions.
"""

from gssapi.raw.types import NameType, RequirementFlag, AddressType  # noqa
from gssapi.raw.types import MechType, IntEnumFlagSet  # noqa
from gssapi.raw.oids import OID  # noqa

from gssapi.creds import Credentials  # noqa
from gssapi.names import Name  # noqa
from gssapi.sec_contexts import SecurityContext  # noqa

from gssapi._utils import set_encoding  # noqa
