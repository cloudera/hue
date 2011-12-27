/* See http://www.python-ldap.org/ for details.
 * $Id: message.h,v 1.6 2011/02/21 21:04:00 stroeder Exp $ */

#ifndef __h_message 
#define __h_message 

#include "common.h"
#include "lber.h"
#include "ldap.h"

extern PyObject* LDAPmessage_to_python( LDAP*ld, LDAPMessage*m, int add_ctrls, int add_intermediates );

#endif /* __h_message_ */

