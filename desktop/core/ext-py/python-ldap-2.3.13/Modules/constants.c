/* constants defined for LDAP
 * See http://www.python-ldap.org/ for details.
 * $Id: constants.c,v 1.49 2010/10/01 18:23:18 stroeder Exp $ */

#include "common.h"
#include "constants.h"
#include "lber.h"
#include "ldap.h"

static PyObject* reverse;
static PyObject* forward;

/* convert an result integer into a Python string */

PyObject*
LDAPconstant( int val ) {
    PyObject *i = PyInt_FromLong( val );
    PyObject *s = PyObject_GetItem( reverse, i );
    if (s == NULL) {
    	PyErr_Clear();
	return i;
    }
    Py_DECREF(i);
    return s;
}

/* initialise the module constants */

void
LDAPinit_constants( PyObject* d )
{
	PyObject *zero, *author,*obj;

	reverse = PyDict_New();
	forward = PyDict_New();
	
	PyDict_SetItemString( d, "_reverse", reverse );
	PyDict_SetItemString( d, "_forward", forward );

#define add_int(d, name)                                                \
	{								\
		PyObject *i = PyInt_FromLong(LDAP_##name);		\
		PyDict_SetItemString( d, #name, i );			\
		Py_DECREF(i);						\
	}

	/* simple constants */

	add_int(d,API_VERSION);
	add_int(d,VENDOR_VERSION);

        add_int(d,PORT);
	add_int(d,VERSION1);
	add_int(d,VERSION2);
	add_int(d,VERSION3);
	add_int(d,VERSION_MIN);
	add_int(d,VERSION);
	add_int(d,VERSION_MAX);
	add_int(d,TAG_MESSAGE);
	add_int(d,TAG_MSGID);

	add_int(d,REQ_BIND);
	add_int(d,REQ_UNBIND);
	add_int(d,REQ_SEARCH);
	add_int(d,REQ_MODIFY);
	add_int(d,REQ_ADD);
	add_int(d,REQ_DELETE);
	add_int(d,REQ_MODRDN);
	add_int(d,REQ_COMPARE);
	add_int(d,REQ_ABANDON);

	add_int(d,TAG_LDAPDN);
	add_int(d,TAG_LDAPCRED);
	add_int(d,TAG_CONTROLS);
	add_int(d,TAG_REFERRAL);

	add_int(d,REQ_EXTENDED);
#if LDAP_API_VERSION >= 2004
	add_int(d,TAG_NEWSUPERIOR);
	add_int(d,TAG_EXOP_REQ_OID);
	add_int(d,TAG_EXOP_REQ_VALUE);
	add_int(d,TAG_EXOP_RES_OID);
	add_int(d,TAG_EXOP_RES_VALUE);
#ifdef HAVE_SASL
	add_int(d,TAG_SASL_RES_CREDS);
#endif
#endif

	add_int(d,SASL_AUTOMATIC);
	add_int(d,SASL_INTERACTIVE);
	add_int(d,SASL_QUIET);

	/* reversibles */

	zero = PyInt_FromLong( 0 );
	PyDict_SetItem( reverse, zero, Py_None );
	Py_DECREF( zero );

	add_int(d,RES_BIND);
	add_int(d,RES_SEARCH_ENTRY);
	add_int(d,RES_SEARCH_RESULT);
	add_int(d,RES_MODIFY);
	add_int(d,RES_ADD);
	add_int(d,RES_DELETE);
	add_int(d,RES_MODRDN);
	add_int(d,RES_COMPARE);
	add_int(d,RES_ANY);

	add_int(d,RES_SEARCH_REFERENCE);
	add_int(d,RES_EXTENDED);
	add_int(d,RES_UNSOLICITED);

	/* non-reversibles */

	add_int(d,AUTH_NONE);
	add_int(d,AUTH_SIMPLE);
	add_int(d,SCOPE_BASE);
	add_int(d,SCOPE_ONELEVEL);
	add_int(d,SCOPE_SUBTREE);
	add_int(d,MOD_ADD);
	add_int(d,MOD_DELETE);
	add_int(d,MOD_REPLACE);
	add_int(d,MOD_INCREMENT);
	add_int(d,MOD_BVALUES);

	add_int(d,MSG_ONE);
	add_int(d,MSG_ALL);
	add_int(d,MSG_RECEIVED);

	/* (errors.c contains the error constants) */

	add_int(d,DEREF_NEVER);
	add_int(d,DEREF_SEARCHING);
	add_int(d,DEREF_FINDING);
	add_int(d,DEREF_ALWAYS);
	add_int(d,NO_LIMIT);

	add_int(d,OPT_API_INFO);
	add_int(d,OPT_DEREF);
	add_int(d,OPT_SIZELIMIT);
	add_int(d,OPT_TIMELIMIT);
#ifdef LDAP_OPT_REFERRALS
	add_int(d,OPT_REFERRALS);
#endif
	add_int(d,OPT_ERROR_NUMBER);
	add_int(d,OPT_RESTART);
	add_int(d,OPT_PROTOCOL_VERSION);
	add_int(d,OPT_SERVER_CONTROLS);
	add_int(d,OPT_CLIENT_CONTROLS);
	add_int(d,OPT_API_FEATURE_INFO);
	add_int(d,OPT_HOST_NAME);

	/* For backward-compability with OpenLDAP 2.3 libs this is defined in ldap/__init__.py */
	/* add_int(d,OPT_DIAGNOSTIC_MESSAGE); */

	add_int(d,OPT_ERROR_STRING);
	add_int(d,OPT_MATCHED_DN);
	add_int(d,OPT_DEBUG_LEVEL);
	add_int(d,OPT_TIMEOUT);
	add_int(d,OPT_REFHOPLIMIT);
	add_int(d,OPT_NETWORK_TIMEOUT);
	add_int(d,OPT_URI);
#ifdef LDAP_OPT_DEFBASE
	add_int(d,OPT_DEFBASE);
#endif
#ifdef HAVE_TLS
	add_int(d,OPT_X_TLS);
#ifdef LDAP_OPT_X_TLS_NEWCTX
	add_int(d,OPT_X_TLS_CTX);
#endif
	add_int(d,OPT_X_TLS_CACERTFILE);
	add_int(d,OPT_X_TLS_CACERTDIR);
	add_int(d,OPT_X_TLS_CERTFILE);
	add_int(d,OPT_X_TLS_KEYFILE);
	add_int(d,OPT_X_TLS_REQUIRE_CERT);
	add_int(d,OPT_X_TLS_CIPHER_SUITE);
	add_int(d,OPT_X_TLS_RANDOM_FILE);
	add_int(d,OPT_X_TLS_DHFILE);
	add_int(d,OPT_X_TLS_NEVER);
	add_int(d,OPT_X_TLS_HARD);
	add_int(d,OPT_X_TLS_DEMAND);
	add_int(d,OPT_X_TLS_ALLOW);
	add_int(d,OPT_X_TLS_TRY);
#ifdef LDAP_OPT_X_TLS_CRLCHECK
  /* only available if OpenSSL supports it => might cause backward compability problems */
	add_int(d,OPT_X_TLS_CRLCHECK);
#ifdef LDAP_OPT_X_TLS_CRLFILE
	add_int(d,OPT_X_TLS_CRLFILE);
#endif
	add_int(d,OPT_X_TLS_CRL_NONE);
	add_int(d,OPT_X_TLS_CRL_PEER);
	add_int(d,OPT_X_TLS_CRL_ALL);
#endif
#ifdef LDAP_OPT_X_TLS_NEWCTX
	add_int(d,OPT_X_TLS_NEWCTX);
#endif
#ifdef LDAP_OPT_X_TLS_PROTOCOL_MIN
	add_int(d,OPT_X_TLS_PROTOCOL_MIN);
#endif
#endif
	add_int(d,OPT_X_SASL_MECH);
	add_int(d,OPT_X_SASL_REALM);
	add_int(d,OPT_X_SASL_AUTHCID);
	add_int(d,OPT_X_SASL_AUTHZID);
	add_int(d,OPT_X_SASL_SSF);
	add_int(d,OPT_X_SASL_SSF_EXTERNAL);
	add_int(d,OPT_X_SASL_SECPROPS);
	add_int(d,OPT_X_SASL_SSF_MIN);
	add_int(d,OPT_X_SASL_SSF_MAX);
#ifdef LDAP_OPT_X_SASL_NOCANON
	add_int(d,OPT_X_SASL_NOCANON);
#endif
#ifdef LDAP_OPT_X_SASL_USERNAME
	add_int(d,OPT_X_SASL_USERNAME);
#endif
#ifdef LDAP_OPT_CONNECT_ASYNC
	add_int(d,OPT_CONNECT_ASYNC);
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_IDLE
	add_int(d,OPT_X_KEEPALIVE_IDLE);
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_PROBES
	add_int(d,OPT_X_KEEPALIVE_PROBES);
#endif
#ifdef LDAP_OPT_X_KEEPALIVE_INTERVAL
	add_int(d,OPT_X_KEEPALIVE_INTERVAL);
#endif

	add_int(d,DN_FORMAT_LDAP);
	add_int(d,DN_FORMAT_LDAPV3);
	add_int(d,DN_FORMAT_LDAPV2);
	add_int(d,DN_FORMAT_DCE);
	add_int(d,DN_FORMAT_UFN);
	add_int(d,DN_FORMAT_AD_CANONICAL);
	/* add_int(d,DN_FORMAT_LBER); */    /* "for testing only" */
	add_int(d,DN_FORMAT_MASK);
	add_int(d,DN_PRETTY);
	add_int(d,DN_SKIP);
	add_int(d,DN_P_NOLEADTRAILSPACES);
	add_int(d,DN_P_NOSPACEAFTERRDN);
	add_int(d,DN_PEDANTIC);

	add_int(d,AVA_NULL);
	add_int(d,AVA_STRING);
	add_int(d,AVA_BINARY);
	add_int(d,AVA_NONPRINTABLE);
	
	/*add_int(d,OPT_ON);*/
	obj = PyInt_FromLong(1);
	PyDict_SetItemString( d, "OPT_ON", obj );
	Py_DECREF(obj);
	/*add_int(d,OPT_OFF);*/
	obj = PyInt_FromLong(0);
	PyDict_SetItemString( d, "OPT_OFF", obj );			
	Py_DECREF(obj);
	
	add_int(d,OPT_SUCCESS);

	/* XXX - these belong in errors.c */

	add_int(d,URL_ERR_BADSCOPE);
	add_int(d,URL_ERR_MEM);

	/* author */

	author = PyString_FromString("python-ldap-dev@lists.sf.net");
	PyDict_SetItemString(d, "__author__", author);
	Py_DECREF(author);

	/* add_int(d,LIBLDAP_R); */
#ifdef HAVE_LIBLDAP_R
	obj = PyInt_FromLong(1);
#else
	obj = PyInt_FromLong(0);
#endif
	PyDict_SetItemString( d, "LIBLDAP_R", obj );
	Py_DECREF(obj);

	/* add_int(d,SASL); */
#ifdef HAVE_SASL
	obj = PyInt_FromLong(1);
#else
	obj = PyInt_FromLong(0);
#endif
	PyDict_SetItemString( d, "SASL_AVAIL", obj );
	Py_DECREF(obj);

	/* add_int(d,TLS); */
#ifdef HAVE_TLS
	obj = PyInt_FromLong(1);
#else
	obj = PyInt_FromLong(0);
#endif
	PyDict_SetItemString( d, "TLS_AVAIL", obj );
	Py_DECREF(obj);

	obj = PyString_FromString(LDAP_CONTROL_PAGE_OID);
	PyDict_SetItemString( d, "LDAP_CONTROL_PAGE_OID", obj );
	Py_DECREF(obj);

	obj = PyString_FromString(LDAP_CONTROL_VALUESRETURNFILTER);
	PyDict_SetItemString( d, "LDAP_CONTROL_VALUESRETURNFILTER", obj );
	Py_DECREF(obj);

}
