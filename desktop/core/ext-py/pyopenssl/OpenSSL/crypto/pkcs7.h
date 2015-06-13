/*
 * pkcs7.h
 *
 * Copyright (C) AB Strakt
 * See LICENSE for details.
 *
 * Export pkcs7 functions and data structure.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#ifndef PyOpenSSL_crypto_PKCS7_H_
#define PyOpenSSL_crypto_PKCS7_H_

#include <Python.h>
#include <openssl/pkcs7.h>

extern  int       init_crypto_pkcs7   (PyObject *);

extern  PyTypeObject      crypto_PKCS7_Type;

#define crypto_PKCS7_Check(v) ((v)->ob_type == &crypto_PKCS7_Type)

typedef struct {
    PyObject_HEAD
    PKCS7                *pkcs7;
    int                  dealloc;
} crypto_PKCS7Obj;


#endif
