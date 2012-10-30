#include <Python.h>
#define crypto_MODULE
#include "crypto.h"


static X509_REVOKED * X509_REVOKED_dup(X509_REVOKED *orig) {
    X509_REVOKED *dupe = NULL;

    dupe = X509_REVOKED_new();
    if (dupe == NULL) {
        return NULL;
    }
    if (orig->serialNumber) {
        dupe->serialNumber = M_ASN1_INTEGER_dup(orig->serialNumber); 
    }
    if (orig->revocationDate) {
        dupe->revocationDate = M_ASN1_INTEGER_dup(orig->revocationDate); 
    }
    if (orig->extensions) {
        STACK_OF(X509_EXTENSION) *sk = NULL;
        X509_EXTENSION * ext;
        int j;

        sk = sk_X509_EXTENSION_new_null();
        for (j = 0; j < sk_X509_EXTENSION_num(orig->extensions); j++) {
            ext = sk_X509_EXTENSION_value(orig->extensions, j);
            ext = X509_EXTENSION_dup(ext);
            sk_X509_EXTENSION_push(sk, ext);
        }
        dupe->extensions = sk;
    }
    dupe->sequence = orig->sequence;
    return dupe;
}

static char crypto_CRL_get_revoked_doc[] = "\n\
Return revoked portion of the CRL structure (by value\n\
not reference).\n\
\n\
@return: A tuple of Revoked objects.\n\
";
static PyObject *
crypto_CRL_get_revoked(crypto_CRLObj *self, PyObject *args) {
    int j, num_rev;
    X509_REVOKED *r = NULL;
    PyObject *obj = NULL, *rev_obj;

    if (!PyArg_ParseTuple(args, ":get_revoked")) {
        return NULL;
    }

    num_rev = sk_X509_REVOKED_num(self->crl->crl->revoked);
    if (num_rev < 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    if ((obj = PyTuple_New(num_rev)) == NULL) {
        return NULL;
    }

    for (j = 0; j < num_rev; j++) {
        r = sk_X509_REVOKED_value(self->crl->crl->revoked, j);
        r = X509_REVOKED_dup(r);
        if (r == NULL ) {
            goto error;
        }
        rev_obj = (PyObject *) crypto_Revoked_New(r);
        if (rev_obj == NULL) {
            goto error;
        }
        r = NULL; /* it's now owned by rev_obj */
        PyTuple_SET_ITEM(obj, j, rev_obj);
    }
    return obj;

 error:
    if (r) {
        X509_REVOKED_free(r);
    }
    Py_XDECREF(obj);
    return NULL;
}

static char crypto_CRL_add_revoked_doc[] = "\n\
Add a revoked (by value not reference) to the CRL structure\n\
\n\
@param cert: The new revoked.\n\
@type cert: L{X509}\n\
@return: None\n\
";
static PyObject *
crypto_CRL_add_revoked(crypto_CRLObj *self, PyObject *args, PyObject *keywds) {
    crypto_RevokedObj * rev_obj = NULL;
    static char *kwlist[] = {"revoked", NULL};
    X509_REVOKED * dup;

    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!:add_revoked", 
        kwlist, &crypto_Revoked_Type, &rev_obj)) {
        return NULL;
    }

    dup = X509_REVOKED_dup( rev_obj->revoked );
    if (dup == NULL) {
        return NULL;
    }
    X509_CRL_add0_revoked(self->crl, dup);

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_CRL_export_doc[] = "\n\
export(cert, key[, type[, days]]) -> export a CRL as a string\n\
\n\
@param cert: Used to sign CRL.\n\
@type cert: L{X509}\n\
@param key: Used to sign CRL.\n\
@type key: L{PKey}\n\
@param type: The export format, either L{FILETYPE_PEM}, L{FILETYPE_ASN1}, or L{FILETYPE_TEXT}.\n\
@param days: The number of days until the next update of this CRL.\n\
@type days: L{int}\n\
@return: L{str}\n\
";
static PyObject *
crypto_CRL_export(crypto_CRLObj *self, PyObject *args, PyObject *keywds) {
    int ret, buf_len, type = X509_FILETYPE_PEM, days = 100;
    char *temp;
    BIO *bio;
    PyObject *buffer;
    crypto_PKeyObj *key;
    ASN1_TIME *tmptm;
    crypto_X509Obj *x509;
    static char *kwlist[] = {"cert", "key", "type", "days", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!|ii:dump_crl", kwlist,
                                     &crypto_X509_Type, &x509, 
                                     &crypto_PKey_Type, &key, &type, &days)) {
        return NULL;
    }
    
    bio = BIO_new(BIO_s_mem());
    tmptm = ASN1_TIME_new();
    if (!tmptm) {
        return 0;
    }
    X509_gmtime_adj(tmptm,0);
    X509_CRL_set_lastUpdate(self->crl, tmptm);
    X509_gmtime_adj(tmptm,days*24*60*60);
    X509_CRL_set_nextUpdate(self->crl, tmptm);
    ASN1_TIME_free(tmptm);
    X509_CRL_set_issuer_name(self->crl, X509_get_subject_name(x509->x509));
    X509_CRL_sign(self->crl, key->pkey, EVP_md5());
    switch (type) {
        case X509_FILETYPE_PEM:
            ret = PEM_write_bio_X509_CRL(bio, self->crl);
            break;

        case X509_FILETYPE_ASN1:
            ret = (int) i2d_X509_CRL_bio(bio, self->crl);
            break;

        case X509_FILETYPE_TEXT:
            ret = X509_CRL_print(bio, self->crl);
            break;

        default:
            PyErr_SetString(
                PyExc_ValueError,
                "type argument must be FILETYPE_PEM, FILETYPE_ASN1, or FILETYPE_TEXT");
            return NULL;
    }
    if (!ret) {
        exception_from_error_queue(crypto_Error);
        BIO_free(bio);
        return NULL;
    }
    buf_len = BIO_get_mem_data(bio, &temp);
    buffer = PyBytes_FromStringAndSize(temp, buf_len);
    BIO_free(bio);
    return buffer;
}

crypto_CRLObj *
crypto_CRL_New(X509_CRL *crl) {
    crypto_CRLObj *self;

    self = PyObject_New(crypto_CRLObj, &crypto_CRL_Type);
    if (self == NULL) {
        return NULL;
    }
    self->crl = crl;
    return self;
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_CRL_name, METH_VARARGS, crypto_CRL_name_doc }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_CRL_##name, METH_VARARGS, crypto_CRL_##name##_doc }
#define ADD_KW_METHOD(name)        \
    { #name, (PyCFunction)crypto_CRL_##name, METH_VARARGS | METH_KEYWORDS, crypto_CRL_##name##_doc }
static PyMethodDef crypto_CRL_methods[] = {
    ADD_KW_METHOD(add_revoked),
    ADD_METHOD(get_revoked),
    ADD_KW_METHOD(export),
    { NULL, NULL }
};
#undef ADD_METHOD


static void
crypto_CRL_dealloc(crypto_CRLObj *self) {
    X509_CRL_free(self->crl);
    self->crl = NULL;

    PyObject_Del(self);
}

static char crypto_CRL_doc[] = "\n\
CRL() -> CRL instance\n\
\n\
Create a new empty CRL object.\n\
\n\
@returns: The CRL object\n\
";

static PyObject* crypto_CRL_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    if (!PyArg_ParseTuple(args, ":CRL")) {
        return NULL;
    }
    
    return (PyObject *)crypto_CRL_New(X509_CRL_new());
}

PyTypeObject crypto_CRL_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "CRL",
    sizeof(crypto_CRLObj),
    0,
    (destructor)crypto_CRL_dealloc,
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
    crypto_CRL_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_CRL_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_CRL_new, /* tp_new */
};

int init_crypto_crl(PyObject *module) {
       if (PyType_Ready(&crypto_CRL_Type) < 0) {
                  return 0;
       }

       if (PyModule_AddObject(module, "CRL", (PyObject *)&crypto_CRL_Type) != 0) {
                  return 0;
       }
       return 1;
}
