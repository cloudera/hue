CLAIMS = 'http://schemas.xmlsoap.org/claims/'


MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    'fro': {
        CLAIMS+'commonname': 'commonName',
        CLAIMS+'emailaddress': 'emailAddress',
        CLAIMS+'group': 'group',
        CLAIMS+'upn': 'upn',
    },
    'to': {
        'commonName': CLAIMS+'commonname',
        'emailAddress': CLAIMS+'emailaddress',
        'group': CLAIMS+'group',
        'upn': CLAIMS+'upn',
    }
}
