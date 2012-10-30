/*
 * pkcs7.h
 *
 * Copyright (C) AB Strakt 2002, All rights reserved
 *
 * Export pkcs7 functions and data structure.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * @(#) $Id: pkcs7.h,v 1.2 2002/09/04 22:24:59 iko Exp $
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
