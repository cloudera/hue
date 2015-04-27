/*
 * netscape_spki.c
 *
 * Copyright (C) Tollef Fog Heen
 * See LICENSE for details.
 *
 * Netscape SPKI handling, thin wrapper
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

/*
 * Constructor for Nestcape_SPKI, never called by Python code directly
 *
 * Arguments: name    - A "real" NetscapeSPKI object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" NetscapeSPKI object
 * Returns:   The newly created NetscapeSPKI object
 */
crypto_NetscapeSPKIObj *
crypto_NetscapeSPKI_New(NETSCAPE_SPKI *name, int dealloc)
{
    crypto_NetscapeSPKIObj *self;

    self = PyObject_New(crypto_NetscapeSPKIObj, &crypto_NetscapeSPKI_Type);

    if (self == NULL)
        return NULL;

    self->netscape_spki = name;
    self->dealloc = dealloc;

    return self;
}


static char crypto_NetscapeSPKI_doc[] = "\n\
NetscapeSPKI([enc]) -> NetscapeSPKI instance\n\
\n\
@param enc: Base64 encoded NetscapeSPKI object.\n\
@type enc: C{str}\n\
@return: The NetscapeSPKI object\n\
";

static PyObject *
crypto_NetscapeSPKI_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    char *enc = NULL;
    int enc_len = -1;
    NETSCAPE_SPKI *spki;

    if (!PyArg_ParseTuple(args, "|s#:NetscapeSPKI", &enc, &enc_len))
        return NULL;

    if (enc_len >= 0)
        spki = NETSCAPE_SPKI_b64_decode(enc, enc_len);
    else
        spki = NETSCAPE_SPKI_new();
    if (spki == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }
    return (PyObject *)crypto_NetscapeSPKI_New(spki, 1);
}


/*
 * Deallocate the memory used by the NetscapeSPKI object
 *
 * Arguments: self - The NetscapeSPKI object
 * Returns:   None
 */
static void
crypto_NetscapeSPKI_dealloc(crypto_NetscapeSPKIObj *self)
{
    /* Sometimes we don't have to dealloc this */
    if (self->dealloc)
        NETSCAPE_SPKI_free(self->netscape_spki);

    PyObject_Del(self);
}

static char crypto_NetscapeSPKI_sign_doc[] = "\n\
Sign the certificate request using the supplied key and digest\n\
\n\
@param pkey: The key to sign with\n\
@param digest: The message digest to use\n\
@return: None\n\
";

static PyObject *
crypto_NetscapeSPKI_sign(crypto_NetscapeSPKIObj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;
    char *digest_name;
    const EVP_MD *digest;

    if (!PyArg_ParseTuple(args, "O!s:sign", &crypto_PKey_Type, &pkey,
			  &digest_name))
        return NULL;

    if (pkey->only_public) {
	PyErr_SetString(PyExc_ValueError, "Key has only public part");
	return NULL;
    }

    if (!pkey->initialized) {
	PyErr_SetString(PyExc_ValueError, "Key is uninitialized");
	return NULL;
    }

    if ((digest = EVP_get_digestbyname(digest_name)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "No such digest method");
        return NULL;
    }

    if (!NETSCAPE_SPKI_sign(self->netscape_spki, pkey->pkey, digest))
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_NetscapeSPKI_verify_doc[] = "\n\
Verifies a certificate request using the supplied public key\n\
\n\
@param key: a public key\n\
@return: True if the signature is correct.\n\
@raise OpenSSL.crypto.Error: If the signature is invalid or there is a\n\
    problem verifying the signature.\n\
";

PyObject *
crypto_NetscapeSPKI_verify(crypto_NetscapeSPKIObj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;
    int answer;

    if (!PyArg_ParseTuple(args, "O!:verify", &crypto_PKey_Type, &pkey)) {
        return NULL;
    }

    if ((answer = NETSCAPE_SPKI_verify(self->netscape_spki, pkey->pkey)) <= 0) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return PyLong_FromLong((long)answer);
}

static char crypto_NetscapeSPKI_b64_encode_doc[] = "\n\
Generate a base64 encoded string from an SPKI\n\
\n\
@return: The base64 encoded string\n\
";

PyObject *
crypto_NetscapeSPKI_b64_encode(crypto_NetscapeSPKIObj *self, PyObject *args)
{
    char *str;

    if (!PyArg_ParseTuple(args, ":b64_encode"))
        return NULL;

    str = NETSCAPE_SPKI_b64_encode(self->netscape_spki);
    return PyBytes_FromString(str);
}


static char crypto_NetscapeSPKI_get_pubkey_doc[] = "\n\
Get the public key of the certificate\n\
\n\
@return: The public key\n\
";

static PyObject *
crypto_NetscapeSPKI_get_pubkey(crypto_NetscapeSPKIObj *self, PyObject *args)
{
    crypto_PKeyObj *crypto_PKey_New(EVP_PKEY *, int);
    EVP_PKEY *pkey;
    crypto_PKeyObj *py_pkey;

    if (!PyArg_ParseTuple(args, ":get_pubkey"))
        return NULL;

    if ((pkey = NETSCAPE_SPKI_get_pubkey(self->netscape_spki)) == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    py_pkey = crypto_PKey_New(pkey, 1);
    if (py_pkey != NULL) {
	py_pkey->only_public = 1;
    }
    return (PyObject *)py_pkey;
}

static char crypto_NetscapeSPKI_set_pubkey_doc[] = "\n\
Set the public key of the certificate\n\
\n\
@param pkey: The public key\n\
@return: None\n\
";

static PyObject *
crypto_NetscapeSPKI_set_pubkey(crypto_NetscapeSPKIObj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;

    if (!PyArg_ParseTuple(args, "O!:set_pubkey", &crypto_PKey_Type, &pkey))
        return NULL;

    if (!NETSCAPE_SPKI_set_pubkey(self->netscape_spki, pkey->pkey))
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_NetscapeSPKI_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_NetscapeSPKI_##name, METH_VARARGS, crypto_NetscapeSPKI_##name##_doc }
static PyMethodDef crypto_NetscapeSPKI_methods[] =
{
    ADD_METHOD(get_pubkey),
    ADD_METHOD(set_pubkey),
    ADD_METHOD(b64_encode),
    ADD_METHOD(sign),
    ADD_METHOD(verify),
    { NULL, NULL }
};
#undef ADD_METHOD

PyTypeObject crypto_NetscapeSPKI_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "NetscapeSPKI",
    sizeof(crypto_NetscapeSPKIObj),
    0,
    (destructor)crypto_NetscapeSPKI_dealloc,
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
    crypto_NetscapeSPKI_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_NetscapeSPKI_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_NetscapeSPKI_new, /* tp_new */
};


/*
 * Initialize the X509Name part of the crypto module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_netscape_spki(PyObject *module) {
    if (PyType_Ready(&crypto_NetscapeSPKI_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference
     */
    Py_INCREF((PyObject *)&crypto_NetscapeSPKI_Type);
    if (PyModule_AddObject(module, "NetscapeSPKI", (PyObject *)&crypto_NetscapeSPKI_Type) != 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference
     */
    Py_INCREF((PyObject *)&crypto_NetscapeSPKI_Type);
    if (PyModule_AddObject(module, "NetscapeSPKIType", (PyObject *)&crypto_NetscapeSPKI_Type) != 0) {
        return 0;
    }

    return 1;
}
