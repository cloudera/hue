__author__ = "rhoerbe"  # 2013-09-05
# Entity Categories specifying the PVP eGov Token as of "PVP2-Allgemein V2.1.0", http://www.ref.gv.at/


EGOVTOKEN = [
    "PVP-VERSION",
    "PVP-PRINCIPAL-NAME",
    "PVP-GIVENNAME",
    "PVP-BIRTHDATE",
    "PVP-USERID",
    "PVP-GID",
    "PVP-BPK",
    "PVP-MAIL",
    "PVP-TEL",
    "PVP-PARTICIPANT-ID",
    "PVP-PARTICIPANT-OKZ",
    "PVP-OU-OKZ",
    "PVP-OU",
    "PVP-OU-GV-OU-ID",
    "PVP-FUNCTION",
    "PVP-ROLES",
]


CHARGEATTR = [
    "PVP-INVOICE-RECPT-ID",
    "PVP-COST-CENTER-ID",
    "PVP-CHARGE-CODE",
]

# all eGov Token attributes except (1) transaction charging and (2) chaining
PVP2 = "http://www.ref.gv.at/ns/names/agiz/pvp/egovtoken"
# transaction charging extension
PVP2CHARGE = "http://www.ref.gv.at/ns/names/agiz/pvp/egovtoken-charge"

RELEASE = {
    PVP2: EGOVTOKEN,
    PVP2CHARGE: CHARGEATTR,
}
