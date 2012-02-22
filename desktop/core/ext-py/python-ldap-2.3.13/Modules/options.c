/* See http://www.python-ldap.org/ for details.
 * $Id: options.c,v 1.38 2010/10/01 18:23:18 stroeder Exp $ */

#include "common.h"
#include "errors.h"
#include "LDAPObject.h"
#include "ldapcontrol.h"
#include "options.h"

void
set_timeval_from_double( struct timeval *tv, double d ) {
	tv->tv_usec = (long) ( fmod(d, 1.0) * 1000000.0 );
	tv->tv_sec = (long) floor(d);
}

/**
 * Converts a return code from ldap_set_option() or ldap_get_option()
 * into a python error, and returns NULL.
 */
static PyObject *
option_error(int res, const char *fn)
{
    if (res == LDAP_OPT_ERROR)
        PyErr_SetString(PyExc_ValueError, "option error");
    else if (res == LDAP_PARAM_ERROR)
        PyErr_SetString(PyExc_ValueError, "parameter error");
    else if (res == LDAP_NO_MEMORY) 
        PyErr_NoMemory();
    else
        PyErr_Format(PyExc_SystemError, "error %d from %s", res, fn);
    return NULL;
}

/**
 * Sets an LDAP option.
 * Returns 0 on failure, 1 on success
 */
int
LDAP_set_option(LDAPObject *self, int option, PyObject *value)
{
    int res;
    int intval;
    double doubleval;
    char *strval;
    struct timeval tv;
    void *ptr;
    LDAP *ld;
    LDAPControl **controls = NULL;

    ld = self ? self->ldap : NULL;

    switch(option) {
    case LDAP_OPT_API_INFO:
    case LDAP_OPT_API_FEATURE_INFO:
#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SSF:
#endif
	    /* Read-only options */
	    PyErr_SetString(PyExc_ValueError, "read-only option");
	    return 0;
    case LDAP_OPT_REFERRALS:
    case LDAP_OPT_RESTART:
#ifdef LDAP_OPT_X_SASL_NOCANON
    case LDAP_OPT_X_SASL_NOCANON:
#endif
#ifdef LDAP_OPT_CONNECT_ASYNC
    case LDAP_OPT_CONNECT_ASYNC:
#endif
	    /* Truth-value options */
	    ptr = PyObject_IsTrue(value) ? LDAP_OPT_ON : LDAP_OPT_OFF;
	    break;

    case LDAP_OPT_DEREF:
    case LDAP_OPT_SIZELIMIT:
    case LDAP_OPT_TIMELIMIT:
    case LDAP_OPT_PROTOCOL_VERSION:
    case LDAP_OPT_ERROR_NUMBER:
    case LDAP_OPT_DEBUG_LEVEL:
#ifdef HAVE_TLS
    case LDAP_OPT_X_TLS:
    case LDAP_OPT_X_TLS_REQUIRE_CERT:
#ifdef LDAP_OPT_X_TLS_CRLCHECK
    case LDAP_OPT_X_TLS_CRLCHECK:
#endif
#ifdef LDAP_OPT_X_TLS_NEWCTX
    case LDAP_OPT_X_TLS_NEWCTX:
#endif
#ifdef LDAP_OPT_X_TLS_PROTOCOL_MIN
    case LDAP_OPT_X_TLS_PROTOCOL_MIN:
#endif
#endif
#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SSF_MIN:
    case LDAP_OPT_X_SASL_SSF_MAX:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_IDLE
    case LDAP_OPT_X_KEEPALIVE_IDLE:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_PROBES
    case LDAP_OPT_X_KEEPALIVE_PROBES:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_INTERVAL
    case LDAP_OPT_X_KEEPALIVE_INTERVAL:
#endif

	    /* integer value options */
	    if (!PyArg_Parse(value, "i:set_option", &intval))
		return 0;
	    ptr = &intval;
	    break;
    case LDAP_OPT_HOST_NAME:
    case LDAP_OPT_URI:
#ifdef LDAP_OPT_DEFBASE
    case LDAP_OPT_DEFBASE:
#endif
    case LDAP_OPT_ERROR_STRING:
    case LDAP_OPT_MATCHED_DN:
#ifdef HAVE_TLS
    case LDAP_OPT_X_TLS_CACERTFILE:
    case LDAP_OPT_X_TLS_CACERTDIR:
    case LDAP_OPT_X_TLS_CERTFILE:
    case LDAP_OPT_X_TLS_KEYFILE:
    case LDAP_OPT_X_TLS_CIPHER_SUITE:
    case LDAP_OPT_X_TLS_RANDOM_FILE:
    case LDAP_OPT_X_TLS_DHFILE:
#ifdef LDAP_OPT_X_TLS_CRLFILE
    case LDAP_OPT_X_TLS_CRLFILE:
#endif
#endif
#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SECPROPS:
#endif
	    /* String valued options */
	    if (!PyArg_Parse(value, "s:set_option", &strval))
		return 0;
	    ptr = strval;
	    break;
    case LDAP_OPT_TIMEOUT:
    case LDAP_OPT_NETWORK_TIMEOUT:
	    /* Float valued timeval options */
	    if (!PyArg_Parse(value, "d:set_option", &doubleval))
		return 0;
            if (doubleval >= 0) {
	        set_timeval_from_double( &tv, doubleval );
                ptr = &tv;
            } else {
    	        ptr = NULL;
            }
	    break;
    case LDAP_OPT_SERVER_CONTROLS:
    case LDAP_OPT_CLIENT_CONTROLS:
            if (!LDAPControls_from_object(value, &controls))
                return 0;
            ptr = controls;
            break;
    default:
	    PyErr_Format(PyExc_ValueError, "unknown option %d", option);
	    return 0;
    }
	
    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
    res = ldap_set_option(ld, option, ptr);
    if (self) LDAP_END_ALLOW_THREADS(self);

    if ((option == LDAP_OPT_SERVER_CONTROLS) || (option == LDAP_OPT_CLIENT_CONTROLS))
        LDAPControl_List_DEL(controls);
    
    if (res != LDAP_OPT_SUCCESS) {
        option_error(res, "ldap_set_option");
        return 0;
    }

    return 1;
}

PyObject *
LDAP_get_option(LDAPObject *self, int option)
{
    int res;
    int intval;
    struct timeval *tv;
    LDAPAPIInfo apiinfo;
    LDAPControl **lcs;
    LDAPControl *lc;
    char *strval;
    PyObject *extensions, *v, *tup;
    Py_ssize_t i, num_extensions, num_controls;
    LDAP *ld;

    ld = self ? self->ldap : NULL;

    switch(option) {
    case LDAP_OPT_API_INFO:
	    apiinfo.ldapai_info_version = LDAP_API_INFO_VERSION;
	    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
	    res = ldap_get_option( ld, option, &apiinfo );
	    if (self) LDAP_END_ALLOW_THREADS(self);
	    if (res != LDAP_OPT_SUCCESS)
		return option_error(res, "ldap_get_option");
    
	    /* put the extensions into tuple form */
	    num_extensions = 0;
	    while (apiinfo.ldapai_extensions[num_extensions])
		num_extensions++;
	    extensions = PyTuple_New(num_extensions);
	    for (i = 0; i < num_extensions; i++)
		PyTuple_SET_ITEM(extensions, i,
		    PyString_FromString(apiinfo.ldapai_extensions[i]));

	    /* return api info as a dictionary */
	    v = Py_BuildValue("{s:i, s:i, s:i, s:s, s:i, s:O}",
		    "info_version",     apiinfo.ldapai_info_version,
		    "api_version",      apiinfo.ldapai_api_version,
		    "protocol_version", apiinfo.ldapai_protocol_version,
		    "vendor_name",      apiinfo.ldapai_vendor_name,
		    "vendor_version",   apiinfo.ldapai_vendor_version,
		    "extensions",       extensions);

	    if (apiinfo.ldapai_vendor_name)
		ldap_memfree(apiinfo.ldapai_vendor_name);
	    for (i = 0; i < num_extensions; i++)
		ldap_memfree(apiinfo.ldapai_extensions[i]);
	    ldap_memfree(apiinfo.ldapai_extensions);
	    Py_DECREF(extensions);

	    return v;

#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SSF:
#endif
    case LDAP_OPT_REFERRALS:
    case LDAP_OPT_RESTART:
    case LDAP_OPT_DEREF:
    case LDAP_OPT_SIZELIMIT:
    case LDAP_OPT_TIMELIMIT:
    case LDAP_OPT_PROTOCOL_VERSION:
    case LDAP_OPT_ERROR_NUMBER:
    case LDAP_OPT_DEBUG_LEVEL:
#ifdef HAVE_TLS
    case LDAP_OPT_X_TLS:
    case LDAP_OPT_X_TLS_REQUIRE_CERT:
#ifdef LDAP_OPT_X_TLS_CRLCHECK
    case LDAP_OPT_X_TLS_CRLCHECK:
#endif
#ifdef LDAP_OPT_X_TLS_PROTOCOL_MIN
    case LDAP_OPT_X_TLS_PROTOCOL_MIN:
#endif
#endif
#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SSF_MIN:
    case LDAP_OPT_X_SASL_SSF_MAX:
#endif
#ifdef LDAP_OPT_X_SASL_NOCANON
    case LDAP_OPT_X_SASL_NOCANON:
#endif
#ifdef LDAP_OPT_CONNECT_ASYNC
    case LDAP_OPT_CONNECT_ASYNC:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_IDLE
    case LDAP_OPT_X_KEEPALIVE_IDLE:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_PROBES
    case LDAP_OPT_X_KEEPALIVE_PROBES:
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_INTERVAL
    case LDAP_OPT_X_KEEPALIVE_INTERVAL:
#endif
	    /* Integer-valued options */
	    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
	    res = ldap_get_option(ld, option, &intval);
	    if (self) LDAP_END_ALLOW_THREADS(self);
	    if (res != LDAP_OPT_SUCCESS)
		return option_error(res, "ldap_get_option");
	    return PyInt_FromLong(intval);

    case LDAP_OPT_HOST_NAME:
    case LDAP_OPT_URI:
#ifdef LDAP_OPT_DEFBASE
    case LDAP_OPT_DEFBASE:
#endif
    case LDAP_OPT_ERROR_STRING:
    case LDAP_OPT_MATCHED_DN:
#ifdef HAVE_TLS
    case LDAP_OPT_X_TLS_CACERTFILE:
    case LDAP_OPT_X_TLS_CACERTDIR:
    case LDAP_OPT_X_TLS_CERTFILE:
    case LDAP_OPT_X_TLS_KEYFILE:
    case LDAP_OPT_X_TLS_CIPHER_SUITE:
    case LDAP_OPT_X_TLS_RANDOM_FILE:
    case LDAP_OPT_X_TLS_DHFILE:
#ifdef LDAP_OPT_X_TLS_CRLFILE
    case LDAP_OPT_X_TLS_CRLFILE:
#endif
#endif
#ifdef HAVE_SASL
    case LDAP_OPT_X_SASL_SECPROPS:
    case LDAP_OPT_X_SASL_MECH:
    case LDAP_OPT_X_SASL_REALM:
    case LDAP_OPT_X_SASL_AUTHCID:
    case LDAP_OPT_X_SASL_AUTHZID:
#ifdef LDAP_OPT_X_SASL_USERNAME
    case LDAP_OPT_X_SASL_USERNAME:
#endif
#endif
	    /* String-valued options */
	    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
	    res = ldap_get_option(ld, option, &strval);
	    if (self) LDAP_END_ALLOW_THREADS(self);
	    if (res != LDAP_OPT_SUCCESS)
		return option_error(res, "ldap_get_option");
	    if (strval == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	    }
	    v = PyString_FromString(strval);
	    ldap_memfree(strval);
	    return v;

    case LDAP_OPT_TIMEOUT:
    case LDAP_OPT_NETWORK_TIMEOUT:
	    /* Double-valued timeval options */
	    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
	    res = ldap_get_option(ld, option, &tv);
	    if (self) LDAP_END_ALLOW_THREADS(self);
	    if (res != LDAP_OPT_SUCCESS)
		return option_error(res, "ldap_get_option");
	    if (tv == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	    }
	    v = PyFloat_FromDouble(
              (double) tv->tv_sec + ( (double) tv->tv_usec / 1000000.0 )
            );
	    ldap_memfree(tv);
	    return v;

    case LDAP_OPT_SERVER_CONTROLS:
    case LDAP_OPT_CLIENT_CONTROLS:
	    if (self) LDAP_BEGIN_ALLOW_THREADS(self);
	    res = ldap_get_option(ld, option, &lcs);
	    if (self) LDAP_END_ALLOW_THREADS(self);

	    if (res != LDAP_OPT_SUCCESS)
		return option_error(res, "ldap_get_option");

            if (lcs == NULL)
                return PyList_New(0);
            
            /* Get the number of controls */
            num_controls = 0;
            while (lcs[num_controls])
                num_controls++;

            /* We'll build a list of controls, with each control a tuple */
            v = PyList_New(num_controls);
            for (i = 0; i < num_controls; i++) {
                lc = lcs[i];
                tup = Py_BuildValue("(sbs)", 
                                    lc->ldctl_oid,
                                    lc->ldctl_iscritical,
                                    lc->ldctl_value.bv_val);
                PyList_SET_ITEM(v, i, tup);
            }
            
            ldap_controls_free(lcs);

            return v;
            
    default:
	    PyErr_Format(PyExc_ValueError, "unknown option %d", option);
	    return NULL;
    }
}
