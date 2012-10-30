/*
 * pkcs12.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export PKCS12 functions and data structure.
 *
 * @(#) $$
 */
#ifndef PyOpenSSL_crypto_PKCS12_H_
#define PyOpenSSL_crypto_PKCS12_H_

#include <Python.h>
#include <openssl/pkcs12.h>
#include <openssl/asn1.h>

extern  int       init_crypto_pkcs12   (PyObject *);

extern  PyTypeObject      crypto_PKCS12_Type;

#define crypto_PKCS12_Check(v) ((v)->ob_type == &crypto_PKCS12_Type)

typedef struct {
    PyObject_HEAD
    /*
     * These either refer to a PyObject* of the appropriate type, or Py_None if
     * they don't have a value.  They aren't set to NULL except during
     * finalization.
     */
    PyObject            *cert;
    PyObject            *key;
    PyObject            *cacerts;
    PyObject            *friendlyname;
} crypto_PKCS12Obj;

crypto_PKCS12Obj *
crypto_PKCS12_New(PKCS12 *p12, char *passphrase);

#endif
