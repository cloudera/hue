from gssapi.raw.cython_types cimport gss_buffer_desc, OM_uint32

cdef extern from "python_gssapi_ext.h":
    ctypedef struct gss_iov_buffer_desc:
        OM_uint32 type
        gss_buffer_desc buffer
    ctypedef gss_iov_buffer_desc* gss_iov_buffer_t

cdef class IOV:
    cdef int iov_len
    cdef bint c_changed

    cdef bint _unprocessed
    cdef list _buffs
    cdef gss_iov_buffer_desc *_iov

    cdef gss_iov_buffer_desc* __cvalue__(IOV self) except NULL
    cdef _recreate_python_values(IOV self)
