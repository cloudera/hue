CLAIMS = 'http://schemas.xmlsoap.org/claims/'
COM_WS_CLAIMS = 'http://schemas.xmlsoap.com/ws/2005/05/identity/claims/'
MS_CLAIMS = 'http://schemas.microsoft.com/ws/2008/06/identity/claims/'
ORG_WS_CLAIMS = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/'


MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    'fro': {
        CLAIMS+'commonname': 'commonName',
        CLAIMS+'group': 'group',
        COM_WS_CLAIMS+'denyonlysid': 'denyOnlySid',
        MS_CLAIMS+'authenticationmethod': 'authenticationMethod',
        MS_CLAIMS+'denyonlyprimarygroupsid': 'denyOnlyPrimaryGroupSid',
        MS_CLAIMS+'denyonlyprimarysid': 'denyOnlyPrimarySid',
        MS_CLAIMS+'groupsid': 'groupSid',
        MS_CLAIMS+'primarygroupsid': 'primaryGroupSid',
        MS_CLAIMS+'primarysid': 'primarySid',
        MS_CLAIMS+'role': 'role',
        MS_CLAIMS+'windowsaccountname': 'windowsAccountName',
        ORG_WS_CLAIMS+'emailaddress': 'emailAddress',
        ORG_WS_CLAIMS+'givenname': 'givenName',
        ORG_WS_CLAIMS+'name': 'name',
        ORG_WS_CLAIMS+'nameidentifier': 'nameId',
        ORG_WS_CLAIMS+'privatepersonalidentifier': 'privatePersonalId',
        ORG_WS_CLAIMS+'surname': 'surname',
        ORG_WS_CLAIMS+'upn': 'upn',
    },
    'to': {
        'authenticationMethod': MS_CLAIMS+'authenticationmethod',
        'commonName': CLAIMS+'commonname',
        'denyOnlyPrimaryGroupSid': MS_CLAIMS+'denyonlyprimarygroupsid',
        'denyOnlyPrimarySid': MS_CLAIMS+'denyonlyprimarysid',
        'denyOnlySid': COM_WS_CLAIMS+'denyonlysid',
        'emailAddress': ORG_WS_CLAIMS+'emailaddress',
        'givenName': ORG_WS_CLAIMS+'givenname',
        'group': CLAIMS+'group',
        'groupSid': MS_CLAIMS+'groupsid',
        'name': ORG_WS_CLAIMS+'name',
        'nameId': ORG_WS_CLAIMS+'nameidentifier',
        'primaryGroupSid': MS_CLAIMS+'primarygroupsid',
        'primarySid': MS_CLAIMS+'primarysid',
        'privatePersonalId': ORG_WS_CLAIMS+'privatepersonalidentifier',
        'role': MS_CLAIMS+'role',
        'surname': ORG_WS_CLAIMS+'surname',
        'upn': ORG_WS_CLAIMS+'upn',
        'windowsAccountName': MS_CLAIMS+'windowsaccountname',
    }
}
