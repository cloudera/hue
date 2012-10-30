/*
 * x509req.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 * Copyright (C) Jean-Paul Calderone 2008, All rights reserved
 *
 * X.509 Request handling, mostly thin wrapping.
 * See the file RATIONALE for a short explanation of why this module was written.
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"


static char crypto_X509Req_get_subject_doc[] = "\n\
Create an X509Name object for the subject of the certificate request\n\
\n\
@return: An X509Name object\n\
";

static PyObject *
crypto_X509Req_get_subject(crypto_X509ReqObj *self, PyObject *args)
{
    crypto_X509NameObj *crypto_X509Name_New(X509_NAME *, int);
    X509_NAME *name;
    crypto_X509NameObj* pyname;

    if (!PyArg_ParseTuple(args, ":get_subject"))
        return NULL;

    if ((name = X509_REQ_get_subject_name(self->x509_req)) == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }
    if ((pyname = crypto_X509Name_New(name, 0)) != NULL) {
	    pyname->parent_cert = (PyObject *)self;
	    Py_INCREF(self);
    }
    return (PyObject *)pyname;
}

static char crypto_X509Req_get_pubkey_doc[] = "\n\
Get the public key from the certificate request\n\
\n\
@return: The public key\n\
";

static PyObject *
crypto_X509Req_get_pubkey(crypto_X509ReqObj *self, PyObject *args)
{
    crypto_PKeyObj *crypto_PKey_New(EVP_PKEY *, int);
    EVP_PKEY *pkey;
    crypto_PKeyObj *py_pkey;

    if (!PyArg_ParseTuple(args, ":get_pubkey"))
        return NULL;

    if ((pkey = X509_REQ_get_pubkey(self->x509_req)) == NULL)
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

static char crypto_X509Req_set_pubkey_doc[] = "\n\
Set the public key of the certificate request\n\
\n\
@param pkey: The public key to use\n\
@return: None\n\
";

static PyObject *
crypto_X509Req_set_pubkey(crypto_X509ReqObj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;

    if (!PyArg_ParseTuple(args, "O!:set_pubkey", &crypto_PKey_Type, &pkey))
        return NULL;

    if (!X509_REQ_set_pubkey(self->x509_req, pkey->pkey))
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509Req_sign_doc[] = "\n\
Sign the certificate request using the supplied key and digest\n\
\n\
@param pkey: The key to sign with\n\
@param digest: The message digest to use\n\
@return: None\n\
";

static PyObject *
crypto_X509Req_sign(crypto_X509ReqObj *self, PyObject *args)
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

    if (!X509_REQ_sign(self->x509_req, pkey->pkey, digest))
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509Req_verify_doc[] = "\n\
Verifies a certificate request using the supplied public key\n\
\n\
@param key: a public key\n\
@return: True if the signature is correct.\n\
@raise OpenSSL.crypto.Error: If the signature is invalid or there is a\n\
    problem verifying the signature.\n\
";

PyObject *
crypto_X509Req_verify(crypto_X509ReqObj *self, PyObject *args)
{
    PyObject *obj;
    crypto_PKeyObj *key;
    int answer;

    if (!PyArg_ParseTuple(args, "O!:verify", &crypto_PKey_Type, &obj)) {
        return NULL;
    }

    key = (crypto_PKeyObj *)obj;

    if ((answer = X509_REQ_verify(self->x509_req, key->pkey)) <= 0) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    return PyLong_FromLong(answer);
}

static char crypto_X509Req_add_extensions_doc[] = "\n\
Add extensions to the request.\n\
\n\
@param extensions: a sequence of X509Extension objects\n\
@return: None\n\
";

static PyObject *
crypto_X509Req_add_extensions(crypto_X509ReqObj *self, PyObject *args)
{
    PyObject *extensions;
    crypto_X509ExtensionObj *ext;
    STACK_OF(X509_EXTENSION) *exts;
    int nr_of_extensions, i;

    if (!PyArg_ParseTuple(args, "O:add_extensions", &extensions))
        return NULL;

    if (!PySequence_Check(extensions))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a sequence");
        return NULL;
    }

    /* Make a STACK_OF(X509_EXTENSION) from sequence */
    if ((exts = sk_X509_EXTENSION_new_null()) == NULL)
    {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    /* Put the extensions in a stack */
    nr_of_extensions = PySequence_Length(extensions);

    for (i = 0; i < nr_of_extensions; i++)
    {
        ext = (crypto_X509ExtensionObj *)PySequence_GetItem(extensions, i);
	if (!(crypto_X509Extension_Check(ext)))
        {
            PyErr_SetString(PyExc_ValueError,
                            "One of the elements is not an X509Extension");
	    sk_X509_EXTENSION_free(exts);
            return NULL;
        }
        sk_X509_EXTENSION_push(exts, ext->x509_extension);
    }

    if (!X509_REQ_add_extensions(self->x509_req, exts))
    {
        sk_X509_EXTENSION_free(exts);
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    sk_X509_EXTENSION_free(exts);

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509Req_set_version_doc[] = "\n\
Set the version subfield (RFC 2459, section 4.1.2.1) of the certificate\n\
request.\n\
\n\
@param version: The version number\n\
@return: None\n\
";

static PyObject *
crypto_X509Req_set_version(crypto_X509ReqObj *self, PyObject *args)
{
    long version;

    if (!PyArg_ParseTuple(args, "l:set_version", &version)) {
        return NULL;
    }

    if (!X509_REQ_set_version(self->x509_req, version)) {
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509Req_get_version_doc[] = "\n\
Get the version subfield (RFC 2459, section 4.1.2.1) of the certificate\n\
request.\n\
\n\
@return: an integer giving the value of the version subfield\n\
";

static PyObject *
crypto_X509Req_get_version(crypto_X509ReqObj *self, PyObject *args)
{
    long version;

    if (!PyArg_ParseTuple(args, ":get_version")) {
        return NULL;
    }

    version = X509_REQ_get_version(self->x509_req);

    return PyLong_FromLong(version);
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_X509Req_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_X509Req_##name, METH_VARARGS, crypto_X509Req_##name##_doc }
static PyMethodDef crypto_X509Req_methods[] =
{
    ADD_METHOD(get_subject),
    ADD_METHOD(get_pubkey),
    ADD_METHOD(set_pubkey),
    ADD_METHOD(sign),
    ADD_METHOD(verify),
    ADD_METHOD(add_extensions),
    ADD_METHOD(set_version),
    ADD_METHOD(get_version),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for X509Req, never called by Python code directly
 *
 * Arguments: name    - A "real" X509_REQ object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" X509_REQ object
 * Returns:   The newly created X509Req object
 */
crypto_X509ReqObj *
crypto_X509Req_New(X509_REQ *req, int dealloc)
{
    crypto_X509ReqObj *self;

    self = PyObject_New(crypto_X509ReqObj, &crypto_X509Req_Type);

    if (self == NULL)
        return NULL;

    self->x509_req = req;
    self->dealloc = dealloc;

    return self;
}


static char crypto_X509Req_doc[] = "\n\
X509Req() -> X509Req instance\n\
\n\
Create a new X509Req object.\n\
\n\
@return: The X509Req object\n\
";

static PyObject *
crypto_X509Req_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    if (!PyArg_ParseTuple(args, ":X509Req")) {
        return NULL;
    }

    return (PyObject *)crypto_X509Req_New(X509_REQ_new(), 1);
}


/*
 * Deallocate the memory used by the X509Req object
 *
 * Arguments: self - The X509Req object
 * Returns:   None
 */
static void
crypto_X509Req_dealloc(crypto_X509ReqObj *self)
{
    /* Sometimes we don't have to dealloc this */
    if (self->dealloc)
        X509_REQ_free(self->x509_req);

    PyObject_Del(self);
}


PyTypeObject crypto_X509Req_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "X509Req",
    sizeof(crypto_X509ReqObj),
    0,
    (destructor)crypto_X509Req_dealloc,
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
    crypto_X509Req_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_X509Req_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_X509Req_new, /* tp_new */
};


/*
 * Initialize the X509Req part of the crypto module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_x509req(PyObject *module)
{
    if (PyType_Ready(&crypto_X509Req_Type) < 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "X509Req", (PyObject *)&crypto_X509Req_Type) != 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "X509ReqType", (PyObject *)&crypto_X509Req_Type) != 0) {
        return 0;
    }

    return 1;
}
