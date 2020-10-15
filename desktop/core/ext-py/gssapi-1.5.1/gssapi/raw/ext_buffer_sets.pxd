from gssapi.raw.cython_types cimport *

cdef extern from "python_gssapi.h":
    ctypedef struct gss_buffer_set_desc:
        size_t count
        gss_buffer_desc *elements
    ctypedef gss_buffer_set_desc* gss_buffer_set_t

    gss_buffer_set_t GSS_C_NO_BUFFER_SET

    OM_uint32 gss_release_buffer_set(OM_uint32 *min_stat,
                                     gss_buffer_set_t *buffer_set) nogil
