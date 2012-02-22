/*
 * errors that arise from ldap use
 * Most errors become their own exception
 * See http://www.python-ldap.org/ for details.
 * $Id: errors.c,v 1.21 2009/04/17 12:19:09 stroeder Exp $ */

#include "common.h"
#include "errors.h"

/* the base exception class */

PyObject*
LDAPexception_class;

/* list of error objects */

#define LDAP_ERROR_MIN          LDAP_REFERRAL_LIMIT_EXCEEDED

#ifdef LDAP_PROXIED_AUTHORIZATION_DENIED
	#define LDAP_ERROR_MAX          LDAP_PROXIED_AUTHORIZATION_DENIED
#else
	#ifdef LDAP_ASSERTION_FAILED
		#define LDAP_ERROR_MAX          LDAP_ASSERTION_FAILED
	#else
		#define LDAP_ERROR_MAX          LDAP_OTHER
	#endif
#endif

#define LDAP_ERROR_OFFSET       -LDAP_ERROR_MIN

static PyObject* errobjects[ LDAP_ERROR_MAX-LDAP_ERROR_MIN+1 ];


/* Convert a bare LDAP error number into an exception */
PyObject*
LDAPerr(int errnum)
{
	if (errnum >= LDAP_ERROR_MIN && errnum <= LDAP_ERROR_MAX)
		PyErr_SetNone(errobjects[errnum+LDAP_ERROR_OFFSET]);
	else
		PyErr_SetObject(LDAPexception_class, 
		    Py_BuildValue("{s:i}", "errnum", errnum));
	return NULL;
}

/* Convert an LDAP error into an informative python exception */
PyObject*
LDAPerror( LDAP*l, char*msg ) 
{
	if (l == NULL) {
		PyErr_SetFromErrno( LDAPexception_class );
		return NULL;
	}
	else {
		int errnum, opt_errnum;
		PyObject *errobj;
		PyObject *info;
		PyObject *str;

		char *matched, *error;

		opt_errnum = ldap_get_option(l, LDAP_OPT_ERROR_NUMBER, &errnum);
		if (opt_errnum != LDAP_OPT_SUCCESS)
			errnum = opt_errnum;

		if (errnum == LDAP_NO_MEMORY)
			return PyErr_NoMemory();

		if (errnum >= LDAP_ERROR_MIN && errnum <= LDAP_ERROR_MAX)
			errobj = errobjects[errnum+LDAP_ERROR_OFFSET];
		else
			errobj = LDAPexception_class;
		
		info = PyDict_New();
		if (info == NULL)
			return NULL;

		str = PyString_FromString(ldap_err2string(errnum));
		if (str)
			PyDict_SetItemString( info, "desc", str );
		Py_XDECREF(str);

		if (ldap_get_option(l, LDAP_OPT_MATCHED_DN, &matched) >= 0
			&& matched != NULL) {
		    if (*matched != '\0') {
			str = PyString_FromString(matched);
			if (str)
			    PyDict_SetItemString( info, "matched", str );
			Py_XDECREF(str);
		    }
		    ldap_memfree(matched);
		}
		
		if (errnum == LDAP_REFERRAL) {
		    str = PyString_FromString(msg);
		    if (str)
			PyDict_SetItemString( info, "info", str );
		    Py_XDECREF(str);
		} else if (ldap_get_option(l, LDAP_OPT_ERROR_STRING, &error) >= 0
			&& error != NULL) {
		    if (error != '\0') {
			str = PyString_FromString(error);
			if (str)
			    PyDict_SetItemString( info, "info", str );
			Py_XDECREF(str);
		    }
		    ldap_memfree(error);
		}
		PyErr_SetObject( errobj, info );
		Py_DECREF(info);
		return NULL;
	}
}


/* initialisation */

void
LDAPinit_errors( PyObject*d ) {

        /* create the base exception class */
        LDAPexception_class = PyErr_NewException("ldap.LDAPError",
                                                  NULL,
                                                  NULL);
        PyDict_SetItemString( d, "LDAPError", LDAPexception_class );

	/* XXX - backward compatibility with pre-1.8 */
        PyDict_SetItemString( d, "error", LDAPexception_class );
	Py_DECREF( LDAPexception_class );

	/* create each LDAP error object */

#	define seterrobj2(n,o) \
		PyDict_SetItemString( d, #n, (errobjects[LDAP_##n+LDAP_ERROR_OFFSET] = o) )


#	define seterrobj(n) { \
		PyObject *e = PyErr_NewException("ldap." #n,		\
				  LDAPexception_class, NULL);		\
		seterrobj2(n, e);					\
		Py_INCREF(e);						\
	}

	seterrobj(ADMINLIMIT_EXCEEDED);
	seterrobj(AFFECTS_MULTIPLE_DSAS);
	seterrobj(ALIAS_DEREF_PROBLEM);
	seterrobj(ALIAS_PROBLEM);
	seterrobj(ALREADY_EXISTS);
	seterrobj(AUTH_UNKNOWN);
	seterrobj(BUSY);
	seterrobj(CLIENT_LOOP);
	seterrobj(COMPARE_FALSE);
	seterrobj(COMPARE_TRUE);
	seterrobj(CONFIDENTIALITY_REQUIRED);
	seterrobj(CONNECT_ERROR);
	seterrobj(CONSTRAINT_VIOLATION);
	seterrobj(CONTROL_NOT_FOUND);
	seterrobj(DECODING_ERROR);
	seterrobj(ENCODING_ERROR);
	seterrobj(FILTER_ERROR);
	seterrobj(INAPPROPRIATE_AUTH);
	seterrobj(INAPPROPRIATE_MATCHING);
	seterrobj(INSUFFICIENT_ACCESS);
	seterrobj(INVALID_CREDENTIALS);
	seterrobj(INVALID_DN_SYNTAX);
	seterrobj(INVALID_SYNTAX);
	seterrobj(IS_LEAF);
	seterrobj(LOCAL_ERROR);
	seterrobj(LOOP_DETECT);
	seterrobj(MORE_RESULTS_TO_RETURN);
	seterrobj(NAMING_VIOLATION);
	seterrobj(NO_OBJECT_CLASS_MODS);
	seterrobj(NOT_ALLOWED_ON_NONLEAF);
	seterrobj(NOT_ALLOWED_ON_RDN);
	seterrobj(NOT_SUPPORTED);
	seterrobj(NO_MEMORY);
	seterrobj(NO_OBJECT_CLASS_MODS);
	seterrobj(NO_RESULTS_RETURNED);
	seterrobj(NO_SUCH_ATTRIBUTE);
	seterrobj(NO_SUCH_OBJECT);
	seterrobj(OBJECT_CLASS_VIOLATION);
	seterrobj(OPERATIONS_ERROR);
	seterrobj(OTHER);
	seterrobj(PARAM_ERROR);
	seterrobj(PARTIAL_RESULTS);
	seterrobj(PROTOCOL_ERROR);
	seterrobj(REFERRAL);
	seterrobj(REFERRAL_LIMIT_EXCEEDED);
	seterrobj(RESULTS_TOO_LARGE);
	seterrobj(SASL_BIND_IN_PROGRESS);
	seterrobj(SERVER_DOWN);
	seterrobj(SIZELIMIT_EXCEEDED);
	seterrobj(STRONG_AUTH_NOT_SUPPORTED);
	seterrobj(STRONG_AUTH_REQUIRED);
	seterrobj(SUCCESS);
	seterrobj(TIMELIMIT_EXCEEDED);
	seterrobj(TIMEOUT);
	seterrobj(TYPE_OR_VALUE_EXISTS);
	seterrobj(UNAVAILABLE);
	seterrobj(UNAVAILABLE_CRITICAL_EXTENSION);
	seterrobj(UNDEFINED_TYPE);
	seterrobj(UNWILLING_TO_PERFORM);
	seterrobj(USER_CANCELLED);

#ifdef LDAP_API_FEATURE_CANCEL
	seterrobj(CANCELLED);
	seterrobj(NO_SUCH_OPERATION);
	seterrobj(TOO_LATE);
	seterrobj(CANNOT_CANCEL);
#endif

#ifdef LDAP_ASSERTION_FAILED
	seterrobj(ASSERTION_FAILED);
#endif

#ifdef LDAP_PROXIED_AUTHORIZATION_DENIED
  seterrobj(PROXIED_AUTHORIZATION_DENIED);
#endif

}
