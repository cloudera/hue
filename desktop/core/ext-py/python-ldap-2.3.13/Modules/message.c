/* See http://www.python-ldap.org/ for details.
 * $Id: message.c,v 1.16 2009/08/17 01:49:47 leonard Exp $ */

#include "common.h"
#include "message.h"
#include "berval.h"
#include "errors.h"

/*
 * Converts an LDAP message into a Python structure.
 *
 * On success, returns a list of dictionaries.
 * On failure, returns NULL, and sets an error.
 *
 * The message m is always freed, regardless of return value.
 */
PyObject *
LDAPmessage_to_python(LDAP *ld, LDAPMessage *m)
{
    /* we convert an LDAP message into a python structure.
     * It is always a list of dictionaries.
     * We always free m.
     */

     PyObject* result;
     LDAPMessage* entry;

     result = PyList_New(0);
     if (result == NULL) {
        ldap_msgfree( m );
	return NULL;
     }

     for(entry = ldap_first_entry(ld,m);
         entry != NULL;
	 entry = ldap_next_entry(ld,entry))
     {
	 char *dn;
	 char *attr;
	 BerElement *ber = NULL;
	 PyObject* entrytuple; 
	 PyObject* attrdict; 

	 dn = ldap_get_dn( ld, entry );
	 if (dn == NULL)  {
	     Py_DECREF(result);
             ldap_msgfree( m );
	     return LDAPerror( ld, "ldap_get_dn" );
	 }

	 attrdict = PyDict_New();
	 if (attrdict == NULL) {
		Py_DECREF(result);
		ldap_msgfree( m );
		ldap_memfree(dn);
		return NULL;
	 }

	 /* Fill attrdict with lists */
	 for( attr = ldap_first_attribute( ld, entry, &ber );
	      attr != NULL;
	      attr = ldap_next_attribute( ld, entry, ber )
	 ) {
	     PyObject* valuelist;
	     struct berval ** bvals =
	     	ldap_get_values_len( ld, entry, attr );

	     /* Find which list to append to */
	     if ( PyMapping_HasKeyString( attrdict, attr ) ) {
		 valuelist = PyMapping_GetItemString( attrdict, attr );
	     } else {
		 valuelist = PyList_New(0);
		 if (valuelist != NULL && PyMapping_SetItemString(attrdict, 
		     attr, valuelist) == -1) {
			Py_DECREF(valuelist);
			valuelist = NULL;	/* catch error later */
		 }
	     }

	     if (valuelist == NULL) {
		Py_DECREF(attrdict);
		Py_DECREF(result);
		if (ber != NULL)
		    ber_free(ber, 0);
		ldap_msgfree( m );
		ldap_memfree(attr);
		ldap_memfree(dn);
		return NULL;
	     }

	     if (bvals != NULL) {
	        Py_ssize_t i;
		for (i=0; bvals[i]; i++) {
		    PyObject *valuestr;

		    valuestr = LDAPberval_to_object(bvals[i]);
		    if (PyList_Append( valuelist, valuestr ) == -1) {
			Py_DECREF(attrdict);
			Py_DECREF(result);
			Py_DECREF(valuestr);
			Py_DECREF(valuelist);
			if (ber != NULL)
			    ber_free(ber, 0);
			ldap_msgfree( m );
			ldap_memfree(attr);
			ldap_memfree(dn);
			return NULL;
		    }
		    Py_DECREF(valuestr);
	    	}
		ldap_value_free_len(bvals);
	     }
	     Py_DECREF( valuelist );
	     ldap_memfree(attr);
	 }

	 entrytuple = Py_BuildValue("(sO)", dn, attrdict);
	 ldap_memfree(dn);
	 Py_DECREF(attrdict);
	 PyList_Append(result, entrytuple);
	 Py_DECREF(entrytuple);
	 if (ber != NULL)
		 ber_free(ber, 0);
     }
     for(entry = ldap_first_reference(ld,m);
	 entry != NULL;
	 entry = ldap_next_reference(ld,entry))
     {
	 char **refs = NULL;
	 PyObject* entrytuple;
	 PyObject* reflist = PyList_New(0);

	 if (reflist == NULL)  {
	     Py_DECREF(result);
	     ldap_msgfree( m );
	     return NULL;
	 }
	 if (ldap_parse_reference(ld, entry, &refs, NULL, 0) != LDAP_SUCCESS) {
	     Py_DECREF(result);
	     ldap_msgfree( m );
	     return LDAPerror( ld, "ldap_parse_reference" );
	 }
	 if (refs) {
	     Py_ssize_t i;
	     for (i=0; refs[i] != NULL; i++) {
		 PyObject *refstr = PyString_FromString(refs[i]);
		 PyList_Append(reflist, refstr);
		 Py_DECREF(refstr);
	     }
	     ber_memvfree( (void **) refs );
	 }
	 entrytuple = Py_BuildValue("(sO)", NULL, reflist);
	 Py_DECREF(reflist);
	 PyList_Append(result, entrytuple);
	 Py_DECREF(entrytuple);
     }
     ldap_msgfree( m );
     return result;
}
