import sys,getpass
import ldap

#l = ldap.open("localhost", 31001)
l = ldap.open("marta.it.uq.edu.au")

login_dn = "cn=root,ou=CSEE,o=UQ,c=AU"
login_pw = getpass.getpass("Password for %s: " % login_dn)
l.simple_bind_s(login_dn, login_pw)

#
# create a new sub organisation
#

try:
    dn = "ou=CSEE,o=UQ,c=AU"
    print "Adding", repr(dn)
    l.add_s(dn,
	 [
	    ("objectclass",["organizationalUnit"]),
	    ("ou", ["CSEE"]),
	    ("description", [
		    "Department of Computer Science and Electrical Engineering"]),
	 ]
       )

except _ldap.LDAPError:
    pass

#
# create an entry for me
#

dn = "cn=David Leonard,ou=CSEE,o=UQ,c=AU"
print "Updating", repr(dn)

try:
	l.delete_s(dn)
except:
	pass

l.add_s(dn,
     [
	("objectclass",			["organizationalPerson"]),
	("sn",				["Leonard"]),
	("cn",				["David Leonard"]),
	("description",			["Ph.D. student"]),
	("display-name",		["David Leonard"]),
	#("commonname",			["David Leonard"]),
	("mail",			["david.leonard@csee.uq.edu.au"]),
	("othermailbox",		["d@openbsd.org"]),
	("givenname",			["David"]),
	("surname",			["Leonard"]),
	("seeAlso",			["http://www.csee.uq.edu.au/~leonard/"]),
	("url",				["http://www.csee.uq.edu.au/~leonard/"]),
	#("homephone",			[]),
	#("fax",			[]),
	#("otherfacsimiletelephonenumber",[]),
	#("officefax",			[]),
	#("mobile",			[]),
	#("otherpager",			[]),
	#("officepager",		[]),
	#("pager",			[]),
	("info",			["info"]),
	("title",			["Mr"]),
	#("telephonenumber",		[]),
	("l",				["Brisbane"]),
	("st",				["Queensland"]),
	("c",				["AU"]),
	("co",				["co"]),
	("o",				["UQ"]),
	("ou",				["CSEE"]),
	#("homepostaladdress",		[]),
	#("postaladdress",		[]),
	#("streetaddress",		[]),
	#("street",			[]),
	("department",			["CSEE"]),
	("comment",			["comment"]),
	#("postalcode",			[]),
	("physicaldeliveryofficename",  ["Bldg 78, UQ, St Lucia"]),
	("preferredDeliveryMethod",	["email"]),
	("initials",			["DRL"]),
	("conferenceinformation",	["MS-conferenceinformation"]),
	#("usercertificate",		[]),
	("labeleduri",			["labeleduri"]),
	("manager",			["cn=Jaga Indulska"]),
	("reports",			["reports"]),
	("jpegPhoto",			[open("/www/leonard/leonard.jpg","r").read()]),
	("uid",				["leonard"]),
	("userPassword",		[""])

    ])

#
# search beneath the CSEE/UQ/AU tree
#

res = l.search_s(
	"ou=CSEE, o=UQ, c=AU", 
	_ldap.SCOPE_SUBTREE, 
	"objectclass=*",
      )
print res

l.unbind()

