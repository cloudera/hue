"""Contains classes and functions that are necessary to implement
different bindings.

Bindings normally consists of three parts:
- rules about what to send
- how to package the information
- which protocol to use
"""

import base64


try:
    import html
except Exception:
    import cgi as html  # type: ignore[no-redef]

import logging
from urllib.parse import urlencode
from urllib.parse import urlparse
from xml.etree import ElementTree as ElementTree

import defusedxml.ElementTree

import saml2
from saml2.s_utils import deflate_and_base64_encode
from saml2.sigver import REQ_ORDER
from saml2.sigver import RESP_ORDER
from saml2.xmldsig import SIG_ALLOWED_ALG


logger = logging.getLogger(__name__)

NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"

HTML_INPUT_ELEMENT_SPEC = '<input type="{type}" name="{name}" value="{val}"/>'

HTML_FORM_SPEC = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
  </head>
  <body onload="document.forms[0].submit()">
    <noscript>
      <p>
        <strong>Note:</strong>
        Since your browser does not support JavaScript,
        you must press the Continue button once to proceed.
      </p>
    </noscript>
    <form action="{action}" method="post">
      {saml_response_input}
      {relay_state_input}
      <noscript>
        <input type="submit" value="Continue"/>
      </noscript>
    </form>
  </body>
</html>"""


def _html_escape(payload):
    return html.escape(payload, quote=True)


def http_form_post_message(message, location, relay_state="", typ="SAMLRequest", **kwargs):
    """The HTTP POST binding defines a mechanism by which SAML protocol
    messages may be transmitted within the base64-encoded content of a
    HTML form control.

    :param message: The message
    :param location: Where the form should be posted to
    :param relay_state: for preserving and conveying state information
    :return: A tuple containing header information and a HTML message.
    """
    if not isinstance(message, str):
        message = str(message)
    if not isinstance(message, bytes):
        message = message.encode("utf-8")

    if typ == "SAMLRequest" or typ == "SAMLResponse":
        _msg = base64.b64encode(message)
    else:
        _msg = message
    _msg = _msg.decode("ascii")

    saml_response_input = HTML_INPUT_ELEMENT_SPEC.format(name=_html_escape(typ), val=_html_escape(_msg), type="hidden")

    relay_state_input = ""
    if relay_state:
        relay_state_input = HTML_INPUT_ELEMENT_SPEC.format(
            name="RelayState", val=_html_escape(relay_state), type="hidden"
        )

    response = HTML_FORM_SPEC.format(
        saml_response_input=saml_response_input, relay_state_input=relay_state_input, action=location
    )

    return {"headers": [("Content-type", "text/html")], "data": response, "status": 200}


def http_post_message(message, relay_state="", typ="SAMLRequest", **kwargs):
    """

    :param message: The message
    :param relay_state: for preserving and conveying state information
    :return: A tuple containing header information and a HTML message.
    """
    if not isinstance(message, str):
        message = str(message)
    if not isinstance(message, bytes):
        message = message.encode("utf-8")

    if typ == "SAMLRequest" or typ == "SAMLResponse":
        _msg = base64.b64encode(message)
    else:
        _msg = message
    _msg = _msg.decode("ascii")

    part = {typ: _msg}
    if relay_state:
        part["RelayState"] = relay_state

    return {"headers": [("Content-type", "application/x-www-form-urlencoded")], "data": urlencode(part), "status": 200}


def http_redirect_message(
    message,
    location,
    relay_state="",
    typ="SAMLRequest",
    sigalg=None,
    sign=None,
    backend=None,
):
    """The HTTP Redirect binding defines a mechanism by which SAML protocol
    messages can be transmitted within URL parameters.
    Messages are encoded for use with this binding using a URL encoding
    technique, and transmitted using the HTTP GET method.

    The DEFLATE Encoding is used in this function.

    :param message: The message
    :param location: Where the message should be posted to
    :param relay_state: for preserving and conveying state information
    :param typ: What type of message it is SAMLRequest/SAMLResponse/SAMLart
    :param sigalg: Which algorithm the signature function will use to sign
        the message
    :param sign: Whether the message should be signed
    :return: A tuple containing header information and a HTML message.
    """

    if not isinstance(message, str):
        message = f"{message}"

    _order = None
    if typ in ["SAMLRequest", "SAMLResponse"]:
        if typ == "SAMLRequest":
            _order = REQ_ORDER
        else:
            _order = RESP_ORDER
        args = {typ: deflate_and_base64_encode(message)}
    elif typ == "SAMLart":
        args = {typ: message}
    else:
        raise Exception(f"Unknown message type: {typ}")

    if relay_state:
        args["RelayState"] = relay_state

    if sign:
        # sigalgs, should be one defined in xmldsig
        if sigalg not in [long_name for short_name, long_name in SIG_ALLOWED_ALG]:
            raise Exception(f"Signature algo not in allowed list: {sigalg}")
        signer = backend.get_signer(sigalg) if sign and sigalg else None
        if not signer:
            raise Exception(f"Could not init signer fro algo {sigalg}")

        args["SigAlg"] = sigalg
        string = "&".join(urlencode({k: args[k]}) for k in _order if k in args)
        string_enc = string.encode("ascii")
        args["Signature"] = base64.b64encode(signer.sign(string_enc))

    string = urlencode(args)
    glue_char = "&" if urlparse(location).query else "?"
    login_url = glue_char.join([location, string])
    headers = [("Location", str(login_url))]
    body = []

    return {"headers": headers, "data": body, "status": 303}


DUMMY_NAMESPACE = "http://example.org/"
PREFIX = '<?xml version="1.0" encoding="UTF-8"?>'


def make_soap_enveloped_saml_thingy(thingy, header_parts=None):
    """Returns a soap envelope containing a SAML request
    as a text string.

    :param thingy: The SAML thingy
    :return: The SOAP envelope as a string
    """
    envelope = ElementTree.Element("")
    envelope.tag = "{%s}Envelope" % NAMESPACE

    if header_parts:
        header = ElementTree.Element("")
        header.tag = "{%s}Header" % NAMESPACE
        envelope.append(header)
        for part in header_parts:
            # This doesn't work if the headers are signed
            part.become_child_element_of(header)

    body = ElementTree.Element("")
    body.tag = "{%s}Body" % NAMESPACE
    envelope.append(body)

    if isinstance(thingy, str):
        # remove the first XML version/encoding line
        if thingy[0:5].lower() == "<?xml":
            logger.debug("thingy0: %s", thingy)
            _part = thingy.split("\n")
            thingy = "\n".join(_part[1:])
        thingy = thingy.replace(PREFIX, "")
        logger.debug("thingy: %s", thingy)
        _child = ElementTree.Element("")
        _child.tag = "{%s}FuddleMuddle" % DUMMY_NAMESPACE
        body.append(_child)
        _str = ElementTree.tostring(envelope, encoding="UTF-8")
        if isinstance(_str, bytes):
            _str = _str.decode("utf-8")
        logger.debug("SOAP precursor: %s", _str)
        # find an remove the namespace definition
        i = _str.find(DUMMY_NAMESPACE)
        j = _str.rfind("xmlns:", 0, i)
        cut1 = _str[j : i + len(DUMMY_NAMESPACE) + 1]
        _str = _str.replace(cut1, "")
        first = _str.find(f"<{cut1[6:9]}:FuddleMuddle")
        last = _str.find(">", first + 14)
        cut2 = _str[first : last + 1]
        return _str.replace(cut2, thingy)
    else:
        thingy.become_child_element_of(body)
        return ElementTree.tostring(envelope, encoding="UTF-8")


def http_soap_message(message):
    return {
        "headers": [("Content-type", "application/soap+xml")],
        "data": make_soap_enveloped_saml_thingy(message),
        "status": 200,
    }


def http_paos(message, extra=None):
    return {
        "headers": [("Content-type", "application/soap+xml")],
        "data": make_soap_enveloped_saml_thingy(message, extra),
        "status": 200,
    }


def parse_soap_enveloped_saml(text, body_class, header_class=None):
    """Parses a SOAP enveloped SAML thing and returns header parts and body

    :param text: The SOAP object as XML
    :return: header parts and body as saml.samlbase instances
    """
    envelope = defusedxml.ElementTree.fromstring(text)

    envelope_tag = "{%s}Envelope" % NAMESPACE
    if envelope.tag != envelope_tag:
        raise ValueError(f"Invalid envelope tag '{envelope.tag}' should be '{envelope_tag}'")

    # print(len(envelope))
    body = None
    header = {}
    for part in envelope:
        # print(">",part.tag)
        if part.tag == "{%s}Body" % NAMESPACE:
            for sub in part:
                try:
                    body = saml2.create_class_from_element_tree(body_class, sub)
                except Exception:
                    raise Exception(f"Wrong body type ({sub.tag}) in SOAP envelope")
        elif part.tag == "{%s}Header" % NAMESPACE:
            if not header_class:
                raise Exception("Header where I didn't expect one")
            # print("--- HEADER ---")
            for sub in part:
                # print(">>",sub.tag)
                for klass in header_class:
                    # print("?{%s}%s" % (klass.c_namespace,klass.c_tag))
                    if sub.tag == f"{{{klass.c_namespace}}}{klass.c_tag}":
                        header[sub.tag] = saml2.create_class_from_element_tree(klass, sub)
                        break

    return body, header


# -----------------------------------------------------------------------------

PACKING = {
    saml2.BINDING_HTTP_REDIRECT: http_redirect_message,
    saml2.BINDING_HTTP_POST: http_form_post_message,
}


def packager(identifier):
    try:
        return PACKING[identifier]
    except KeyError:
        raise Exception(f"Unknown binding type: {identifier}")


def factory(binding, message, location, relay_state="", typ="SAMLRequest", **kwargs):
    return PACKING[binding](message, location, relay_state, typ, **kwargs)
