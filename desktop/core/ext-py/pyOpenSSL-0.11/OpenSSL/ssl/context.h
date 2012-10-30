/*
 * context.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export SSL Context object data structures and functions.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 * @(#) $Id: context.h,v 1.6 2002/09/04 22:24:59 iko Exp $
 */
#ifndef PyOpenSSL_SSL_CONTEXT_H_
#define PyOpenSSL_SSL_CONTEXT_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  int                   init_ssl_context      (PyObject *);

extern  PyTypeObject      ssl_Context_Type;

#define ssl_Context_Check(v) ((v)->ob_type == &ssl_Context_Type)

typedef struct {
    PyObject_HEAD
    SSL_CTX             *ctx;
    PyObject            *passphrase_callback,
                        *passphrase_userdata,
                        *verify_callback,
                        *info_callback,
                        *app_data;
    PyThreadState       *tstate;
} ssl_ContextObj;

#define ssl_SSLv2_METHOD      (1)
#define ssl_SSLv3_METHOD      (2)
#define ssl_SSLv23_METHOD     (3)
#define ssl_TLSv1_METHOD      (4)


#endif
