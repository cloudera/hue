from gssapi.raw.cython_types cimport gss_ctx_id_t

cdef class SecurityContext:
    cdef gss_ctx_id_t raw_ctx
    cdef bint _free_on_dealloc
