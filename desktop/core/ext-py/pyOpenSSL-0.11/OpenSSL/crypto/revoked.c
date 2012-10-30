#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

#ifdef _WIN32
#define strcasecmp(string1, string2) _stricmp(string1, string2)
#endif

/* http://www.openssl.org/docs/apps/x509v3_config.html#CRL_distribution_points_ */
/* which differs from crl_reasons of crypto/x509v3/v3_enum.c that matches */
/* OCSP_crl_reason_str.  We use the latter, just like the command line program.  */
static const char *crl_reasons[] = {
    "unspecified",
    "keyCompromise",
    "CACompromise",
    "affiliationChanged",
    "superseded",
    "cessationOfOperation",
    "certificateHold",
    NULL,
    "removeFromCRL",
};

#define NUM_REASONS (sizeof(crl_reasons) / sizeof(char *))

static char crypto_Revoked_all_reasons_doc[] = "\n\
Return a list of all the supported reason strings.\n\
\n\
@return: A list of reason strings.\n\
";
static PyObject *
crypto_Revoked_all_reasons(crypto_RevokedObj *self, PyObject *args) {
    PyObject *list, *str;
    int j;

    list = PyList_New(0);
    for (j = 0; j < NUM_REASONS; j++) {
        if(crl_reasons[j]) {
            str = PyBytes_FromString(crl_reasons[j]);
            PyList_Append(list, str);
            Py_DECREF(str);
        }
    }
    return list;
}

static PyObject *
X509_EXTENSION_value_to_PyString(X509_EXTENSION *ex) {
    BIO *bio = NULL;
    PyObject *str = NULL;
    int str_len;
    char *tmp_str;

    /* Create a openssl BIO buffer */
    bio = BIO_new(BIO_s_mem());
    if (bio == NULL) {
        goto err;
    }

    /* These are not the droids you are looking for. */
    if (!X509V3_EXT_print(bio, ex, 0, 0)) {
        if (M_ASN1_OCTET_STRING_print(bio, ex->value) == 0) {
            goto err;
        }
    }

    /* Convert to a Python string. */
    str_len = BIO_get_mem_data(bio, &tmp_str);
    str = PyBytes_FromStringAndSize(tmp_str, str_len);

    /* Cleanup */
    BIO_free(bio);
    return str;

 err:
    if (bio) {
        BIO_free(bio);
    }
    if (str) {
        Py_DECREF(str);
    }
    return NULL;
}

static void
delete_reason(STACK_OF(X509_EXTENSION) *sk) {
    X509_EXTENSION * ext;
    int j;

    for (j = 0; j < sk_X509_EXTENSION_num(sk); j++) {
         ext = sk_X509_EXTENSION_value(sk, j);
         if (OBJ_obj2nid(ext->object) == NID_crl_reason) {
             X509_EXTENSION_free(ext);
             (void) sk_X509_EXTENSION_delete(sk, j);
             break;
         }
    }
}

static int
reason_str_to_code(const char * reason_str) {
    int reason_code = -1, j;
    char *spaceless_reason, * sp;

    /*  Remove spaces so that the responses of
     *  get_reason() work in set_reason()  */
    if ((spaceless_reason = strdup(reason_str)) == NULL) {
        return -1;
    }

    while ((sp = strchr(spaceless_reason, ' '))) {
       memmove(sp, sp+1, strlen(sp));
    }

    for (j = 0; j < NUM_REASONS; j++) {
        if(crl_reasons[j] && !strcasecmp(spaceless_reason, crl_reasons[j])) {
            reason_code = j;
            break;
        }
    }
    free(spaceless_reason);
    return reason_code;
}


static char crypto_Revoked_set_reason_doc[] = "\n\
Set the reason of a Revoked object.\n\
\n\
@param reason: The reason string.\n\
@type reason: L{str}\n\
@return: None\n\
";
static PyObject *
crypto_Revoked_set_reason(crypto_RevokedObj *self, PyObject *args, PyObject *keywds) {
    static char *kwlist[] = {"reason", NULL};
    const char *reason_str = NULL;
    int reason_code;
    ASN1_ENUMERATED *rtmp = NULL;

    if (!PyArg_ParseTupleAndKeywords(
            args, keywds, "O&:set_reason", kwlist,
            crypto_byte_converter, &reason_str)) {
        return NULL;
    }

    if(reason_str == NULL) {
        delete_reason(self->revoked->extensions);
        goto done;
    }

    reason_code = reason_str_to_code(reason_str);
    if (reason_code == -1) {
        PyErr_SetString(PyExc_ValueError, "bad reason string");
        return NULL;
    }

    rtmp = ASN1_ENUMERATED_new();
    if (!rtmp || !ASN1_ENUMERATED_set(rtmp, reason_code)) {
        goto err;
    }
    delete_reason(self->revoked->extensions);
    if (!X509_REVOKED_add1_ext_i2d(self->revoked, NID_crl_reason, rtmp, 0, 0)) {
        goto err;
    }

 done:
    Py_INCREF(Py_None);
    return Py_None;

 err:
    exception_from_error_queue(crypto_Error);
    return NULL;
}


static char crypto_Revoked_get_reason_doc[] = "\n\
Return the reason of a Revoked object.\n\
\n\
@return: The reason as a string\n\
";
static PyObject *
crypto_Revoked_get_reason(crypto_RevokedObj *self, PyObject *args) {
    X509_EXTENSION * ext;
    int j;
    STACK_OF(X509_EXTENSION) *sk = NULL;

    if (!PyArg_ParseTuple(args, ":get_reason")) {
        return NULL;
    }

    sk = self->revoked->extensions;
    for (j = 0; j < sk_X509_EXTENSION_num(sk); j++) {
         ext = sk_X509_EXTENSION_value(sk, j);
         if (OBJ_obj2nid(ext->object) == NID_crl_reason) {
             return X509_EXTENSION_value_to_PyString(ext);
         }
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char crypto_Revoked_get_rev_date_doc[] = "\n\
Retrieve the revocation date\n\
\n\
@return: A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
";

static PyObject*
crypto_Revoked_get_rev_date(crypto_RevokedObj *self, PyObject *args) {
    /* returns a borrowed reference.  */
    return _get_asn1_time(
        ":get_rev_date", self->revoked->revocationDate, args);
}

static char crypto_Revoked_set_rev_date_doc[] = "\n\
Set the revocation timestamp\n\
\n\
@param when: A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
\n\
@return: None\n\
";

static PyObject*
crypto_Revoked_set_rev_date(crypto_RevokedObj *self, PyObject *args) {
    return _set_asn1_time(
        BYTESTRING_FMT ":set_rev_date", self->revoked->revocationDate, args);
}

/* The integer is converted to an upper-case hex string
 * without a '0x' prefix. */
static PyObject *
ASN1_INTEGER_to_PyString(ASN1_INTEGER *asn1_int) {
    BIO *bio = NULL;
    PyObject *str = NULL;
    int str_len;
    char *tmp_str;

    /* Create a openssl BIO buffer */
    bio = BIO_new(BIO_s_mem());
    if (bio == NULL) {
        goto err;
    }

    /* Write the integer to the BIO as a hex string. */
    if (i2a_ASN1_INTEGER(bio, asn1_int) < 0) {
        goto err;
    }

    /* Convert to a Python string. */
    str_len = BIO_get_mem_data(bio, &tmp_str);
    str = PyBytes_FromStringAndSize(tmp_str, str_len);

    /* Cleanup */
    BIO_free(bio);
    return str;

 err:
    if (bio) {
        BIO_free(bio);
    }
    if (str) {
        Py_DECREF(str);
    }
    return NULL;
}


static char crypto_Revoked_get_serial_doc[] = "\n\
Return the serial number of a Revoked structure\n\
\n\
@return: The serial number as a string\n\
";
static PyObject *
crypto_Revoked_get_serial(crypto_RevokedObj *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, ":get_serial")) {
        return NULL;
    }

    if (self->revoked->serialNumber == NULL) {
        /* never happens */
        Py_INCREF(Py_None);
        return Py_None;
    } else {
        return ASN1_INTEGER_to_PyString(self->revoked->serialNumber);
    }
}

static char crypto_Revoked_set_serial_doc[] = "\n\
Set the serial number of a revoked Revoked structure\n\
\n\
@param hex_str: The new serial number.\n\
@type hex_str: L{str}\n\
@return: None\n\
";
static PyObject *
crypto_Revoked_set_serial(crypto_RevokedObj *self, PyObject *args, PyObject *keywds) {
    static char *kwlist[] = {"hex_str", NULL};
    const char *hex_str = NULL;
    BIGNUM *serial = NULL;
    ASN1_INTEGER *tmpser = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, keywds, BYTESTRING_FMT ":set_serial",
                                     kwlist, &hex_str)) {
        return NULL;
    }

    if (!BN_hex2bn(&serial, hex_str) ) {
        PyErr_SetString(PyExc_ValueError, "bad hex string");
        return NULL;
    }

    tmpser = BN_to_ASN1_INTEGER(serial, NULL);
    BN_free(serial);
    serial = NULL;
    X509_REVOKED_set_serialNumber(self->revoked, tmpser);
    ASN1_INTEGER_free(tmpser);

    Py_INCREF(Py_None);
    return Py_None;
}


crypto_RevokedObj *
crypto_Revoked_New(X509_REVOKED *revoked) {
    crypto_RevokedObj *self;

    self = PyObject_New(crypto_RevokedObj, &crypto_Revoked_Type);
    if (self == NULL) {
        return NULL;
    }
    self->revoked = revoked;
    return self;
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_Revoked_name, METH_VARARGS, crypto_Revoked_name_doc }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_Revoked_##name, METH_VARARGS, crypto_Revoked_##name##_doc }
#define ADD_KW_METHOD(name)        \
    { #name, (PyCFunction)crypto_Revoked_##name, METH_VARARGS | METH_KEYWORDS, crypto_Revoked_##name##_doc }
static PyMethodDef crypto_Revoked_methods[] = {
    ADD_METHOD(all_reasons),
    ADD_METHOD(get_reason),
    ADD_KW_METHOD(set_reason),
    ADD_METHOD(get_rev_date),
    ADD_METHOD(set_rev_date),
    ADD_METHOD(get_serial),
    ADD_KW_METHOD(set_serial),
    { NULL, NULL }
};
#undef ADD_METHOD


static void
crypto_Revoked_dealloc(crypto_RevokedObj *self) {
    X509_REVOKED_free(self->revoked);
    self->revoked = NULL;

    PyObject_Del(self);
}

static char crypto_Revoked_doc[] = "\n\
Revoked() -> Revoked instance\n\
\n\
Create a new empty Revoked object.\n\
\n\
@returns: The Revoked object\n\
";

static PyObject* crypto_Revoked_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    if (!PyArg_ParseTuple(args, ":Revoked")) {
        return NULL;
    }

    return (PyObject *)crypto_Revoked_New(X509_REVOKED_new());
}

PyTypeObject crypto_Revoked_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "Revoked",
    sizeof(crypto_RevokedObj),
    0,
    (destructor)crypto_Revoked_dealloc,
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
    crypto_Revoked_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_Revoked_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_Revoked_new, /* tp_new */
};

int init_crypto_revoked(PyObject *module) {
    if(PyType_Ready(&crypto_Revoked_Type) < 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "Revoked", (PyObject *)&crypto_Revoked_Type) != 0) {
        return 0;
    }
    return 1;
}
