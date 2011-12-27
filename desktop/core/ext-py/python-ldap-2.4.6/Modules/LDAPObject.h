/* See http://www.python-ldap.org/ for details.
 * $Id: LDAPObject.h,v 1.10 2009/04/17 12:19:09 stroeder Exp $ */

#ifndef __h_LDAPObject 
#define __h_LDAPObject 

#include "common.h"

#include "lber.h"
#include "ldap.h"
#if LDAP_API_VERSION < 2000
#error Current python-ldap requires OpenLDAP 2.x
#endif

#if PYTHON_API_VERSION < 1007
typedef PyObject*	_threadstate;
#else
typedef PyThreadState*	_threadstate;
#endif

typedef struct {
        PyObject_HEAD
	LDAP* ldap;
	_threadstate	_save; /* for thread saving on referrals */
	int valid;
} LDAPObject;

extern PyTypeObject LDAP_Type;
#define LDAPObject_Check(v)     ((v)->ob_type == &LDAP_Type)

extern LDAPObject *newLDAPObject( LDAP* );

/* macros to allow thread saving in the context of an LDAP connection */

#define LDAP_BEGIN_ALLOW_THREADS( l )                                   \
	{                                                               \
	  LDAPObject *lo = (l);                                         \
	  if (lo->_save != NULL)                                        \
	  	Py_FatalError( "saving thread twice?" );                \
	  lo->_save = PyEval_SaveThread();                              \
	}

#define LDAP_END_ALLOW_THREADS( l )                                     \
	{                                                               \
	  LDAPObject *lo = (l);                                         \
	  _threadstate _save = lo->_save;                               \
	  lo->_save = NULL;                                             \
	  PyEval_RestoreThread( _save );                                \
	}

#endif /* __h_LDAPObject */

