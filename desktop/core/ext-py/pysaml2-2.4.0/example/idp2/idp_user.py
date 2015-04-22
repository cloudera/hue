#from dirg_util.dict import LDAPDict
#ldap_settings = {
#    "ldapuri": "ldaps://ldap.test.umu.se",
#    "base": "dc=umu, dc=se",
#    "filter_pattern": "(uid=%s)",
#    "user": "",
#    "passwd": "",
#    "attr": [
#        "eduPersonScopedAffiliation",
#        "eduPersonAffiliation",
#        "eduPersonPrincipalName",
#        "givenName",
#        "sn",
#        "mail",
#        "uid",
#        "o",
#        "c",
#        "labeledURI",
#        "ou",
#        "displayName",
#        "norEduPersonLIN"
#    ],
#    "keymap": {
#        "mail": "email",
#        "labeledURI": "labeledURL",
#    },
#    "static_values": {
#        "eduPersonTargetedID": "one!for!all",
#    },
#    "exact_match": True,
#    "firstonly_len1": True,
#    "timeout": 15,
#}
#Uncomment to use a LDAP directory instead.
#USERS = LDAPDict(**ldap_settings)

USERS = {
    "haho0032": {
        "sn": "Hoerberg",
        "givenName": "Hasse",
        "eduPersonAffiliation": "student",
        "eduPersonScopedAffiliation": "student@example.com",
        "eduPersonPrincipalName": "haho@example.com",
        "uid": "haho0032",
        "eduPersonTargetedID": "one!for!all",
        "c": "SE",
        "o": "Example Co.",
        "ou": "IT",
        "initials": "P",
        "schacHomeOrganization": "example.com",
        "email": "hans@example.com",
        "displayName": "Hans Hoerberg",
        "labeledURL": "http://www.example.com/haho My homepage",
        "norEduPersonNIN": "SE199012315555"
    },
    "roland": {
        "sn": "Hedberg",
        "givenName": "Roland",
        "eduPersonScopedAffiliation": "staff@example.com",
        "eduPersonPrincipalName": "rohe@example.com",
        "uid": "rohe",
        "eduPersonTargetedID": "one!for!all",
        "c": "SE",
        "o": "Example Co.",
        "ou": "IT",
        "initials": "P",
        #"schacHomeOrganization": "example.com",
        "email": "roland@example.com",
        "displayName": "P. Roland Hedberg",
        "labeledURL": "http://www.example.com/rohe My homepage",
        "norEduPersonNIN": "SE197001012222"
    },
    "babs": {
        "surname": "Babs",
        "givenName": "Ozzie",
        "eduPersonAffiliation": "affiliate"
    },
    "upper": {
        "surname": "Jeter",
        "givenName": "Derek",
        "eduPersonAffiliation": "affiliate"
    },
}

EXTRA = {
    "roland": {
        "eduPersonEntitlement": "urn:mace:swamid.se:foo:bar",
        "schacGender": "male",
        "schacUserPresenceID": "skype:pepe.perez"
    }
}