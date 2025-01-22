__author__ = "rolandh"

COC = "http://www.geant.net/uri/dataprotection-code-of-conduct/v1"
COCO = COC

RELEASE = {
    "": ["eduPersonTargetedID"],
    # COC: ["eduPersonPrincipalName", "eduPersonScopedAffiliation", "mail",
    #       "displayName", "schacHomeOrganization"],
    COCO: [
        "eduPersonPrincipalName",
        "eduPersonScopedAffiliation",
        "eduPersonAffiliation",
        "mail",
        "displayName",
        "cn",
        "schacHomeOrganization",
    ],
}

ONLY_REQUIRED = {COCO: True}
