__author__ = 'rolandh'

ENTITYATTRIBUTES = "urn:oasis:names:tc:SAML:metadata:attribute&EntityAttributes"


def entity_categories(md):
    res = []
    if "extensions" in md:
        for elem in md["extensions"]["extension_elements"]:
            if elem["__class__"] == ENTITYATTRIBUTES:
                for attr in elem["attribute"]:
                    res.append(attr["text"])

    return res