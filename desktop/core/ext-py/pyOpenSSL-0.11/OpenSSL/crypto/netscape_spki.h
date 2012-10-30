/*
 * netscape_spki.h
 *
 * Copyright (C) Tollef Fog Heen 2003, All rights reserved
 *
 * Handle Netscape SPKI (challenge response) certificate requests.
 *
 *
 */
#ifndef PyOpenSSL_crypto_Netscape_SPKI_H_
#define PyOpenSSL_crypto_Netscape_SPKI_H_

#include <Python.h>
#include <openssl/ssl.h>

extern  int     init_crypto_netscape_spki       (PyObject *);

extern  PyTypeObject      crypto_NetscapeSPKI_Type;

#define crypto_NetscapeSPKI_Check(v) ((v)->ob_type == &crypto_NetscapeSPKI_Type)

typedef struct {
    PyObject_HEAD
    NETSCAPE_SPKI           *netscape_spki;
    int                  dealloc;
} crypto_NetscapeSPKIObj;


#endif
