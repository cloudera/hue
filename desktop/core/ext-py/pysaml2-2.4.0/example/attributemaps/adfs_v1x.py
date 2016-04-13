# See http://technet.microsoft.com/en-us/library/cc733065(v=ws.10).aspx
# and http://technet.microsoft.com/en-us/library/ee913589(v=ws.10).aspx
# for information regarding the default claim types supported by
# Microsoft ADFS v1.x.

MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    "fro": {
        'http://schemas.xmlsoap.org/claims/commonname': 'commonName',
        'http://schemas.xmlsoap.org/claims/emailaddress': 'emailAddress',
        'http://schemas.xmlsoap.org/claims/group': 'group',
        'http://schemas.xmlsoap.org/claims/upn': 'upn',
        },
    "to": {
        'commonName': 'http://schemas.xmlsoap.org/claims/commonname',
        'emailAddress': 'http://schemas.xmlsoap.org/claims/emailaddress',
        'group': 'http://schemas.xmlsoap.org/claims/group',
        'upn': 'http://schemas.xmlsoap.org/claims/upn',
    }
}
