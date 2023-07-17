from saml2 import extension_elements_to_elements
from saml2.authn_context import ippword
from saml2.authn_context import mobiletwofactor
from saml2.authn_context import ppt
from saml2.authn_context import pword
from saml2.authn_context import sslcert
from saml2.saml import AuthnContext
from saml2.saml import AuthnContextClassRef
from saml2.samlp import RequestedAuthnContext


UNSPECIFIED = "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified"

INTERNETPROTOCOLPASSWORD = "urn:oasis:names:tc:SAML:2.0:ac:classes:InternetProtocolPassword"
MOBILETWOFACTORCONTRACT = "urn:oasis:names:tc:SAML:2.0:ac:classes:MobileTwoFactorContract"
PASSWORDPROTECTEDTRANSPORT = "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
PASSWORD = "urn:oasis:names:tc:SAML:2.0:ac:classes:Password"
TLSCLIENT = "urn:oasis:names:tc:SAML:2.0:ac:classes:TLSClient"
TIMESYNCTOKEN = "urn:oasis:names:tc:SAML:2.0:ac:classes:TimeSyncToken"

AL1 = "http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel1"
AL2 = "http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel2"
AL3 = "http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel3"
AL4 = "http://idmanagement.gov/icam/2009/12/saml_2.0_profile/assurancelevel4"

CMP_TYPE = ["exact", "minimum", "maximum", "better"]


class AuthnBroker:
    def __init__(self):
        self.db = {"info": {}, "key": {}}
        self.next = 0

    @staticmethod
    def exact(a, b):
        return a == b

    @staticmethod
    def minimum(a, b):
        return b >= a

    @staticmethod
    def maximum(a, b):
        return b <= a

    @staticmethod
    def better(a, b):
        return b > a

    def add(self, spec, method, level=0, authn_authority="", reference=None):
        """
        Adds a new authentication method.
        Assumes not more than one authentication method per AuthnContext
        specification.

        :param spec: What the authentication endpoint offers in the form
            of an AuthnContext
        :param method: A identifier of the authentication method.
        :param level: security level, positive integers, 0 is lowest
        :param reference: Desired unique reference to this `spec'
        :return:
        """

        if spec.authn_context_class_ref:
            key = spec.authn_context_class_ref.text
            _info = {"class_ref": key, "method": method, "level": level, "authn_auth": authn_authority}
        elif spec.authn_context_decl:
            key = spec.authn_context_decl.c_namespace
            _info = {"method": method, "decl": spec.authn_context_decl, "level": level, "authn_auth": authn_authority}
        else:
            raise NotImplementedError()

        self.next += 1
        _ref = reference
        if _ref is None:
            _ref = str(self.next)

        if _ref in self.db["info"]:
            raise Exception("Internal error: reference is not unique")

        self.db["info"][_ref] = _info
        try:
            self.db["key"][key].append(_ref)
        except KeyError:
            self.db["key"][key] = [_ref]

    def remove(self, spec, method=None, level=0, authn_authority=""):
        if spec.authn_context_class_ref:
            _cls_ref = spec.authn_context_class_ref.text
            try:
                _refs = self.db["key"][_cls_ref]
            except KeyError:
                return
            else:
                _remain = []
                for _ref in _refs:
                    item = self.db["info"][_ref]
                    if method and method != item["method"]:
                        _remain.append(_ref)
                    if level and level != item["level"]:
                        _remain.append(_ref)
                    if authn_authority and authn_authority != item["authn_authority"]:
                        _remain.append(_ref)
                if _remain:
                    self.db[_cls_ref] = _remain

    def _pick_by_class_ref(self, cls_ref, comparision_type="exact"):
        func = getattr(self, comparision_type)
        try:
            _refs = self.db["key"][cls_ref]
        except KeyError:
            return []
        else:
            _item = self.db["info"][_refs[0]]
            _level = _item["level"]
            if comparision_type != "better":
                if _item["method"]:
                    res = [(_item["method"], _refs[0])]
                else:
                    res = []
            else:
                res = []

            for ref in _refs[1:]:
                item = self.db["info"][ref]
                res.append((item["method"], ref))
                if func(_level, item["level"]):
                    _level = item["level"]
            for ref, _dic in self.db["info"].items():
                if ref in _refs:
                    continue
                elif func(_level, _dic["level"]):
                    if _dic["method"]:
                        _val = (_dic["method"], ref)
                        if _val not in res:
                            res.append(_val)
            return res

    def pick(self, req_authn_context=None):
        """
        Given the authentication context find zero or more places where
        the user could be sent next. Ordered according to security level.

        :param req_authn_context: The requested context as an
            RequestedAuthnContext instance
        :return: An URL
        """

        if req_authn_context is None:
            return self._pick_by_class_ref(UNSPECIFIED, "minimum")
        if req_authn_context.authn_context_class_ref:
            if req_authn_context.comparison:
                _cmp = req_authn_context.comparison
            else:
                _cmp = "exact"
            if _cmp == "exact":
                res = []
                for cls_ref in req_authn_context.authn_context_class_ref:
                    res += self._pick_by_class_ref(cls_ref.text, _cmp)
                return res
            else:
                return self._pick_by_class_ref(req_authn_context.authn_context_class_ref[0].text, _cmp)
        elif req_authn_context.authn_context_decl_ref:
            if req_authn_context.comparison:
                _cmp = req_authn_context.comparison
            else:
                _cmp = "exact"
            return self._pick_by_class_ref(req_authn_context.authn_context_decl_ref, _cmp)

    def match(self, requested, provided):
        if requested == provided:
            return True
        else:
            return False

    def __getitem__(self, ref):
        return self.db["info"][ref]

    def get_authn_by_accr(self, accr):
        _ids = self.db["key"][accr]
        return self[_ids[0]]


def authn_context_factory(text):
    # brute force
    for mod in [ippword, mobiletwofactor, ppt, pword, sslcert]:
        inst = mod.authentication_context_declaration_from_string(text)
        if inst:
            return inst

    return None


def authn_context_decl_from_extension_elements(extelems):
    res = extension_elements_to_elements(extelems, [ippword, mobiletwofactor, ppt, pword, sslcert])
    try:
        return res[0]
    except IndexError:
        return None


def authn_context_class_ref(ref):
    return AuthnContext(authn_context_class_ref=AuthnContextClassRef(text=ref))


def requested_authn_context(class_ref, comparison="minimum"):
    if not isinstance(class_ref, list):
        class_ref = [class_ref]
    return RequestedAuthnContext(
        authn_context_class_ref=[AuthnContextClassRef(text=i) for i in class_ref], comparison=comparison
    )
