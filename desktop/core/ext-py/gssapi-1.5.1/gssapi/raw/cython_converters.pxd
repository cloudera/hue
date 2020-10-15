from libc.string cimport memcmp

from gssapi.raw.cython_types cimport gss_OID, gss_OID_set, gss_OID_desc
from gssapi.raw.cython_types cimport OM_uint32
from gssapi.raw.cython_types cimport GSS_C_INDEFINITE
from gssapi.raw.oids cimport OID

from gssapi.raw.types import MechType, NameType


cdef gss_OID_set c_get_mech_oid_set(object mechs)
cdef inline bint c_compare_oids(gss_OID a, gss_OID b)
cdef object c_create_oid_set(gss_OID_set mech_set, bint free=*)
cdef OID c_make_oid(gss_OID oid)

cdef inline OM_uint32 c_py_ttl_to_c(object ttl) except? 1:
    """Converts None to GSS_C_INDEFINITE, otherwise returns input."""
    if ttl is None:
        return GSS_C_INDEFINITE
    else:
        return <OM_uint32>ttl


cdef inline object c_c_ttl_to_py(OM_uint32 ttl):
    """Converts GSS_C_INDEFINITE to None, otherwise return input."""
    if ttl == GSS_C_INDEFINITE:
        return None
    else:
        return ttl


cdef inline bint c_compare_oids(gss_OID a, gss_OID b):
    """Compare two OIDs to see if they are the same."""

    return (a.length == b.length and
            not memcmp(a.elements, b.elements, a.length))
