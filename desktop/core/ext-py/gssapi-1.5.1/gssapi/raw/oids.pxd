from gssapi.raw.cython_types cimport gss_OID_desc


cdef class OID:
    # NB(directxman12): this is a pointer, not a gss_OID_desc
    cdef gss_OID_desc raw_oid
    cdef bint _free_on_dealloc

    cdef int _copy_from(OID self, gss_OID_desc base) except -1
    cdef int _from_bytes(OID self, object elements) except -1
