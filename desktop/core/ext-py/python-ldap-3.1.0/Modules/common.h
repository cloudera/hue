/* common utility macros
 * See https://www.python-ldap.org/ for details. */

#ifndef __h_common
#define __h_common

#define PY_SSIZE_T_CLEAN

#include "Python.h"

#if defined(HAVE_CONFIG_H)
#include "config.h"
#endif

#if defined(MS_WINDOWS)
#include <winsock.h>
#else /* unix */
#include <netdb.h>
#include <sys/time.h>
#include <sys/types.h>
#endif

#include <string.h>
#define streq( a, b ) \
	( (*(a)==*(b)) && 0==strcmp(a,b) )

extern PyObject *LDAPerror_TypeError(const char *, PyObject *);

void LDAPadd_methods(PyObject *d, PyMethodDef *methods);

#define PyNone_Check(o) ((o) == Py_None)

/* Py2/3 compatibility */
#if PY_VERSION_HEX >= 0x03000000
/* In Python 3, alias PyInt to PyLong */
#define PyInt_FromLong PyLong_FromLong
#endif

#endif /* __h_common_ */
