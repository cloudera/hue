# See http://technet.microsoft.com/en-us/library/ee913589(v=ws.10).aspx
# for information regarding the default claim types supported by
# Microsoft ADFS v2.0.

MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    "fro": {
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'emailAddress',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'givenName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'name',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn': 'upn',
        'http://schemas.xmlsoap.org/claims/commonname': 'commonName',
        'http://schemas.xmlsoap.org/claims/group': 'group',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/role': 'role',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'surname',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/privatepersonalidentifier': 'privatePersonalId',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier': 'nameId',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationmethod': 'authenticationMethod',
        'http://schemas.xmlsoap.com/ws/2005/05/identity/claims/denyonlysid': 'denyOnlySid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarysid': 'denyOnlyPrimarySid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarygroupsid': 'denyOnlyPrimaryGroupSid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid': 'groupSid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/primarygroupsid': 'primaryGroupSid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/primarysid': 'primarySid',
        'http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname': 'windowsAccountName',
        },
    "to": {
        'emailAddress': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
        'givenName': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
        'name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
        'upn': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn',
        'commonName': 'http://schemas.xmlsoap.org/claims/commonname',
        'group': 'http://schemas.xmlsoap.org/claims/group',
        'role': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/role',
        'surname': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
        'privatePersonalId': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/privatepersonalidentifier',
        'nameId': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier',
        'authenticationMethod': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/authenticationmethod',
        'denyOnlySid': 'http://schemas.xmlsoap.com/ws/2005/05/identity/claims/denyonlysid',
        'denyOnlyPrimarySid': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarysid',
        'denyOnlyPrimaryGroupSid': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/denyonlyprimarygroupsid',
        'groupSid': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/groupsid',
        'primaryGroupSid': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/primarygroupsid',
        'primarySid':  'http://schemas.microsoft.com/ws/2008/06/identity/claims/primarysid',
        'windowsAccountName': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname',
    }
}
