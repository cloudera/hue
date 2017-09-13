# from dirg_util.dict import LDAPDict
# ldap_settings = {
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
# }
# Uncomment to use a LDAP directory instead.
# USERS = LDAPDict(**ldap_settings)

USERS = {
    "testuser": {
        "sn": "Testsson",
        "givenName": "Test",
        "eduPersonAffiliation": "student",
        "eduPersonScopedAffiliation": "student@example.com",
        "eduPersonPrincipalName": "test@example.com",
        "uid": "testuser",
        "eduPersonTargetedID": "one!for!all",
        "c": "SE",
        "o": "Example Co.",
        "ou": "IT",
        "initials": "P",
        "co": "co",
        "mail": "mail",
        "noreduorgacronym": "noreduorgacronym",
        "schacHomeOrganization": "example.com",
        "email": "test@example.com",
        "displayName": "Test Testsson",
        "labeledURL": "http://www.example.com/test My homepage",
        "norEduPersonNIN": "SE199012315555",
        "postaladdress": "postaladdress",
        "cn": "cn"
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
        # "schacHomeOrganization": "example.com",
        "mail": "roland@example.com",
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
