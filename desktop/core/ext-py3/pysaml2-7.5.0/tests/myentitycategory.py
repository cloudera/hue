CUSTOM_R_AND_S = [
    "eduPersonTargetedID",
    "eduPersonPrincipalName",
    "mail",
    "displayName",
    "givenName",
    "sn",
    "eduPersonScopedAffiliation",
    "eduPersonUniqueId",
]

RESEARCH_AND_SCHOLARSHIP = "http://refeds.org/category/research-and-scholarship"

RELEASE = {
    "": ["eduPersonTargetedID"],
    RESEARCH_AND_SCHOLARSHIP: CUSTOM_R_AND_S,
}
