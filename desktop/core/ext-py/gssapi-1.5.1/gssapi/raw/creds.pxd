from gssapi.raw.cython_types cimport gss_cred_id_t


cdef class Creds:
    cdef gss_cred_id_t raw_creds
    cdef bint _free_on_dealloc
