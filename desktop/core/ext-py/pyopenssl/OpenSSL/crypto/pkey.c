/*
 * pkey.c
 *
 * Copyright (C) AB Strakt
 * Copyright (C) Jean-Paul Calderone
 * See LICENSE for details.
 *
 * Public/rivate key handling code, mostly thin wrappers around OpenSSL.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

/*
 * This is done every time something fails, so turning it into a macro is
 * really nice.
 *
 * Arguments:   None
 * Returns:     Doesn't return
 */
#define FAIL() \
do {                                    \
    exception_from_error_queue(crypto_Error); \
    return NULL;                        \
} while (0)
    

static char crypto_PKey_generate_key_doc[] = "\n\
Generate a key of a given type, with a given number of a bits\n\
\n\
@param type: The key type (TYPE_RSA or TYPE_DSA)\n\
@param bits: The number of bits\n\
@return: None\n\
";

static PyObject *
crypto_PKey_generate_key(crypto_PKeyObj *self, PyObject *args)
{
    int type, bits;
    RSA *rsa;
    DSA *dsa;

    if (!PyArg_ParseTuple(args, "ii:generate_key", &type, &bits))
        return NULL;

    switch (type)
    {
        case crypto_TYPE_RSA:
            if (bits <= 0) {
                PyErr_SetString(PyExc_ValueError, "Invalid number of bits");
                return NULL;
            }
            if ((rsa = RSA_generate_key(bits, 0x10001, NULL, NULL)) == NULL)
                FAIL();
            if (!EVP_PKEY_assign_RSA(self->pkey, rsa))
                FAIL();
	    break;

        case crypto_TYPE_DSA:
            if ((dsa = DSA_generate_parameters(bits, NULL, 0, NULL, NULL, NULL, NULL)) == NULL)
                FAIL();
            if (!DSA_generate_key(dsa))
                FAIL();
            if (!EVP_PKEY_assign_DSA(self->pkey, dsa))
                FAIL();
	    break;

        default:
	    PyErr_SetString(crypto_Error, "No such key type");
	    return NULL;

    }
    self->initialized = 1;
    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKey_bits_doc[] = "\n\
Returns the number of bits of the key\n\
\n\
@return: The number of bits of the key.\n\
";

static PyObject *
crypto_PKey_bits(crypto_PKeyObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":bits"))
        return NULL;

    return PyLong_FromLong(EVP_PKEY_bits(self->pkey));
}

static char crypto_PKey_type_doc[] = "\n\
Returns the type of the key\n\
\n\
@return: The type of the key.\n\
";

static PyObject *
crypto_PKey_type(crypto_PKeyObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type"))
        return NULL;

    return PyLong_FromLong(self->pkey->type);
}

static char crypto_PKey_check_doc[] = "\n\
Check the consistency of an RSA private key.\n\
\n\
@return: True if key is consistent.\n\
@raise Error: if the key is inconsistent.\n\
@raise TypeError: if the key is of a type which cannot be checked.\n\
    Only RSA keys can currently be checked.\n\
";

static PyObject *
crypto_PKey_check(crypto_PKeyObj *self, PyObject *args) {
    int r;

    if (!PyArg_ParseTuple(args, ":check")) {
        return NULL;
    }

    if (self->pkey->type == EVP_PKEY_RSA) {
        RSA *rsa;
        rsa = EVP_PKEY_get1_RSA(self->pkey);
        r = RSA_check_key(rsa);
        if (r == 1) {
            return PyBool_FromLong(1L);
        } else {
            FAIL();
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "key type unsupported");
        return NULL;
    }
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_PKey_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_PKey_##name, METH_VARARGS, crypto_PKey_##name##_doc }
static PyMethodDef crypto_PKey_methods[] =
{
    ADD_METHOD(generate_key),
    ADD_METHOD(bits),
    ADD_METHOD(type),
    ADD_METHOD(check),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for PKey objects, never called by Python code directly
 *
 * Arguments: pkey    - A "real" EVP_PKEY object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" EVP_PKEY object
 * Returns:   The newly created PKey object
 */
crypto_PKeyObj *
crypto_PKey_New(EVP_PKEY *pkey, int dealloc)
{
    crypto_PKeyObj *self;

    self = PyObject_New(crypto_PKeyObj, &crypto_PKey_Type);

    if (self == NULL)
        return NULL;

    self->pkey = pkey;
    self->dealloc = dealloc;
    self->only_public = 0;

    /*
     * Heuristic.  Most call-sites pass an initialized EVP_PKEY.  Not
     * necessarily the case that they will, though.  That's part of why this is
     * a hack. -exarkun
     */
    self->initialized = 1;

    return self;
}

static char crypto_PKey_doc[] = "\n\
PKey() -> PKey instance\n\
\n\
Create a new PKey object.\n\
\n\
@return: The PKey object\n\
";
static PyObject*
crypto_PKey_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    crypto_PKeyObj *self;

    if (!PyArg_ParseTuple(args, ":PKey")) {
        return NULL;
    }

    self = crypto_PKey_New(EVP_PKEY_new(), 1);
    if (self) {
	self->initialized = 0;
    }

    return (PyObject *)self;
}


/*
 * Deallocate the memory used by the PKey object
 *
 * Arguments: self - The PKey object
 * Returns:   None
 */
static void
crypto_PKey_dealloc(crypto_PKeyObj *self)
{
    /* Sometimes we don't have to dealloc the "real" EVP_PKEY pointer ourselves */
    if (self->dealloc)
        EVP_PKEY_free(self->pkey);

    PyObject_Del(self);
}

PyTypeObject crypto_PKey_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "OpenSSL.crypto.PKey",
    sizeof(crypto_PKeyObj),
    0,
    (destructor)crypto_PKey_dealloc,
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
    NULL, /* str */
    NULL, /* getattro */
    NULL, /* setattro */
    NULL, /* as_buffer */
    Py_TPFLAGS_DEFAULT,
    crypto_PKey_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_PKey_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_PKey_new, /* tp_new */
};


/*
 * Initialize the PKey part of the crypto sub module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_pkey(PyObject *module)
{
    if (PyType_Ready(&crypto_PKey_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&crypto_PKey_Type);
    if (PyModule_AddObject(module, "PKey", (PyObject *)&crypto_PKey_Type) != 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&crypto_PKey_Type);
    if (PyModule_AddObject(module, "PKeyType", (PyObject *)&crypto_PKey_Type) != 0) {
        return 0;
    }

    return 1;
}

