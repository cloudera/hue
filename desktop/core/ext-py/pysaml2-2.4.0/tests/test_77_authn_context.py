
__author__ = 'rolandh'

ex1 = """<AuthenticationContextDeclaration
  xmlns="urn:oasis:names:tc:SAML:2.0:ac:classes:Password">
  <AuthnMethod>
    <Authenticator>
      <RestrictedPassword>
        <Length min="4"/>
      </RestrictedPassword>
    </Authenticator>
  </AuthnMethod>
</AuthenticationContextDeclaration>"""

from saml2.saml import AuthnContext
from saml2.saml import authn_context_from_string
from saml2.saml import AuthnContextClassRef
from saml2.samlp import RequestedAuthnContext
from saml2.authn_context import pword
from saml2.authn_context import ppt
from saml2.authn_context import authn_context_class_ref
from saml2.authn_context import requested_authn_context
from saml2.authn_context import PASSWORDPROTECTEDTRANSPORT
from saml2.authn_context import AL1
from saml2.authn_context import AL2
from saml2.authn_context import AL3
from saml2.authn_context import AL4
from saml2.authn_context import AuthnBroker
from saml2.authn_context import authn_context_decl_from_extension_elements
from saml2.authn_context import authn_context_factory

length = pword.Length(min="4")
restricted_password = pword.RestrictedPassword(length=length)
authenticator = pword.Authenticator(restricted_password=restricted_password)
authn_method = pword.AuthnMethod(authenticator=authenticator)
ACD = pword.AuthenticationContextDeclaration(authn_method=authn_method)

AUTHNCTXT = AuthnContext(authn_context_decl=ACD)
REQAUTHNCTXT = RequestedAuthnContext(authn_context_decl_ref=ACD.c_namespace)

def test_passwd():
    inst = ACD
    inst2 = pword.authentication_context_declaration_from_string(ex1)

    assert inst == inst2


def test_factory():
    inst_pw = pword.authentication_context_declaration_from_string(ex1)
    inst = authn_context_factory(ex1)

    assert inst_pw == inst


def test_authn_decl_in_authn_context():
    authnctxt = AuthnContext(authn_context_decl=ACD)

    acs = authn_context_from_string("%s" % authnctxt)
    if acs.extension_elements:
        cacd = authn_context_decl_from_extension_elements(
            acs.extension_elements)
        if cacd:
            acs.authn_context_decl = cacd

    assert acs.authn_context_decl == ACD


def test_authn_1():
    ac = authn_context_class_ref(PASSWORDPROTECTEDTRANSPORT)
    rac = requested_authn_context(PASSWORDPROTECTEDTRANSPORT)
    authn = AuthnBroker()
    target = "https://example.org/login"
    authn.add(ac, target, 1, "http://www.example.com")

    result = authn.pick(rac)
    assert len(result) == 1
    method, reference = result[0]
    assert target == method


def test_authn_2():
    authn = AuthnBroker()
    target = "https://example.org/login"
    authn.add(AUTHNCTXT, target, 10, "https://example.org")

    result = authn.pick(REQAUTHNCTXT)
    assert len(result) == 1
    method, reference = result[0]
    assert target == method


REF2METHOD = {
    AL1: "https://example.com/authn/pin",
    AL2: "https://example.com/authn/passwd",
    AL3: "https://example.com/authn/multifact",
    AL4: "https://example.com/authn/cert"
}


def test_authn_3():
    authn = AuthnBroker()
    level = 0
    for ref in [AL1, AL2, AL3, AL4]:
        level += 4
        ac = authn_context_class_ref(ref)

        authn.add(ac, REF2METHOD[ref], level,
                  "https://www.example.com/%s" % "al%d" % level)

    rac = requested_authn_context(AL1, "minimum")

    info = authn.pick(rac)
    assert len(info) == 4
    method, ref = info[0]
    assert REF2METHOD[AL1] == method

    rac = requested_authn_context(AL2, "minimum")

    info = authn.pick(rac)
    assert len(info) == 3
    method, ref = info[0]
    assert REF2METHOD[AL2] == method

    rac = requested_authn_context(AL3, "minimum")

    info = authn.pick(rac)
    assert len(info) == 2
    method, ref = info[0]
    assert REF2METHOD[AL3] == method

    rac = requested_authn_context(AL4, "minimum")

    info = authn.pick(rac)
    assert len(info) == 1
    method, ref = info[0]
    assert REF2METHOD[AL4] == method

    rac = requested_authn_context(AL1, "exact")

    info = authn.pick(rac)
    assert len(info) == 1
    method, ref = info[0]
    assert REF2METHOD[AL1] == method

    rac = requested_authn_context([AL1, AL2], "exact")

    info = authn.pick(rac)
    assert len(info) == 2
    method, ref = info[0]
    assert REF2METHOD[AL1] == method
    method, ref = info[1]
    assert REF2METHOD[AL2] == method

    rac = requested_authn_context([AL3, AL2], "exact")

    info = authn.pick(rac)
    assert len(info) == 2
    method, ref = info[0]
    assert REF2METHOD[AL3] == method
    method, ref = info[1]
    assert REF2METHOD[AL2] == method

    rac = requested_authn_context(AL1, "better")

    info = authn.pick(rac)
    assert len(info) == 3


if __name__ == "__main__":
    test_authn_3()
