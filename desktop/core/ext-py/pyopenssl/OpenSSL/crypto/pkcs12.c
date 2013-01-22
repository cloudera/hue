/*
 * pkcs12.c
 *
 * Copyright (C) AB Strakt
 * See LICENSE for details.
 *
 * Certificate transport (PKCS12) handling code,
 * mostly thin wrappers around OpenSSL.
 * See the file RATIONALE for a short explanation of why
 * this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

/*
 * PKCS12 is a standard exchange format for digital certificates.
 * See e.g. the OpenSSL homepage http://www.openssl.org/ for more information
 */

static void crypto_PKCS12_dealloc(crypto_PKCS12Obj *self);
static int crypto_PKCS12_clear(crypto_PKCS12Obj *self);

static char crypto_PKCS12_get_certificate_doc[] = "\n\
Return certificate portion of the PKCS12 structure\n\
\n\
@return: X509 object containing the certificate\n\
";
static PyObject *
crypto_PKCS12_get_certificate(crypto_PKCS12Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_certificate"))
        return NULL;

    Py_INCREF(self->cert);
    return self->cert;
}

static char crypto_PKCS12_set_certificate_doc[] = "\n\
Replace the certificate portion of the PKCS12 structure\n\
\n\
@param cert: The new certificate.\n\
@type cert: L{X509} or L{NoneType}\n\
@return: None\n\
";
static PyObject *
crypto_PKCS12_set_certificate(crypto_PKCS12Obj *self, PyObject *args, PyObject *keywds) {
    PyObject *cert = NULL;
    static char *kwlist[] = {"cert", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:set_certificate",
        kwlist, &cert))
        return NULL;

    if (cert != Py_None && ! crypto_X509_Check(cert)) {
        PyErr_SetString(PyExc_TypeError, "cert must be type X509 or None");
        return NULL;
    }

    Py_INCREF(cert);  /* Make consistent before calling Py_DECREF() */
    Py_DECREF(self->cert);
    self->cert = cert;

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKCS12_get_privatekey_doc[] = "\n\
Return private key portion of the PKCS12 structure\n\
\n\
@returns: PKey object containing the private key\n\
";
static crypto_PKeyObj *
crypto_PKCS12_get_privatekey(crypto_PKCS12Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_privatekey"))
        return NULL;

    Py_INCREF(self->key);
    return (crypto_PKeyObj *) self->key;
}

static char crypto_PKCS12_set_privatekey_doc[] = "\n\
Replace or set the certificate portion of the PKCS12 structure\n\
\n\
@param pkey: The new private key.\n\
@type pkey: L{PKey}\n\
@return: None\n\
";
static PyObject *
crypto_PKCS12_set_privatekey(crypto_PKCS12Obj *self, PyObject *args, PyObject *keywds) {
    PyObject *pkey = NULL;
    static char *kwlist[] = {"pkey", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:set_privatekey",
        kwlist, &pkey))
        return NULL;

    if (pkey != Py_None && ! crypto_PKey_Check(pkey)) {
        PyErr_SetString(PyExc_TypeError, "pkey must be type X509 or None");
        return NULL;
    }

    Py_INCREF(pkey);  /* Make consistent before calling Py_DECREF() */
    Py_DECREF(self->key);
    self->key = pkey;

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKCS12_get_ca_certificates_doc[] = "\n\
Return CA certificates within of the PKCS12 object\n\
\n\
@return: A newly created tuple containing the CA certificates in the chain,\n\
         if any are present, or None if no CA certificates are present.\n\
";
static PyObject *
crypto_PKCS12_get_ca_certificates(crypto_PKCS12Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_ca_certificates"))
        return NULL;

    Py_INCREF(self->cacerts);
    return self->cacerts;
}

static char crypto_PKCS12_set_ca_certificates_doc[] = "\n\
Replace or set the CA certificates withing the PKCS12 object.\n\
\n\
@param cacerts: The new CA certificates.\n\
@type cacerts: Iterable of L{X509} or L{NoneType}\n\
@return: None\n\
";
static PyObject *
crypto_PKCS12_set_ca_certificates(crypto_PKCS12Obj *self, PyObject *args, PyObject *keywds)
{
    PyObject *obj;
    PyObject *cacerts;
    static char *kwlist[] = {"cacerts", NULL};
    int i, len; /* Py_ssize_t for Python 2.5+ */

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:set_ca_certificates",
        kwlist, &cacerts))
        return NULL;
    if (cacerts == Py_None) {
        Py_INCREF(cacerts);
    } else {
        /* It's iterable */
        cacerts = PySequence_Tuple(cacerts);
        if (cacerts == NULL) {
            return NULL;
        }
        len = PyTuple_Size(cacerts);

        /* Check is's a simple list filled only with X509 objects. */
        for (i = 0; i < len; i++) {
            obj = PyTuple_GetItem(cacerts, i);
            if (!crypto_X509_Check(obj)) {
                Py_DECREF(cacerts);
                PyErr_SetString(PyExc_TypeError, "iterable must only contain X509Type");
                return NULL;
            }
        }
    }

    Py_DECREF(self->cacerts);
    self->cacerts = cacerts;

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKCS12_get_friendlyname_doc[] = "\n\
Return friendly name portion of the PKCS12 structure\n\
\n\
@returns: String containing the friendlyname\n\
";
static PyObject *
crypto_PKCS12_get_friendlyname(crypto_PKCS12Obj *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ":get_friendlyname"))
        return NULL;

    Py_INCREF(self->friendlyname);
    return (PyObject *) self->friendlyname;
}

static char crypto_PKCS12_set_friendlyname_doc[] = "\n\
Replace or set the certificate portion of the PKCS12 structure\n\
\n\
@param name: The new friendly name.\n\
@type name: L{str}\n\
@return: None\n\
";
static PyObject *
crypto_PKCS12_set_friendlyname(crypto_PKCS12Obj *self, PyObject *args, PyObject *keywds) {
    PyObject *name = NULL;
    static char *kwlist[] = {"name", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O:set_friendlyname",
        kwlist, &name))
        return NULL;

    if (name != Py_None && ! PyBytes_CheckExact(name)) {
        PyErr_SetString(PyExc_TypeError, "name must be a byte string or None");
        return NULL;
    }

    Py_INCREF(name);  /* Make consistent before calling Py_DECREF() */
    Py_DECREF(self->friendlyname);
    self->friendlyname = name;

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKCS12_export_doc[] = "\n\
export([passphrase=None][, friendly_name=None][, iter=2048][, maciter=1]\n\
Dump a PKCS12 object as a string.  See also \"man PKCS12_create\".\n\
\n\
@param passphrase: used to encrypt the PKCS12\n\
@type passphrase: L{str}\n\
@param iter: How many times to repeat the encryption\n\
@type iter: L{int}\n\
@param maciter: How many times to repeat the MAC\n\
@type maciter: L{int}\n\
@return: The string containing the PKCS12\n\
";
static PyObject *
crypto_PKCS12_export(crypto_PKCS12Obj *self, PyObject *args, PyObject *keywds) {
    int i; /* Py_ssize_t for Python 2.5+ */
    PyObject *obj;
    int buf_len;
    PyObject *buffer;
    char *temp, *passphrase = NULL, *friendly_name = NULL;
    BIO *bio;
    PKCS12 *p12;
    EVP_PKEY *pkey = NULL;
    STACK_OF(X509) *cacerts = NULL;
    X509 *x509 = NULL;
    int iter = 0;  /* defaults to PKCS12_DEFAULT_ITER */
    int maciter = 0;
    static char *kwlist[] = {"passphrase", "iter", "maciter", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "|zii:export",
        kwlist, &passphrase, &iter, &maciter))
        return NULL;

    if (self->key != Py_None) {
        pkey = ((crypto_PKeyObj*) self->key)->pkey;
    }
    if (self->cert != Py_None) {
        x509 = ((crypto_X509Obj*) self->cert)->x509;
    }
    if (self->cacerts != Py_None) {
        cacerts = sk_X509_new_null();
        for (i = 0; i < PyTuple_Size(self->cacerts); i++) {  /* For each CA cert */
            obj = PySequence_GetItem(self->cacerts, i);
            /* assert(PyObject_IsInstance(obj, (PyObject *) &crypto_X509_Type )); */
            sk_X509_push(cacerts, (( crypto_X509Obj* ) obj)->x509);
            Py_DECREF(obj);
        }
    }
    if (self->friendlyname != Py_None) {
        friendly_name = PyBytes_AsString(self->friendlyname);
    }

    p12 = PKCS12_create(passphrase, friendly_name, pkey, x509, cacerts,
                        NID_pbe_WithSHA1And3_Key_TripleDES_CBC,
                        NID_pbe_WithSHA1And3_Key_TripleDES_CBC,
                        iter, maciter, 0);
    sk_X509_free(cacerts); /* NULL safe.  Free just the container. */
    if (p12 == NULL) {
        exception_from_error_queue(crypto_Error);
        return NULL;
    }
    bio = BIO_new(BIO_s_mem());
    i2d_PKCS12_bio(bio, p12);
    buf_len = BIO_get_mem_data(bio, &temp);
    buffer = PyBytes_FromStringAndSize(temp, buf_len);
    BIO_free(bio);
    return buffer;
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_PKCS12_name, METH_VARARGS, crypto_PKCS12_name_doc }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_PKCS12_##name, METH_VARARGS, crypto_PKCS12_##name##_doc }
#define ADD_KW_METHOD(name)        \
    { #name, (PyCFunction)crypto_PKCS12_##name, METH_VARARGS | METH_KEYWORDS, crypto_PKCS12_##name##_doc }
static PyMethodDef crypto_PKCS12_methods[] =
{
    ADD_METHOD(get_certificate),
    ADD_KW_METHOD(set_certificate),
    ADD_METHOD(get_privatekey),
    ADD_KW_METHOD(set_privatekey),
    ADD_METHOD(get_ca_certificates),
    ADD_KW_METHOD(set_ca_certificates),
    ADD_METHOD(get_friendlyname),
    ADD_KW_METHOD(set_friendlyname),
    ADD_KW_METHOD(export),
    { NULL, NULL }
};
#undef ADD_METHOD

/*
 * Constructor for PKCS12 objects, never called by Python code directly.
 * The strategy for this object is to create all the Python objects
 * corresponding to the cert/key/CA certs right away
 *
 * Arguments: p12        - A "real" PKCS12 object or NULL
 *            passphrase - Passphrase to use when decrypting the PKCS12 object
 * Returns:   The newly created PKCS12 object
 */
crypto_PKCS12Obj *
crypto_PKCS12_New(PKCS12 *p12, char *passphrase) {
    crypto_PKCS12Obj *self = NULL;
    PyObject *cacertobj = NULL;

    unsigned char *alias_str;
    int alias_len;

    X509 *cert = NULL;
    EVP_PKEY *pkey = NULL;
    STACK_OF(X509) *cacerts = NULL;

    int i, cacert_count = 0;

    /* allocate space for the CA cert stack */
    if((cacerts = sk_X509_new_null()) == NULL) {
        goto error;   /* out of memory? */
    }

    /* parse the PKCS12 lump */
    if (p12) {
        if (!PKCS12_parse(p12, passphrase, &pkey, &cert, &cacerts)) {
	    /*
             * If PKCS12_parse fails, and it allocated cacerts, it seems to
             * free cacerts, but not re-NULL the pointer.  Zounds!  Make sure
             * it is re-set to NULL here, else we'll have a double-free below.
             */
            cacerts = NULL;
            exception_from_error_queue(crypto_Error);
            goto error;
        } else {
	  /*
	   * OpenSSL 1.0.0 sometimes leaves an X509_check_private_key error in
	   * the queue for no particular reason.  This error isn't interesting
	   * to anyone outside this function.  It's not even interesting to
	   * us.  Get rid of it.
	   */
	  flush_error_queue();
	}
    }

    if (!(self = PyObject_GC_New(crypto_PKCS12Obj, &crypto_PKCS12_Type))) {
        goto error;
    }

    /* client certificate and friendlyName */
    if (cert == NULL) {
        Py_INCREF(Py_None);
        self->cert = Py_None;
        Py_INCREF(Py_None);
        self->friendlyname = Py_None;
    } else {
        if ((self->cert = (PyObject *)crypto_X509_New(cert, 1)) == NULL) {
            goto error;
        }

        /*  Now we need to extract the friendlyName of the PKCS12
         *  that was stored by PKCS_parse() in the alias of the
         *  certificate. */
        alias_str = X509_alias_get0(cert, &alias_len);
        if (alias_str) {
            self->friendlyname = Py_BuildValue(BYTESTRING_FMT "#", alias_str, alias_len);
            if (!self->friendlyname) {
                /*
                 * XXX Untested
                 */
                goto error;
            }
            /* success */
        } else {
            Py_INCREF(Py_None);
            self->friendlyname = Py_None;
        }
    }

    /* private key */
    if (pkey == NULL) {
        Py_INCREF(Py_None);
        self->key = Py_None;
    } else {
        if ((self->key = (PyObject *)crypto_PKey_New(pkey, 1)) == NULL)
            goto error;
    }

    /* CA certs */
    cacert_count = sk_X509_num(cacerts);
    if (cacert_count <= 0) {
        Py_INCREF(Py_None);
        self->cacerts = Py_None;
    } else {
        if ((self->cacerts = PyTuple_New(cacert_count)) == NULL) {
            goto error;
        }

        for (i = 0; i < cacert_count; i++) {
            cert = sk_X509_value(cacerts, i);
            if ((cacertobj = (PyObject *)crypto_X509_New(cert, 1)) == NULL) {
                goto error;
            }
            PyTuple_SET_ITEM(self->cacerts, i, cacertobj);
        }
    }

    sk_X509_free(cacerts); /* Don't free the certs, just the container. */
    PyObject_GC_Track(self);

    return self;

error:
    sk_X509_free(cacerts); /* NULL safe. Free just the container. */
    if (self) {
        crypto_PKCS12_clear(self);
        PyObject_GC_Del(self);
    }
    return NULL;
}

static char crypto_PKCS12_doc[] = "\n\
PKCS12() -> PKCS12 instance\n\
\n\
Create a new empty PKCS12 object.\n\
\n\
@returns: The PKCS12 object\n\
";
static PyObject *
crypto_PKCS12_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    if (!PyArg_ParseTuple(args, ":PKCS12")) {
        return NULL;
    }

    return (PyObject *)crypto_PKCS12_New(NULL, NULL);
}

/*
 * Call the visitproc on all contained objects.
 *
 * Arguments: self - The PKCS12 object
 *            visit - Function to call
 *            arg - Extra argument to visit
 * Returns:   0 if all goes well, otherwise the return code from the first
 *            call that gave non-zero result.
 */
static int
crypto_PKCS12_traverse(crypto_PKCS12Obj *self, visitproc visit, void *arg)
{
    int ret = 0;

    if (ret == 0 && self->cert != NULL)
        ret = visit(self->cert, arg);
    if (ret == 0 && self->key != NULL)
        ret = visit(self->key, arg);
    if (ret == 0 && self->cacerts != NULL)
        ret = visit(self->cacerts, arg);
    if (ret == 0 && self->friendlyname != NULL)
        ret = visit(self->friendlyname, arg);
    return ret;
}

/*
 * Decref all contained objects and zero the pointers.
 *
 * Arguments: self - The PKCS12 object
 * Returns:   Always 0.
 */
static int
crypto_PKCS12_clear(crypto_PKCS12Obj *self)
{
    Py_XDECREF(self->cert);
    self->cert = NULL;
    Py_XDECREF(self->key);
    self->key = NULL;
    Py_XDECREF(self->cacerts);
    self->cacerts = NULL;
    Py_XDECREF(self->friendlyname);
    self->friendlyname = NULL;
    return 0;
}

/*
 * Deallocate the memory used by the PKCS12 object
 *
 * Arguments: self - The PKCS12 object
 * Returns:   None
 */
static void
crypto_PKCS12_dealloc(crypto_PKCS12Obj *self)
{
    PyObject_GC_UnTrack(self);
    crypto_PKCS12_clear(self);
    PyObject_GC_Del(self);
}

PyTypeObject crypto_PKCS12_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "PKCS12",
    sizeof(crypto_PKCS12Obj),
    0,
    (destructor)crypto_PKCS12_dealloc,
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    crypto_PKCS12_doc,
    (traverseproc)crypto_PKCS12_traverse,
    (inquiry)crypto_PKCS12_clear,
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_PKCS12_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_PKCS12_new, /* tp_new */
};

/*
 * Initialize the PKCS12 part of the crypto sub module
 *
 * Arguments: module - The crypto module
 * Returns:   None
 */
int
init_crypto_pkcs12(PyObject *module) {
    if (PyType_Ready(&crypto_PKCS12_Type) < 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&crypto_PKCS12_Type);
    if (PyModule_AddObject(module, "PKCS12", (PyObject *)&crypto_PKCS12_Type) != 0) {
        return 0;
    }

    /* PyModule_AddObject steals a reference.
     */
    Py_INCREF((PyObject *)&crypto_PKCS12_Type);
    if (PyModule_AddObject(module, "PKCS12Type", (PyObject *)&crypto_PKCS12_Type) != 0) {
        return 0;
    }

    return 1;
}
