CLAIMS = "http://schemas.xmlsoap.org/claims/"


MAP = {
    "identifier": "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified",
    "fro": {
        f"{CLAIMS}commonname": "commonName",
        f"{CLAIMS}emailaddress": "emailAddress",
        f"{CLAIMS}group": "group",
        f"{CLAIMS}upn": "upn",
    },
    "to": {
        "commonName": f"{CLAIMS}commonname",
        "emailAddress": f"{CLAIMS}emailaddress",
        "group": f"{CLAIMS}group",
        "upn": f"{CLAIMS}upn",
    },
}
