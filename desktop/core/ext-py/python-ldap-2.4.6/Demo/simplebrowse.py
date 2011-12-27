#! python

#
# simple LDAP server browsing example
#

import ldap
import string
from traceback import print_exc

url = "ldap://ldap.openldap.org/"
dn = "dc=openldap,dc=org"

print "Connecting to", url

l = ldap.initialize(url)
l.bind_s("", "", ldap.AUTH_SIMPLE);

lastdn = dn
dnlist = None

while 1:

    #-- read a command
    try:
        cmd = raw_input(dn + "> ")
    except EOFError:
	print
	break

    try:

	if cmd == "?":
		print  "cd <dn>	- change DN to <dn>"
		print  "cd <n>	- change DN to number <n> of last 'ls'"
		print  "cd -	- change to previous DN"
		print  "cd ..	- change to one-level higher DN"
		print  "cd 	- change to root DN"
		print  "ls	- list children of crrent DN"
		print  ".	- show attributes of current DN"
		print  "/<expr>	- list descendents matching filter <expr>"
		print  "?	- show this help"

	elif cmd == "ls":
		print "Children of", `dn`, ":"
		dnlist = []
		#
		# List the children at one level down from the current dn
		# We use the filter 'objectclass=*' to match everything.
		# We're not interested in attributes at this stage, so
		# we specify [] as the list of attribute names to retreive.
		#
		for name,attrs in l.search_s(dn, ldap.SCOPE_ONELEVEL, 
		    "objectclass=*", []):
			#-- shorten resulting dns for output brevity
			if name.startswith(dn+", "):
				shortname = "+ "+name[len(dn)+2:]
			elif name.endswith(", "+dn):
				shortname = name[:-len(dn)-2]+" +"
			else:
				shortname = name
			print " %3d. %s" % (len(dnlist), shortname)
			dnlist.append(name)

	elif cmd == "cd":
		dn = ""
		dnlist = None

	elif cmd.startswith("cd "):
		arg = cmd[3:]
		if arg == '-':
			lastdn,dn = dn,lastdn
		elif arg == '..':
			dn = string.join(ldap.explode_dn(dn)[1:], ",")
			dn = string.strip(dn)
                else:
		        try:
			        i = int(arg)
		        except:
			        godn = arg
                        else:
			        if dnlist is None:
				        print "do an ls first"
                                else:
			                godn = dnlist[i]
		                lastdn = dn
		                dn = godn

	elif cmd == ".":
		#
		# Retrieve all the attributes for the current dn.
		# We construct a search using SCOPE_BASE (ie just the
		# given DN) and again filter with "objectclass=*".
		# No attributes are listed, so the default is for
		# the client to receive all attributes on the DN.
		#
		print "Attributes of", `dn`, ":"
		for name,attrs in l.search_s(dn, ldap.SCOPE_BASE,
		    "objectclass=*"):
			print "  %-24s" % name
			for k,vals in attrs.items():
			    for v in vals:
				if len(v) > 200: 
					v = `v[:200]` + \
						("... (%d bytes)" % len(v))
				else:
					v = `v`
				print "      %-12s: %s" % (k, v)

	elif cmd.startswith("/"):
		#
		# Search descendent objects to match a given filter.
		# We use SCOPE_SUBTREE to indicate descendents, and
		# again specify an empty attribute list to indicate
		# that we're not interested in them.
		#
		expr = cmd[1:]
		print "Descendents matching filter", `expr`, ":"
		for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,
		    expr, []):
			print "  %24s", name

	else:
		print "unknown command - try '?' for help"

    except:
	print_exc()

