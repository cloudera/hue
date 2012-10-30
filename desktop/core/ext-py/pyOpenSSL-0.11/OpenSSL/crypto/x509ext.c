/*
 * x509ext.c
 *
 * Copyright (C) Jean-Paul Calderone 2008, All rights reserved
 *
 * Export X.509 extension functions and data structures.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * @(#) $Id: x509ext.c,v 1.1 2002/07/09 13:34:46 martin Exp $
 */

#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

static char crypto_X509Extension_get_critical_doc[] = "\n\
Returns the critical field of the X509Extension\n\
\n\
@return: The critical field.\n\
";

static PyObject *
crypto_X509Extension_get_critical(crypto_X509ExtensionObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_critical"))
        return NULL;

    return PyLong_FromLong(X509_EXTENSION_get_critical(self->x509_extension));
}

static char crypto_X509Extension_get_short_name_doc[] = "\n\
Returns the short version of the type name of the X509Extension\n\
\n\
@return: The short type name.\n\
";

static PyObject *
crypto_X509Extension_get_short_name(crypto_X509ExtensionObj *self, PyObject *args) {
	ASN1_OBJECT *obj;
	const char *extname;

	if (!PyArg_ParseTuple(args, ":get_short_name")) {
		return NULL;
	}

	/* Returns an internal pointer to x509_extension, not a copy */
	obj = X509_EXTENSION_get_object(self->x509_extension);

	extname = OBJ_nid2sn(OBJ_obj2nid(obj));
	return PyBytes_FromString(extname);
}


/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_X509Extension_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
{ #name, (PyCFunction)crypto_X509Extension_##name, METH_VARARGS, crypto_X509Extension_##name##_doc }
static PyMethodDef crypto_X509Extension_methods[] =
{
    ADD_METHOD(get_critical),
    ADD_METHOD(get_short_name),
    { NULL, NULL }
};
#undef ADD_METHOD

/*
 * Constructor for X509Extension, never called by Python code directly
 *
 * Arguments: type_name - ???
 *            critical  - ???
 *            value     - ???
 *            subject   - An x509v3 certificate which is the subject for this extension.
 *            issuer    - An x509v3 certificate which is the issuer for this extension.
 * Returns:   The newly created X509Extension object
 */
crypto_X509ExtensionObj *
crypto_X509Extension_New(char *type_name, int critical, char *value,
                         crypto_X509Obj *subject, crypto_X509Obj  *issuer) {
    X509V3_CTX ctx;
    crypto_X509ExtensionObj *self;
    char* value_with_critical = NULL;


    /*
     * A context is necessary for any extension which uses the r2i conversion
     * method.  That is, X509V3_EXT_nconf may segfault if passed a NULL ctx.
     * Start off by initializing most of the fields to NULL.
     */
    X509V3_set_ctx(&ctx, NULL, NULL, NULL, NULL, 0);

    /*
     * We have no configuration database - but perhaps we should (some
     * extensions may require it).
     */
    X509V3_set_ctx_nodb(&ctx);

    /*
     * Initialize the subject and issuer, if appropriate.  ctx is a local, and
     * as far as I can tell none of the X509V3_* APIs invoked here steal any
     * references, so no need to incref subject or issuer.
     */
    if (subject) {
            ctx.subject_cert = subject->x509;
    }

    if (issuer) {
            ctx.issuer_cert = issuer->x509;
    }

    self = PyObject_New(crypto_X509ExtensionObj, &crypto_X509Extension_Type);

    if (self == NULL) {
	    goto error;
    }

    self->dealloc = 0;

    /* There are other OpenSSL APIs which would let us pass in critical
     * separately, but they're harder to use, and since value is already a pile
     * of crappy junk smuggling a ton of utterly important structured data,
     * what's the point of trying to avoid nasty stuff with strings? (However,
     * X509V3_EXT_i2d in particular seems like it would be a better API to
     * invoke.  I do not know where to get the ext_struc it desires for its
     * last parameter, though.) */
    value_with_critical = malloc(strlen("critical,") + strlen(value) + 1);
    if (!value_with_critical) {
	    goto critical_malloc_error;
    }

    if (critical) {
	    strcpy(value_with_critical, "critical,");
	    strcpy(value_with_critical + strlen("critical,"), value);
    } else {
	    strcpy(value_with_critical, value);
    }

    self->x509_extension = X509V3_EXT_nconf(
	    NULL, &ctx, type_name, value_with_critical);

    free(value_with_critical);

    if (!self->x509_extension) {
	    goto nconf_error;
    }

    self->dealloc = 1;
    return self;

  nconf_error:
    exception_from_error_queue(crypto_Error);

  critical_malloc_error:
    Py_XDECREF(self);

  error:
    return NULL;

}

static char crypto_X509Extension_doc[] = "\n\
X509Extension(typename, critical, value[, subject][, issuer]) -> \n\
                X509Extension instance\n\
\n\
@param typename: The name of the extension to create.\n\
@type typename: C{str}\n\
@param critical: A flag indicating whether this is a critical extension.\n\
@param value: The value of the extension.\n\
@type value: C{str}\n\
@param subject: Optional X509 cert to use as subject.\n\
@type subject: C{X509}\n\
@param issuer: Optional X509 cert to use as issuer.\n\
@type issuer: C{X509}\n\
@return: The X509Extension object\n\
";

static PyObject *
crypto_X509Extension_new(PyTypeObject *subtype, PyObject *args,
                         PyObject *kwargs) {
    char *type_name, *value;
    int critical = 0;
    crypto_X509Obj * subject = NULL;
    crypto_X509Obj * issuer = NULL;
    static char *kwlist[] = {"type_name", "critical", "value", "subject",
                             "issuer", NULL};

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs,
            BYTESTRING_FMT "i" BYTESTRING_FMT "|O!O!:X509Extension",
            kwlist, &type_name, &critical, &value,
            &crypto_X509_Type, &subject,
            &crypto_X509_Type, &issuer )) {
        return NULL;
    }

    return (PyObject *)crypto_X509Extension_New(type_name, critical, value,
                                                subject, issuer);
}

/*
 * Deallocate the memory used by the X509Extension object
 *
 * Arguments: self - The X509Extension object
 * Returns:   None
 */
static void
crypto_X509Extension_dealloc(crypto_X509ExtensionObj *self)
{
    /* Sometimes we don't have to dealloc this */
    if (self->dealloc)
        X509_EXTENSION_free(self->x509_extension);

    PyObject_Del(self);
}

/*
 * Print a nice text representation of the certificate request.
 */
static PyObject *
crypto_X509Extension_str(crypto_X509ExtensionObj *self)
{
    int str_len;
    char *tmp_str;
    PyObject *str;
    BIO *bio = BIO_new(BIO_s_mem());

    if (!X509V3_EXT_print(bio, self->x509_extension, 0, 0))
    {
        BIO_free(bio);
        exception_from_error_queue(crypto_Error);
        return NULL;
    }

    str_len = BIO_get_mem_data(bio, &tmp_str);
    str = PyText_FromStringAndSize(tmp_str, str_len);

    BIO_free(bio);

    return str;
}

PyTypeObject crypto_X509Extension_Type = {
    PyOpenSSL_HEAD_INIT(&PyType_Type, 0)
    "X509Extension",
    sizeof(crypto_X509ExtensionObj),
    0,
    (destructor)crypto_X509Extension_dealloc, 
    NULL, /* print */
    NULL, /* getattr */
    NULL, /* setattr  (setattrfunc)crypto_X509Name_setattr, */
    NULL, /* compare */
    NULL, /* repr */ 
    NULL, /* as_number */
    NULL, /* as_sequence */
    NULL, /* as_mapping */
    NULL, /* hash */
    NULL, /* call */
    (reprfunc)crypto_X509Extension_str, /* str */
    NULL, /* getattro */
    NULL, /* setattro */
    NULL, /* as_buffer */
    Py_TPFLAGS_DEFAULT,
    crypto_X509Extension_doc, /* doc */
    NULL, /* traverse */
    NULL, /* clear */
    NULL, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    crypto_X509Extension_methods, /* tp_methods */
    NULL, /* tp_members */
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    0, /* tp_dictoffset */
    NULL, /* tp_init */
    NULL, /* tp_alloc */
    crypto_X509Extension_new, /* tp_new */
};

/*
 * Initialize the X509Extension part of the crypto module
 *
 * Arguments: dict - The crypto module
 * Returns:   None
 */
int
init_crypto_x509extension(PyObject *module)
{
    if (PyType_Ready(&crypto_X509Extension_Type) < 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "X509Extension",
                           (PyObject *)&crypto_X509Extension_Type) != 0) {
        return 0;
    }

    if (PyModule_AddObject(module, "X509ExtensionType",
                           (PyObject *)&crypto_X509Extension_Type) != 0) {
        return 0;
    }

    return 1;
}
