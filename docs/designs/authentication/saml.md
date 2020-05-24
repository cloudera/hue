
# SAML Authentication with additional group checks

SAML is one of the main solution for offering SSO with LDAP and OpenId Connect. In Hue, this happens with the [SAML2Backend](https://docs.gethue.com/administrator/configuration/server/#saml) [Django Backend](https://docs.djangoproject.com/en/3.0/ref/contrib/auth/).

## Restricting user authentication via a dedicated 'groups' attribute

e.g. In addition to SSO, only allow to authenticate a user if he belongs to a set of SAML groups. (note: if we want to allow the authentication if ANY group is matching instead of ALL the groups we would need an extra parameter).

We could add the list of requires groups in libsaml:

    [libsaml]
    # Comma separated list of group names which are all required to authenticate successfully.
    ## required_groups=['admin', 'sales']
    ## required_groups_attribute='groups'


And in the SAML2Backend class, we could override `is_authorized` to take care of the logic:

    def is_authorized(self, attributes, attribute_mapping):
        """Hook to allow custom authorization policies based on
        SAML attributes.
        """
        return set(required_groups) & set(attributes[REQUIRED_GROUPS_ATTRIBUTES.get()])

Note: this solution is hardcoded with the concept of groups. We might want or not generifying to any other attribute. But if not a concern, it should be good enough for a v1.

Note: we should contribute back some short `def is_authorized` documentation to https://github.com/knaperek/djangosaml2/ as this would be a neat feature to promote.

## Tests

Add tests (with the help of the Mock module) to check if:

* Authentication with group list [] --> rejects
* Authentication with group list missing one group --> rejetcs
* Authentication with group list intersecting all the required groups --> succeeds
