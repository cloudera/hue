/*
 * x509ext.h
 *
 * Copyright (C) Awanim
 * See LICENSE for details.
 *
 * Export X.509 extension functions and data structures.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#ifndef PyOpenSSL_crypto_X509EXTENSION_H_
#define PyOpenSSL_crypto_X509EXTENSION_H_

#include <Python.h>
#include <openssl/ssl.h>
#include <openssl/x509v3.h>

extern  int     init_crypto_x509extension       (PyObject *);

extern  PyTypeObject      crypto_X509Extension_Type;

#define crypto_X509Extension_Check(v) ( \
        PyObject_TypeCheck((v),         \
                           &crypto_X509Extension_Type))

typedef struct {
    PyObject_HEAD
    X509_EXTENSION       *x509_extension;
    int                  dealloc;
} crypto_X509ExtensionObj;

#endif

