CLAIMS = "http://schemas.xmlsoap.org/claims/"
COM_WS_CLAIMS = "http://schemas.xmlsoap.com/ws/2005/05/identity/claims/"
MS_CLAIMS = "http://schemas.microsoft.com/ws/2008/06/identity/claims/"
ORG_WS_CLAIMS = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/"


MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    "fro": {
        f"{CLAIMS}commonname": "commonName",
        f"{CLAIMS}group": "group",
        f"{COM_WS_CLAIMS}denyonlysid": "denyOnlySid",
        f"{MS_CLAIMS}authenticationmethod": "authenticationMethod",
        f"{MS_CLAIMS}denyonlyprimarygroupsid": "denyOnlyPrimaryGroupSid",
        f"{MS_CLAIMS}denyonlyprimarysid": "denyOnlyPrimarySid",
        f"{MS_CLAIMS}groupsid": "groupSid",
        f"{MS_CLAIMS}primarygroupsid": "primaryGroupSid",
        f"{MS_CLAIMS}primarysid": "primarySid",
        f"{MS_CLAIMS}role": "role",
        f"{MS_CLAIMS}windowsaccountname": "windowsAccountName",
        f"{ORG_WS_CLAIMS}emailaddress": "emailAddress",
        f"{ORG_WS_CLAIMS}givenname": "givenName",
        f"{ORG_WS_CLAIMS}name": "name",
        f"{ORG_WS_CLAIMS}nameidentifier": "nameId",
        f"{ORG_WS_CLAIMS}privatepersonalidentifier": "privatePersonalId",
        f"{ORG_WS_CLAIMS}surname": "surname",
        f"{ORG_WS_CLAIMS}upn": "upn",
    },
    "to": {
        "authenticationMethod": f"{MS_CLAIMS}authenticationmethod",
        "commonName": f"{CLAIMS}commonname",
        "denyOnlyPrimaryGroupSid": f"{MS_CLAIMS}denyonlyprimarygroupsid",
        "denyOnlyPrimarySid": f"{MS_CLAIMS}denyonlyprimarysid",
        "denyOnlySid": f"{COM_WS_CLAIMS}denyonlysid",
        "emailAddress": f"{ORG_WS_CLAIMS}emailaddress",
        "givenName": f"{ORG_WS_CLAIMS}givenname",
        "group": f"{CLAIMS}group",
        "groupSid": f"{MS_CLAIMS}groupsid",
        "name": f"{ORG_WS_CLAIMS}name",
        "nameId": f"{ORG_WS_CLAIMS}nameidentifier",
        "primaryGroupSid": f"{MS_CLAIMS}primarygroupsid",
        "primarySid": f"{MS_CLAIMS}primarysid",
        "privatePersonalId": f"{ORG_WS_CLAIMS}privatepersonalidentifier",
        "role": f"{MS_CLAIMS}role",
        "surname": f"{ORG_WS_CLAIMS}surname",
        "upn": f"{ORG_WS_CLAIMS}upn",
        "windowsAccountName": f"{MS_CLAIMS}windowsaccountname",
    },
}
