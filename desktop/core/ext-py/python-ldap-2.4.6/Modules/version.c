/* Set release version
 * See http://www.python-ldap.org/ for details.
 * $Id: version.c,v 1.4 2009/04/17 12:19:09 stroeder Exp $ */

#include "common.h"

#define _STR(x)	#x
#define STR(x)	_STR(x)

static char version_str[] = STR(LDAPMODULE_VERSION);

void
LDAPinit_version( PyObject* d ) 
{
	PyObject *version;

	version = PyString_FromString(version_str);
	PyDict_SetItemString( d, "__version__", version );
	Py_DECREF(version);
}
