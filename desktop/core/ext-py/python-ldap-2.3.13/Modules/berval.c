/* See http://www.python-ldap.org/ for details.
 * $Id: berval.c,v 1.1 2009/08/17 01:49:47 leonard Exp $ */

#include "common.h"
#include "berval.h"

/*
 * Converts a Python object into a data for a berval structure.
 *
 * New memory is allocated, and the content of the object is copied into it.
 * Then the (pre-existing) berval structure's field are filled in with pointer
 * and length data.
 *
 * The source object must implement the buffer interface, or be None.
 * If the source object is None, bv->bv_val will be set to NULL and bv_len to 0.
 * Otherwise, bv->bv_val will be non-NULL (even for zero-length data).
 * This allows the caller to distinguish a None argument as something special.
 *
 * Returns 0 on failure, leaving *bv unchanged, and setting an error.
 * Returns 1 on success: the berval must be freed with LDAPberval_release().
 */
int
LDAPberval_from_object(PyObject *obj, struct berval *bv)
{
    const void *data;
    char *datacp;
    Py_ssize_t len;

    if (PyNone_Check(obj)) {
        bv->bv_len = 0;
        bv->bv_val = NULL;
        return 1;
    }

    if (!PyObject_AsReadBuffer(obj, &data, &len))
        return 0;

    datacp = PyMem_MALLOC(len ? len : 1);
    if (!datacp) {
        PyErr_NoMemory();
        return 0;
    }
    memcpy(datacp, data, len);

    bv->bv_len = len;
    bv->bv_val = datacp;
    return 1;
}

/*
 * Returns true if the object could be used to initialize a berval structure
 * with LDAPberval_from_object()
 */
int
LDAPberval_from_object_check(PyObject *obj)
{
    return PyNone_Check(obj) ||
           PyObject_CheckReadBuffer(obj);
}

/*
 * Releases memory allocated by LDAPberval_from_object().
 * Has no effect if the berval pointer is NULL or the berval data is NULL.
 */
void
LDAPberval_release(struct berval *bv) {
    if (bv && bv->bv_val) {
        PyMem_FREE(bv->bv_val);
        bv->bv_len = 0;
        bv->bv_val = NULL;
    }
}

/*
 * Copies out the data from a berval, and returns it as a new Python object,
 * Returns None if the berval pointer is NULL.
 *
 * Note that this function is not the exact inverse of LDAPberval_from_object
 * with regards to the NULL/None conversion.
 *
 * Returns a new Python object on success, or NULL on failure.
 */
PyObject *
LDAPberval_to_object(const struct berval *bv)
{
    PyObject *ret = NULL;

    if (!bv) {
        ret = Py_None;
        Py_INCREF(ret);
    }
    else {
        ret = PyString_FromStringAndSize(bv->bv_val, bv->bv_len);
    }

    return ret;
}
