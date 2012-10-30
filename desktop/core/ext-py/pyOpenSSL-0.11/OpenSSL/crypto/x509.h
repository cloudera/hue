/*
 * x509.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export x509 functions and data structure.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 * @(#) $Id: x509.h,v 1.9 2002/09/04 22:24:59 iko Exp $
 */
#ifndef PyOpenSSL_crypto_X509_H_
#define PyOpenSSL_crypto_X509_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  PyTypeObject      crypto_X509_Type;

#define crypto_X509_Check(v) ((v)->ob_type == &crypto_X509_Type)

typedef struct {
    PyObject_HEAD
    X509                *x509;
    int                  dealloc;
} crypto_X509Obj;

PyObject* _set_asn1_time(char *format, ASN1_TIME* timestamp, PyObject *args);
PyObject* _get_asn1_time(char *format, ASN1_TIME* timestamp, PyObject *args);
extern  int       init_crypto_x509   (PyObject *);


#endif
