__author__ = "rolandh"

RESEARCH_AND_SCHOLARSHIP = "http://id.incommon.org/category/research-and-scholarship"

RELEASE = {
    "": ["eduPersonTargetedID"],
    RESEARCH_AND_SCHOLARSHIP: [
        "eduPersonPrincipalName",
        "eduPersonScopedAffiliation",
        "mail",
        "givenName",
        "sn",
        "displayName",
    ],
}
