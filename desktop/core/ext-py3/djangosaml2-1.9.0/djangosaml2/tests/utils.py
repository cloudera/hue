from html.parser import HTMLParser


class SAMLPostFormParser(HTMLParser):
    """
    Parses the SAML Post binding form page for the SAMLRequest value.
    """

    saml_request_value = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag != "input" or attrs_dict.get("name") != "SAMLRequest":
            return
        self.saml_request_value = attrs_dict.get("value")
