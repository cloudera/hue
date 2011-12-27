/* Miscellaneous common routines
 * See http://www.python-ldap.org/ for details.
 * $Id: common.c,v 1.3 2009/04/17 12:19:09 stroeder Exp $ */

#include "common.h"

/* dynamically add the methods into the module dictionary d */

void
LDAPadd_methods( PyObject* d, PyMethodDef* methods ) 
{
    PyMethodDef *meth;

    for( meth = methods; meth->ml_meth; meth++ ) {
        PyObject *f = PyCFunction_New( meth, NULL );
        PyDict_SetItemString( d, meth->ml_name, f );
        Py_DECREF(f);
    }
}
