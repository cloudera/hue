/* See http://www.python-ldap.org/ for details.
 * $Id: message.h,v 1.5 2009/04/17 12:19:09 stroeder Exp $ */

#ifndef __h_message 
#define __h_message 

#include "common.h"
#include "lber.h"
#include "ldap.h"

extern PyObject* LDAPmessage_to_python( LDAP*ld, LDAPMessage*m );

#endif /* __h_message_ */

