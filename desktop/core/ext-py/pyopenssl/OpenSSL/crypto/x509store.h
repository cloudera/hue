/*
 * x509store.h
 *
 * Copyright (C) AB Strakt
 * See LICENSE for details.
 *
 * Export X509 store functions and data structures.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#ifndef PyOpenSSL_SSL_X509STORE_H_
#define PyOpenSSL_SSL_X509STORE_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  int     init_crypto_x509store       (PyObject *);

extern  PyTypeObject      crypto_X509Store_Type;

#define crypto_X509Store_Check(v) ((v)->ob_type == &crypto_X509Store_Type)

typedef struct {
    PyObject_HEAD
    X509_STORE           *x509_store;
    int                  dealloc;
} crypto_X509StoreObj;


#endif
