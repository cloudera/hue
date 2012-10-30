/*
 * x509req.h
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * Export X509 request functions and data structures.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * @(#) $Id: x509req.h,v 1.6 2002/09/04 22:24:59 iko Exp $
 */
#ifndef PyOpenSSL_SSL_X509REQ_H_
#define PyOpenSSL_SSL_X509REQ_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  int       init_crypto_x509req   (PyObject *);

extern  PyTypeObject      crypto_X509Req_Type;

#define crypto_X509Req_Check(v) ((v)->ob_type == &crypto_X509Req_Type)

typedef struct {
    PyObject_HEAD
    X509_REQ            *x509_req;
    int                  dealloc;
} crypto_X509ReqObj;


#endif
