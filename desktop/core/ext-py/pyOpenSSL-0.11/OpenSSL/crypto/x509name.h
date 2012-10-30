/*
 * x509name.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export X.509 name functions and data structures.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 *
 * @(#) $Id: x509name.h,v 1.8 2002/09/04 22:24:59 iko Exp $
 */
#ifndef PyOpenSSL_crypto_X509NAME_H_
#define PyOpenSSL_crypto_X509NAME_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  int     init_crypto_x509name       (PyObject *);

extern  PyTypeObject      crypto_X509Name_Type;

#define crypto_X509Name_Check(v) ((v)->ob_type == &crypto_X509Name_Type)

typedef struct {
    PyObject_HEAD
    X509_NAME           *x509_name;
    int                  dealloc;
    PyObject            *parent_cert;
} crypto_X509NameObj;


#endif
