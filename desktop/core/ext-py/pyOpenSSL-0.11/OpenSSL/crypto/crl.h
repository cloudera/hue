#ifndef PyOpenSSL_crypto_CRL_H_
#define PyOpenSSL_crypto_CRL_H_

#include <Python.h>

extern  int       init_crypto_crl   (PyObject *);

extern  PyTypeObject      crypto_CRL_Type;

#define crypto_CRL_Check(v) ((v)->ob_type == &crypto_CRL_Type)

typedef struct {
    PyObject_HEAD
    X509_CRL *crl;
} crypto_CRLObj;

crypto_CRLObj * crypto_CRL_New(X509_CRL *crl);

#endif
