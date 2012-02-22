/* See http://www.python-ldap.org/ for details.
 * $Id: ldapcontrol.h,v 1.6 2009/08/04 05:39:10 leonard Exp $ */

#ifndef __h_ldapcontrol
#define __h_ldapcontrol

#include "common.h"
#include "ldap.h"

void LDAPinit_control(PyObject *d);
void LDAPControl_List_DEL( LDAPControl** );
int  LDAPControls_from_object(PyObject *, LDAPControl ***);
PyObject* LDAPControls_to_List(LDAPControl **ldcs);

#endif /* __h_ldapcontrol */
