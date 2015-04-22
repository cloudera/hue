from saml2.assertion import Policy

HOST = '127.0.0.1'
PORT = 8087
HTTPS = False

# Which groups of entity categories to use
POLICY = Policy(
    {
        "default": {"entity_categories": ["swamid", "edugain"]}
    }
)

# HTTPS cert information
SERVER_CERT = "pki/mycert.pem"
SERVER_KEY = "pki/mykey.pem"
CERT_CHAIN = ""
