/*
 * ssl.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 * Copyright (C) Jean-Paul Calderone 2008, All rights reserved
 *
 * Main file of the SSL sub module.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>

#ifndef MS_WINDOWS
#  include <sys/socket.h>
#  include <netinet/in.h>
#  if !(defined(__BEOS__) || defined(__CYGWIN__))
#    include <netinet/tcp.h>
#  endif
#else
#  include <winsock.h>
#  include <wincrypt.h>
#endif

#define SSL_MODULE
#include "ssl.h"

static char ssl_doc[] = "\n\
Main file of the SSL sub module.\n\
See the file RATIONALE for a short explanation of why this module was written.\n\
";

crypto_X509Obj* (*new_x509)(X509*, int);
crypto_X509NameObj* (*new_x509name)(X509_NAME*, int);
crypto_X509StoreObj* (*new_x509store)(X509_STORE*, int);


#ifndef PY3
void **crypto_API;
#endif

int _pyOpenSSL_tstate_key;

/* Exceptions defined by the SSL submodule */
PyObject *ssl_Error,                   /* Base class              */
         *ssl_ZeroReturnError,         /* Used with SSL_get_error */
         *ssl_WantReadError,           /* ...                     */
         *ssl_WantWriteError,          /* ...                     */
         *ssl_WantX509LookupError,     /* ...                     */
         *ssl_SysCallError;            /* Uses (errno,errstr)     */


/* Methods in the OpenSSL.SSL module */
static PyMethodDef ssl_methods[] = {
    { NULL, NULL }
};

#ifdef PY3
static struct PyModuleDef sslmodule = {
    PyModuleDef_HEAD_INIT,
    "SSL",
    ssl_doc,
    -1,
    ssl_methods
};
#endif

/*
 * Initialize SSL sub module
 *
 * Arguments: None
 * Returns:   None
 */
PyOpenSSL_MODINIT(SSL) {
    PyObject *module;
#ifndef PY3
    static void *ssl_API[ssl_API_pointers];
    PyObject *ssl_api_object;

    import_crypto();

    new_x509 = crypto_X509_New;
    new_x509name = crypto_X509Name_New;
    new_x509store = crypto_X509Store_New;
#else
#   ifdef _WIN32
    HMODULE crypto = GetModuleHandle("crypto.pyd");
    if (crypto == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Unable to get crypto module");
        PyOpenSSL_MODRETURN(NULL);
    }

    new_x509 = (crypto_X509Obj* (*)(X509*, int))GetProcAddress(crypto, "crypto_X509_New");
    new_x509name = (crypto_X509NameObj* (*)(X509_NAME*, int))GetProcAddress(crypto, "crypto_X509Name_New");
    new_x509store = (crypto_X509StoreObj* (*)(X509_STORE*, int))GetProcAddress(crypto, "crypto_X509Store_New");
#   else
    new_x509 = crypto_X509_New;
    new_x509name = crypto_X509Name_New;
    new_x509store = crypto_X509Store_New;
#   endif
#endif

    SSL_library_init();
    ERR_load_SSL_strings();

#ifdef PY3
    module = PyModule_Create(&sslmodule);
#else
    module = Py_InitModule3("SSL", ssl_methods, ssl_doc);
#endif
    if (module == NULL) {
        PyOpenSSL_MODRETURN(NULL);
    }

#ifndef PY3
    /* Initialize the C API pointer array */
    ssl_API[ssl_Context_New_NUM]    = (void *)ssl_Context_New;
    ssl_API[ssl_Connection_New_NUM] = (void *)ssl_Connection_New;
    ssl_api_object = PyCObject_FromVoidPtr((void *)ssl_API, NULL);
    if (ssl_api_object != NULL)
        PyModule_AddObject(module, "_C_API", ssl_api_object);
#endif

    /* Exceptions */
/*
 * ADD_EXCEPTION(dict,name,base) expands to a correct Exception declaration,
 * inserting OpenSSL.SSL.name into dict, derviving the exception from base.
 */
#define ADD_EXCEPTION(_name, _base)                                    \
do {                                                                          \
    ssl_##_name = PyErr_NewException("OpenSSL.SSL."#_name, _base, NULL);\
    if (ssl_##_name == NULL)                                            \
        goto error;                                                           \
    if (PyModule_AddObject(module, #_name, ssl_##_name) != 0)           \
        goto error;                                                           \
} while (0)

    ssl_Error = PyErr_NewException("OpenSSL.SSL.Error", NULL, NULL);
    if (ssl_Error == NULL)
        goto error;
    if (PyModule_AddObject(module, "Error", ssl_Error) != 0)
        goto error;

    ADD_EXCEPTION(ZeroReturnError,     ssl_Error);
    ADD_EXCEPTION(WantReadError,       ssl_Error);
    ADD_EXCEPTION(WantWriteError,      ssl_Error);
    ADD_EXCEPTION(WantX509LookupError, ssl_Error);
    ADD_EXCEPTION(SysCallError,        ssl_Error);
#undef ADD_EXCEPTION

    /* Method constants */
    PyModule_AddIntConstant(module, "SSLv2_METHOD",  ssl_SSLv2_METHOD);
    PyModule_AddIntConstant(module, "SSLv3_METHOD",  ssl_SSLv3_METHOD);
    PyModule_AddIntConstant(module, "SSLv23_METHOD", ssl_SSLv23_METHOD);
    PyModule_AddIntConstant(module, "TLSv1_METHOD",  ssl_TLSv1_METHOD);

    /* Verify constants */
    PyModule_AddIntConstant(module, "VERIFY_NONE", SSL_VERIFY_NONE);
    PyModule_AddIntConstant(module, "VERIFY_PEER", SSL_VERIFY_PEER);
    PyModule_AddIntConstant(module, "VERIFY_FAIL_IF_NO_PEER_CERT",
                            SSL_VERIFY_FAIL_IF_NO_PEER_CERT);
    PyModule_AddIntConstant(module, "VERIFY_CLIENT_ONCE",
                            SSL_VERIFY_CLIENT_ONCE);

    /* File type constants */
    PyModule_AddIntConstant(module, "FILETYPE_PEM",  SSL_FILETYPE_PEM);
    PyModule_AddIntConstant(module, "FILETYPE_ASN1", SSL_FILETYPE_ASN1);

    /* SSL option constants */
    PyModule_AddIntConstant(module, "OP_SINGLE_DH_USE", SSL_OP_SINGLE_DH_USE);
    PyModule_AddIntConstant(module, "OP_EPHEMERAL_RSA", SSL_OP_EPHEMERAL_RSA);
    PyModule_AddIntConstant(module, "OP_NO_SSLv2", SSL_OP_NO_SSLv2);
    PyModule_AddIntConstant(module, "OP_NO_SSLv3", SSL_OP_NO_SSLv3);
    PyModule_AddIntConstant(module, "OP_NO_TLSv1", SSL_OP_NO_TLSv1);

    /* More SSL option constants */
    PyModule_AddIntConstant(module, "OP_MICROSOFT_SESS_ID_BUG", SSL_OP_MICROSOFT_SESS_ID_BUG);
    PyModule_AddIntConstant(module, "OP_NETSCAPE_CHALLENGE_BUG", SSL_OP_NETSCAPE_CHALLENGE_BUG);
    PyModule_AddIntConstant(module, "OP_NETSCAPE_REUSE_CIPHER_CHANGE_BUG", SSL_OP_NETSCAPE_REUSE_CIPHER_CHANGE_BUG);
    PyModule_AddIntConstant(module, "OP_SSLREF2_REUSE_CERT_TYPE_BUG", SSL_OP_SSLREF2_REUSE_CERT_TYPE_BUG);
    PyModule_AddIntConstant(module, "OP_MICROSOFT_BIG_SSLV3_BUFFER", SSL_OP_MICROSOFT_BIG_SSLV3_BUFFER);
    PyModule_AddIntConstant(module, "OP_MSIE_SSLV2_RSA_PADDING", SSL_OP_MSIE_SSLV2_RSA_PADDING);
    PyModule_AddIntConstant(module, "OP_SSLEAY_080_CLIENT_DH_BUG", SSL_OP_SSLEAY_080_CLIENT_DH_BUG);
    PyModule_AddIntConstant(module, "OP_TLS_D5_BUG", SSL_OP_TLS_D5_BUG);
    PyModule_AddIntConstant(module, "OP_TLS_BLOCK_PADDING_BUG", SSL_OP_TLS_BLOCK_PADDING_BUG);
    PyModule_AddIntConstant(module, "OP_DONT_INSERT_EMPTY_FRAGMENTS", SSL_OP_DONT_INSERT_EMPTY_FRAGMENTS);
    PyModule_AddIntConstant(module, "OP_ALL", SSL_OP_ALL);
    PyModule_AddIntConstant(module, "OP_CIPHER_SERVER_PREFERENCE", SSL_OP_CIPHER_SERVER_PREFERENCE);
    PyModule_AddIntConstant(module, "OP_TLS_ROLLBACK_BUG", SSL_OP_TLS_ROLLBACK_BUG);
    PyModule_AddIntConstant(module, "OP_PKCS1_CHECK_1", SSL_OP_PKCS1_CHECK_1);
    PyModule_AddIntConstant(module, "OP_PKCS1_CHECK_2", SSL_OP_PKCS1_CHECK_2);
    PyModule_AddIntConstant(module, "OP_NETSCAPE_CA_DN_BUG", SSL_OP_NETSCAPE_CA_DN_BUG);
    PyModule_AddIntConstant(module, "OP_NETSCAPE_DEMO_CIPHER_CHANGE_BUG", SSL_OP_NETSCAPE_DEMO_CIPHER_CHANGE_BUG);

    /* DTLS related options.  The first two of these were introduced in
     * 2005, the third in 2007.  To accomodate systems which are still using
     * older versions, make them optional. */
#ifdef SSL_OP_NO_QUERY_MTU
    PyModule_AddIntConstant(module, "OP_NO_QUERY_MTU", SSL_OP_NO_QUERY_MTU);
#endif
#ifdef SSL_OP_COOKIE_EXCHANGE
    PyModule_AddIntConstant(module, "OP_COOKIE_EXCHANGE", SSL_OP_COOKIE_EXCHANGE);
#endif
#ifdef SSL_OP_NO_TICKET
    PyModule_AddIntConstant(module, "OP_NO_TICKET", SSL_OP_NO_TICKET);
#endif

    /* For SSL_set_shutdown */
    PyModule_AddIntConstant(module, "SENT_SHUTDOWN", SSL_SENT_SHUTDOWN);
    PyModule_AddIntConstant(module, "RECEIVED_SHUTDOWN", SSL_RECEIVED_SHUTDOWN);

    if (!init_ssl_context(module))
        goto error;
    if (!init_ssl_connection(module))
        goto error;

#ifdef WITH_THREAD
    /*
     * Initialize this module's threading support structures.
     */
    _pyOpenSSL_tstate_key = PyThread_create_key();
#endif

    PyOpenSSL_MODRETURN(module);

error:
    PyOpenSSL_MODRETURN(NULL);
    ;
}
