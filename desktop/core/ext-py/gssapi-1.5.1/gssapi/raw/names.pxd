from gssapi.raw.cython_types cimport gss_name_t

cdef class Name:
    cdef gss_name_t raw_name
    cdef bint _free_on_dealloc
