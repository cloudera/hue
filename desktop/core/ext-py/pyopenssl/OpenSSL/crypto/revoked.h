#ifndef PyOpenSSL_crypto_REVOKED_H_
#define PyOpenSSL_crypto_REVOKED_H_

#include <Python.h>

extern  PyTypeObject      crypto_Revoked_Type;

#define crypto_Revoked_Check(v) ((v)->ob_type == &crypto_Revoked_Type)

typedef struct {
    PyObject_HEAD
    X509_REVOKED *revoked;
} crypto_RevokedObj;

extern  int       init_crypto_revoked   (PyObject *);
extern crypto_RevokedObj * crypto_Revoked_New(X509_REVOKED *revoked);

#endif
