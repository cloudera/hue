/*
 * x509store.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * X.509 Store handling, mostly thin wrapping.
 * See the file RATIONALE for a short explanation of why this module was written.
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

static char crypto_X509Store_add_cert_doc[] = "\n\
Add a certificate\n\
\n\
@param cert: The certificate to add\n\
@return: None\n\
";

static PyObject *
crypto_X509Store_add_cert(crypto_X509StoreObj *self, PyObject *args)
{
    crypto_X509Obj *cert;

    if (!PyArg_ParseTuple(args, "O!:add_cert", &crypto_X509_Type, &cert))
        return NULL;

    if (!X509_STORE_add_cert(self->x509_store, cert->x509))
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_X509Store_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_X509Store_##name, METH_VARARGS, crypto_X509Store_##name##_doc }
static PyMethodDef crypto_X509Store_methods[] =
{
    ADD_METHOD(add_cert),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for X509Store, never called by Python code directly
 *
 * Arguments: name    - A "real" X509_STORE object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" X509_STORE object
 * Returns:   The newly created X509Store object
 */
crypto_X509StoreObj *
crypto_X509Store_New(X509_STORE *store, int dealloc)
{
    crypto_X509StoreObj *self;

    self = PyObject_New(crypto_X509StoreObj, &crypto_X509Store_Type);

    if (self == NULL)
        return NULL;

    self->x509_store = store;
    self->dealloc = dealloc;

    return self;
}

/*
 * Deallocate the memory used by the X509Store object
 *
 * Arguments: self - The X509Store object
 * Returns:   None
 */
static void
crypto_X509Store_dealloc(crypto_X509StoreObj *self)
{
    /* Sometimes we don't have to dealloc this */
    if (self->dealloc)
        X509_STORE_free(self->x509_store);

    PyObject_Del(self);
}


PyTypeObject crypto_X509Store_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "X509Store",
    sizeof(crypto_X509StoreObj),
    0,
    (destructor)crypto_X509Store_dealloc,
    NULL, /* print */
    NULL, /* getattr */
    NULL, /* setattr */
    NULL, /* compare */
    NULL, /* repr */
    NULL, /* as_number */
    NULL, /* as_sequence */
    NULL, /* as_mapping */
    NULL,  /* hash */
    NULL, /* call */
    NULL, /* str */
    NULL, /* getattro */
    NULL, /* setattro */
    NULL, /* as_buffer */
    Py_TPFLAGS_DEFAULT,
    NULL, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_X509Store_methods, /* tp_methods */
};


/*
 * Initialize the X509Store part of the crypto module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_x509store(PyObject *module)
{
    if (PyType_Ready(&crypto_X509Store_Type) < 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "X509StoreType", (PyObject *)&crypto_X509Store_Type) != 0) {
        return 0;
    }

    return 1;
}
