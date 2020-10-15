from libc.stdlib cimport malloc, free

from gssapi.raw.cython_types cimport *

cdef class ChannelBindings:
    cdef public object initiator_address_type
    cdef public bytes initiator_address

    cdef public object acceptor_address_type
    cdef public bytes acceptor_address

    cdef public bytes application_data

    cdef gss_channel_bindings_t __cvalue__(ChannelBindings self) except NULL
