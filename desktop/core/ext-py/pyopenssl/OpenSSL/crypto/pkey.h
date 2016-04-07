/*
 * pkey.h
 *
 * Copyright (C) AB Strakt
 * Copyright (C) Jean-Paul Calderone
 * See LICENSE for details.
 *
 * Export pkey functions and data structure.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#ifndef PyOpenSSL_crypto_PKEY_H_
#define PyOpenSSL_crypto_PKEY_H_

extern  int       init_crypto_pkey   (PyObject *);

extern  PyTypeObject    crypto_PKey_Type;

#define crypto_PKey_Check(v) ((v)->ob_type == &crypto_PKey_Type)

typedef struct {
    PyObject_HEAD

    /*
     * A pointer to the underlying OpenSSL structure.
     */
    EVP_PKEY            *pkey;

    /*
     * A flag indicating the underlying pkey object has no private parts (so it
     * can't sign, for example).  This is a bit of a temporary hack.
     * Public-only should be represented as a different type. -exarkun
     */
    int                  only_public;

    /*
     * A flag indicating whether the underlying pkey object has no meaningful
     * data in it whatsoever.  This is a temporary hack.  It should be
     * impossible to create PKeys in an unusable state. -exarkun
     */
    int                  initialized;

    /*
     * A flag indicating whether pkey will be freed when this object is freed.
     */
    int                  dealloc;
} crypto_PKeyObj;

#define crypto_TYPE_RSA           EVP_PKEY_RSA
#define crypto_TYPE_DSA           EVP_PKEY_DSA

#endif
