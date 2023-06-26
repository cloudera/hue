__author__ = 'rolandh'

NAME = ["givenName", "displayName", "sn", "cn"]
STATIC_ORG_INFO = ["c", "o", "co", "norEduOrgAcronym", "schacHomeOrganization",
                   'schacHomeOrganizationType']
OTHER = ["eduPersonPrincipalName", "eduPersonScopedAffiliation", "mail",
         "eduPersonAssurance"]

R_AND_S = ['eduPersonTargetedID',
           'eduPersonPrincipalName',
           'mail',
           'displayName',
           'givenName',
           'sn',
           'eduPersonScopedAffiliation'
           ]

# These give you access to information
RESEARCH_AND_EDUCATION = "http://www.swamid.se/category/research-and-education"
SFS_1993_1153 = "http://www.swamid.se/category/sfs-1993-1153"
RESEARCH_AND_SCHOLARSHIP = "http://refeds.org/category/research-and-scholarship"

# presently these don't by themself
EU = "http://www.swamid.se/category/eu-adequate-protection"
NREN = "http://www.swamid.se/category/nren-service"
HEI = "http://www.swamid.se/category/hei-service"

RELEASE = {
    "": ["eduPersonTargetedID"],
    SFS_1993_1153: ["norEduPersonNIN", "eduPersonAssurance"],
    (RESEARCH_AND_EDUCATION, EU): NAME + STATIC_ORG_INFO + OTHER,
    (RESEARCH_AND_EDUCATION, NREN): NAME + STATIC_ORG_INFO + OTHER,
    (RESEARCH_AND_EDUCATION, HEI): NAME + STATIC_ORG_INFO + OTHER,
    RESEARCH_AND_SCHOLARSHIP: R_AND_S,
}