/*
 * pkcs7.c
 *
 * Copyright (C) AB Strakt
 * See LICENSE for details.
 *
 * PKCS7 handling code, mostly thin wrappers around OpenSSL.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

static char crypto_PKCS7_type_is_signed_doc[] = "\n\
Check if this NID_pkcs7_signed object\n\
\n\
@return: True if the PKCS7 is of type signed\n\
";

static PyObject *
crypto_PKCS7_type_is_signed(crypto_PKCS7Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type_is_signed")) 
        return NULL;

    if (PKCS7_type_is_signed(self->pkcs7))
        return PyLong_FromLong(1L);
    else
        return PyLong_FromLong(0L);
}

static char crypto_PKCS7_type_is_enveloped_doc[] = "\n\
Check if this NID_pkcs7_enveloped object\n\
\n\
@returns: True if the PKCS7 is of type enveloped\n\
";

static PyObject *
crypto_PKCS7_type_is_enveloped(crypto_PKCS7Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type_is_enveloped")) 
        return NULL;

    if (PKCS7_type_is_enveloped(self->pkcs7))
        return PyLong_FromLong(1L);
    else
        return PyLong_FromLong(0L);
}

static char crypto_PKCS7_type_is_signedAndEnveloped_doc[] = "\n\
Check if this NID_pkcs7_signedAndEnveloped object\n\
\n\
@returns: True if the PKCS7 is of type signedAndEnveloped\n\
";

static PyObject *
crypto_PKCS7_type_is_signedAndEnveloped(crypto_PKCS7Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type_is_signedAndEnveloped")) 
        return NULL;

    if (PKCS7_type_is_signedAndEnveloped(self->pkcs7))
        return PyLong_FromLong(1L);
    else
        return PyLong_FromLong(0L);
}

static char crypto_PKCS7_type_is_data_doc[] = "\n\
Check if this NID_pkcs7_data object\n\
\n\
@return: True if the PKCS7 is of type data\n\
";

static PyObject *
crypto_PKCS7_type_is_data(crypto_PKCS7Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type_is_data")) 
        return NULL;

    if (PKCS7_type_is_data(self->pkcs7))
        return PyLong_FromLong(1L);
    else
        return PyLong_FromLong(0L);
}

static char crypto_PKCS7_get_type_name_doc[] = "\n\
Returns the type name of the PKCS7 structure\n\
\n\
@return: A string with the typename\n\
";

static PyObject *
crypto_PKCS7_get_type_name(crypto_PKCS7Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_type_name")) 
        return NULL;

    /* 
     * return a string with the typename
     */
    return PyBytes_FromString(OBJ_nid2sn(OBJ_obj2nid(self->pkcs7->type)));
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_PKCS7_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_PKCS7_##name, METH_VARARGS, crypto_PKCS7_##name##_doc }
static PyMethodDef crypto_PKCS7_methods[] =
{
    ADD_METHOD(type_is_signed),
    ADD_METHOD(type_is_enveloped),
    ADD_METHOD(type_is_signedAndEnveloped),
    ADD_METHOD(type_is_data),
    ADD_METHOD(get_type_name),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for PKCS7 objects, never called by Python code directly
 *
 * Arguments: pkcs7    - A "real" pkcs7 certificate object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" pkcs7 object
 * Returns:   The newly created pkcs7 object
 */
crypto_PKCS7Obj *
crypto_PKCS7_New(PKCS7 *pkcs7, int dealloc)
{
    crypto_PKCS7Obj *self;

    self = PyObject_New(crypto_PKCS7Obj, &crypto_PKCS7_Type);

    if (self == NULL)
        return NULL;

    self->pkcs7 = pkcs7;
    self->dealloc = dealloc;

    return self;
}

/*
 * Deallocate the memory used by the PKCS7 object
 *
 * Arguments: self - The PKCS7 object
 * Returns:   None
 */
static void
crypto_PKCS7_dealloc(crypto_PKCS7Obj *self)
{
    /* Sometimes we don't have to dealloc the "real" PKCS7 pointer ourselves */
    if (self->dealloc)
        PKCS7_free(self->pkcs7);

    PyObject_Del(self);
}

PyTypeObject crypto_PKCS7_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "PKCS7",
    sizeof(crypto_PKCS7Obj),
    0,
    (destructor)crypto_PKCS7_dealloc,
    NULL, /* print */
    NULL, /* getattr */
    NULL, /* setattr */
    NULL, /* compare */
    NULL, /* repr */
    NULL, /* as_number */
    NULL, /* as_sequence */
    NULL, /* as_mapping */
    NULL, /* hash */
    NULL, /* call */
    NULL,  /* str */
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
    crypto_PKCS7_methods, /* tp_methods */
};

/*
 * Initialize the PKCS7 part of the crypto sub module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_pkcs7(PyObject *module) {
    if (PyType_Ready(&crypto_PKCS7_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&crypto_PKCS7_Type);
    if (PyModule_AddObject(module, "PKCS7Type", (PyObject *)&crypto_PKCS7_Type) != 0) {
        return 0;
    }

    return 1;
}

