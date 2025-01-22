""" Functions connected to signing and verifying.
Based on the use of xmlsec1 binaries and not the python xmlsec module.
"""

import base64
import datetime
import hashlib
import itertools
import logging
import os
import re
from subprocess import PIPE
from subprocess import Popen
import sys
from tempfile import NamedTemporaryFile
from time import mktime
from uuid import uuid4 as gen_random_key

import dateutil


# importlib.resources was introduced in python 3.7
# files API from importlib.resources introduced in python 3.9
if sys.version_info[:2] >= (3, 9):
    from importlib.resources import files as _resource_files
else:
    from importlib_resources import files as _resource_files

from urllib import parse

from OpenSSL import crypto
import pytz

from saml2 import ExtensionElement
from saml2 import SamlBase
from saml2 import SAMLError
from saml2 import class_name
from saml2 import extension_elements_to_elements
from saml2 import saml
from saml2 import samlp
from saml2.cert import CertificateError
from saml2.cert import OpenSSLWrapper
from saml2.cert import read_cert_from_file
import saml2.cryptography.asymmetric
import saml2.cryptography.pki
import saml2.data.templates as _data_template
from saml2.extension import pefim
from saml2.extension.pefim import SPCertEnc
from saml2.s_utils import Unsupported
from saml2.saml import EncryptedAssertion
from saml2.time_util import str_to_time
from saml2.xml.schema import XMLSchemaError
from saml2.xml.schema import validate as validate_doc_with_schema
from saml2.xmldsig import ALLOWED_CANONICALIZATIONS
from saml2.xmldsig import ALLOWED_TRANSFORMS
from saml2.xmldsig import SIG_RSA_SHA1
from saml2.xmldsig import SIG_RSA_SHA224
from saml2.xmldsig import SIG_RSA_SHA256
from saml2.xmldsig import SIG_RSA_SHA384
from saml2.xmldsig import SIG_RSA_SHA512
from saml2.xmldsig import TRANSFORM_C14N
from saml2.xmldsig import TRANSFORM_ENVELOPED
import saml2.xmldsig as ds
from saml2.xmlenc import CipherData
from saml2.xmlenc import CipherValue
from saml2.xmlenc import EncryptedData
from saml2.xmlenc import EncryptedKey
from saml2.xmlenc import EncryptionMethod


logger = logging.getLogger(__name__)

SIG = f"{{{ds.NAMESPACE}#}}Signature"

# RSA_1_5 is considered deprecated
RSA_1_5 = "http://www.w3.org/2001/04/xmlenc#rsa-1_5"
TRIPLE_DES_CBC = "http://www.w3.org/2001/04/xmlenc#tripledes-cbc"
RSA_OAEP_MGF1P = "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"


class SigverError(SAMLError):
    pass


class CertificateTooOld(SigverError):
    pass


class XmlsecError(SigverError):
    pass


class MissingKey(SigverError):
    pass


class DecryptError(XmlsecError):
    pass


class EncryptError(XmlsecError):
    pass


class SignatureError(XmlsecError):
    pass


class BadSignature(SigverError):
    """The signature is invalid."""


def get_pem_wrapped_unwrapped(cert):
    begin_cert = "-----BEGIN CERTIFICATE-----\n"
    end_cert = "\n-----END CERTIFICATE-----\n"
    unwrapped_cert = re.sub(f"{begin_cert}|{end_cert}", "", cert)
    wrapped_cert = f"{begin_cert}{unwrapped_cert}{end_cert}"
    return wrapped_cert, unwrapped_cert


def rm_xmltag(statement):
    XMLTAG = "<?xml version='1.0'?>"
    PREFIX1 = "<?xml version='1.0' encoding='UTF-8'?>"
    PREFIX2 = '<?xml version="1.0" encoding="UTF-8"?>'

    try:
        _t = statement.startswith(XMLTAG)
    except TypeError:
        statement = statement.decode()
        _t = statement.startswith(XMLTAG)

    if _t:
        statement = statement[len(XMLTAG) :]
        if statement[0] == "\n":
            statement = statement[1:]
    elif statement.startswith(PREFIX1):
        statement = statement[len(PREFIX1) :]
        if statement[0] == "\n":
            statement = statement[1:]
    elif statement.startswith(PREFIX2):
        statement = statement[len(PREFIX2) :]
        if statement[0] == "\n":
            statement = statement[1:]

    return statement


def signed(item):
    """
    Is any part of the document signed ?

    :param item: A Samlbase instance
    :return: True if some part of it is signed
    """
    if SIG in item.c_children.keys() and item.signature:
        return True
    else:
        for prop in item.c_child_order:
            child = getattr(item, prop, None)
            if isinstance(child, list):
                for chi in child:
                    if signed(chi):
                        return True
            elif child and signed(child):
                return True

    return False


def get_xmlsec_binary(paths=None):
    """
    Tries to find the xmlsec1 binary.

    :param paths: Non-system path paths which should be searched when
        looking for xmlsec1
    :return: full name of the xmlsec1 binary found. If no binaries are
        found then an exception is raised.
    """
    if os.name == "posix":
        bin_name = ["xmlsec1"]
    elif os.name == "nt":
        bin_name = ["xmlsec.exe", "xmlsec1.exe"]
    else:  # Default !?
        bin_name = ["xmlsec1"]

    if paths:
        for bname in bin_name:
            for path in paths:
                fil = os.path.join(path, bname)
                try:
                    if os.lstat(fil):
                        return fil
                except OSError:
                    pass

    for path in os.environ["PATH"].split(os.pathsep):
        for bname in bin_name:
            fil = os.path.join(path, bname)
            try:
                if os.lstat(fil):
                    return fil
            except OSError:
                pass

    raise SigverError(f"Cannot find {bin_name}")


def _get_xmlsec_cryptobackend(path=None, search_paths=None, delete_tmpfiles=True):
    """
    Initialize a CryptoBackendXmlSec1 crypto backend.

    This function is now internal to this module.
    """
    if path is None:
        path = get_xmlsec_binary(paths=search_paths)
    return CryptoBackendXmlSec1(path, delete_tmpfiles=delete_tmpfiles)


NODE_NAME = "urn:oasis:names:tc:SAML:2.0:assertion:Assertion"
ENC_NODE_NAME = "urn:oasis:names:tc:SAML:2.0:assertion:EncryptedAssertion"
ENC_KEY_CLASS = "EncryptedKey"


def _make_vals(val, klass, seccont, klass_inst=None, prop=None, part=False, base64encode=False, elements_to_sign=None):
    """
    Creates a class instance with a specified value, the specified
    class instance may be a value on a property in a defined class instance.

    :param val: The value
    :param klass: The value class
    :param klass_inst: The class instance which has a property on which
        what this function returns is a value.
    :param prop: The property which the value should be assigned to.
    :param part: If the value is one of a possible list of values it should be
        handled slightly different compared to if it isn't.
    :return: Value class instance
    """
    cinst = None

    if isinstance(val, dict):
        cinst = _instance(klass, val, seccont, base64encode=base64encode, elements_to_sign=elements_to_sign)
    else:
        try:
            cinst = klass().set_text(val)
        except ValueError:
            if not part:
                cis = [
                    _make_vals(sval, klass, seccont, klass_inst, prop, True, base64encode, elements_to_sign)
                    for sval in val
                ]
                setattr(klass_inst, prop, cis)
            else:
                raise

    if part:
        return cinst
    else:
        if cinst:
            cis = [cinst]
            setattr(klass_inst, prop, cis)


def _instance(klass, ava, seccont, base64encode=False, elements_to_sign=None):
    instance = klass()

    for prop in instance.c_attributes.values():
        if prop in ava:
            if isinstance(ava[prop], bool):
                setattr(instance, prop, str(ava[prop]).encode())
            elif isinstance(ava[prop], int):
                setattr(instance, prop, str(ava[prop]))
            else:
                setattr(instance, prop, ava[prop])

    if "text" in ava:
        instance.set_text(ava["text"], base64encode)

    for prop, klassdef in instance.c_children.values():
        if prop in ava:
            if isinstance(klassdef, list):
                # means there can be a list of values
                _make_vals(
                    ava[prop],
                    klassdef[0],
                    seccont,
                    instance,
                    prop,
                    base64encode=base64encode,
                    elements_to_sign=elements_to_sign,
                )
            else:
                cis = _make_vals(ava[prop], klassdef, seccont, instance, prop, True, base64encode, elements_to_sign)
                setattr(instance, prop, cis)

    if "extension_elements" in ava:
        for item in ava["extension_elements"]:
            instance.extension_elements.append(ExtensionElement(item["tag"]).loadd(item))

    if "extension_attributes" in ava:
        for key, val in ava["extension_attributes"].items():
            instance.extension_attributes[key] = val

    if "signature" in ava:
        elements_to_sign.append((class_name(instance), instance.id))

    return instance


# XXX will actually sign the nodes
# XXX assumes pre_signature_part has already been called
# XXX calls sign without specifying sign_alg/digest_alg
# XXX this is fine as the algs are embeded in the document
# XXX as setup by pre_signature_part
# XXX !!expects instance string!!
def signed_instance_factory(instance, seccont, elements_to_sign=None):
    """

    :param instance: The instance to be signed or not
    :param seccont: The security context
    :param elements_to_sign: Which parts if any that should be signed
    :return: A class instance if not signed otherwise a string
    """
    if not elements_to_sign:
        return instance

    signed_xml = instance
    if not isinstance(instance, str):
        signed_xml = instance.to_string()

    for (node_name, nodeid) in elements_to_sign:
        signed_xml = seccont.sign_statement(signed_xml, node_name=node_name, node_id=nodeid)

    return signed_xml


def make_temp(content, suffix="", decode=True, delete_tmpfiles=True):
    """
    Create a temporary file with the given content.

    This is needed by xmlsec in some cases where only strings exist when files
    are expected.

    :param content: The information to be placed in the file
    :param suffix: The temporary file might have to have a specific
        suffix in certain circumstances.
    :param decode: The input content might be base64 coded. If so it
        must, in some cases, be decoded before being placed in the file.
    :param delete_tmpfiles: Whether to keep the tmp files or delete them when they are
        no longer in use
    :return: 2-tuple with file pointer ( so the calling function can
        close the file) and filename (which is for instance needed by the
        xmlsec function).
    """
    content_encoded = content.encode("utf-8") if not isinstance(content, bytes) else content
    content_raw = base64.b64decode(content_encoded) if decode else content_encoded
    ntf = NamedTemporaryFile(suffix=suffix, delete=delete_tmpfiles)
    ntf.write(content_raw)
    ntf.seek(0)
    return ntf


def split_len(seq, length):
    return [seq[i : i + length] for i in range(0, len(seq), length)]


M2_TIME_FORMAT = "%b %d %H:%M:%S %Y"


def to_time(_time):
    if not _time.endswith(" GMT"):
        raise ValueError("Time does not end with GMT")
    _time = _time[:-4]
    return mktime(str_to_time(_time, M2_TIME_FORMAT))


def active_cert(key):
    """
    Verifies that a key is active that is present time is after not_before
    and before not_after.

    :param key: The Key
    :return: True if the key is active else False
    """
    try:
        cert_str = pem_format(key)
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_str)
    except AttributeError:
        return False

    now = pytz.UTC.localize(datetime.datetime.utcnow())
    valid_from = dateutil.parser.parse(cert.get_notBefore())
    valid_to = dateutil.parser.parse(cert.get_notAfter())
    active = not cert.has_expired() and valid_from <= now < valid_to
    return active


def cert_from_key_info(key_info, ignore_age=False):
    """Get all X509 certs from a KeyInfo instance. Care is taken to make sure
    that the certs are continues sequences of bytes.

    All certificates appearing in an X509Data element MUST relate to the
    validation key by either containing it or being part of a certification
    chain that terminates in a certificate containing the validation key.

    :param key_info: The KeyInfo instance
    :return: A possibly empty list of certs
    """
    res = []
    for x509_data in key_info.x509_data:
        x509_certificate = x509_data.x509_certificate
        cert = x509_certificate.text.strip()
        cert = "\n".join(split_len("".join([s.strip() for s in cert.split()]), 64))
        if ignore_age or active_cert(cert):
            res.append(cert)
        else:
            logger.info("Inactive cert")
    return res


def cert_from_key_info_dict(key_info, ignore_age=False):
    """Get all X509 certs from a KeyInfo dictionary. Care is taken to make sure
    that the certs are continues sequences of bytes.

    All certificates appearing in an X509Data element MUST relate to the
    validation key by either containing it or being part of a certification
    chain that terminates in a certificate containing the validation key.

    :param key_info: The KeyInfo dictionary
    :return: A possibly empty list of certs in their text representation
    """
    res = []
    if "x509_data" not in key_info:
        return res

    for x509_data in key_info["x509_data"]:
        x509_certificate = x509_data["x509_certificate"]
        cert = x509_certificate["text"].strip()
        cert = "\n".join(split_len("".join([s.strip() for s in cert.split()]), 64))
        if ignore_age or active_cert(cert):
            res.append(cert)
        else:
            logger.info("Inactive cert")
    return res


def cert_from_instance(instance):
    """Find certificates that are part of an instance

    :param instance: An instance
    :return: possible empty list of certificates
    """
    if instance.signature:
        if instance.signature.key_info:
            return cert_from_key_info(instance.signature.key_info, ignore_age=True)
    return []


def extract_rsa_key_from_x509_cert(pem):
    cert = saml2.cryptography.pki.load_pem_x509_certificate(pem)
    return cert.public_key()


def pem_format(key):
    return os.linesep.join(["-----BEGIN CERTIFICATE-----", key, "-----END CERTIFICATE-----"]).encode("ascii")


def import_rsa_key_from_file(filename):
    with open(filename, "rb") as fd:
        data = fd.read()
    key = saml2.cryptography.asymmetric.load_pem_private_key(data)
    return key


def parse_xmlsec_verify_output(output, version=None):
    """Parse the output from xmlsec to try to find out if the
    command was successfull or not.

    :param output: The output from Popen
    :return: A boolean; True if the command was a success otherwise False
    """
    if version is None or version < (1, 3):
        for line in output.splitlines():
            if line == "OK":
                return True
            elif line == "FAIL":
                raise XmlsecError(output)
    else:
        for line in output.splitlines():
            if line == 'Verification status: OK':
                return True
            elif line == 'Verification status: FAILED':
                raise XmlsecError(output)
    raise XmlsecError(output)


def sha1_digest(msg):
    return hashlib.sha1(msg).digest()


class Signer:
    """Abstract base class for signing algorithms."""

    def __init__(self, key):
        self.key = key

    def sign(self, msg, key):
        """Sign ``msg`` with ``key`` and return the signature."""
        raise NotImplementedError

    def verify(self, msg, sig, key):
        """Return True if ``sig`` is a valid signature for ``msg``."""
        raise NotImplementedError


class RSASigner(Signer):
    def __init__(self, digest, key=None):
        Signer.__init__(self, key)
        self.digest = digest

    def sign(self, msg, key=None):
        return saml2.cryptography.asymmetric.key_sign(key or self.key, msg, self.digest)

    def verify(self, msg, sig, key=None):
        return saml2.cryptography.asymmetric.key_verify(key or self.key, sig, msg, self.digest)


SIGNER_ALGS = {
    SIG_RSA_SHA1: RSASigner(saml2.cryptography.asymmetric.hashes.SHA1()),
    SIG_RSA_SHA224: RSASigner(saml2.cryptography.asymmetric.hashes.SHA224()),
    SIG_RSA_SHA256: RSASigner(saml2.cryptography.asymmetric.hashes.SHA256()),
    SIG_RSA_SHA384: RSASigner(saml2.cryptography.asymmetric.hashes.SHA384()),
    SIG_RSA_SHA512: RSASigner(saml2.cryptography.asymmetric.hashes.SHA512()),
}

REQ_ORDER = [
    "SAMLRequest",
    "RelayState",
    "SigAlg",
]

RESP_ORDER = [
    "SAMLResponse",
    "RelayState",
    "SigAlg",
]


class RSACrypto:
    def __init__(self, key):
        self.key = key

    def get_signer(self, sigalg, sigkey=None):
        try:
            signer = SIGNER_ALGS[sigalg]
        except KeyError:
            return None
        else:
            if sigkey:
                signer.key = sigkey
            else:
                signer.key = self.key

        return signer


def verify_redirect_signature(saml_msg, crypto, cert=None, sigkey=None):
    """

    :param saml_msg: A dictionary with strings as values, *NOT* lists as
    produced by parse_qs.
    :param cert: A certificate to use when verifying the signature
    :return: True, if signature verified
    """

    try:
        signer = crypto.get_signer(saml_msg["SigAlg"], sigkey)
    except KeyError:
        raise Unsupported(f"Signature algorithm: {saml_msg['SigAlg']}")
    else:
        if saml_msg["SigAlg"] in SIGNER_ALGS:
            if "SAMLRequest" in saml_msg:
                _order = REQ_ORDER
            elif "SAMLResponse" in saml_msg:
                _order = RESP_ORDER
            else:
                raise Unsupported("Verifying signature on something that should not be signed")

            _args = saml_msg.copy()
            del _args["Signature"]  # everything but the signature
            string = "&".join([parse.urlencode({k: _args[k]}) for k in _order if k in _args]).encode("ascii")

            if cert:
                _key = extract_rsa_key_from_x509_cert(pem_format(cert))
            else:
                _key = sigkey

            _sign = base64.b64decode(saml_msg["Signature"])

            return bool(signer.verify(string, _sign, _key))


class CryptoBackend:
    @property
    def version(self):
        raise NotImplementedError()

    @property
    def version_nums(self):
        try:
            vns = tuple(int(t) for t in self.version.split("."))
        except ValueError:
            vns = (0, 0, 0)
        return vns

    def encrypt(self, text, recv_key, template, key_type):
        raise NotImplementedError()

    def encrypt_assertion(self, statement, enc_key, template, key_type, node_xpath):
        raise NotImplementedError()

    def decrypt(self, enctext, key_file):
        raise NotImplementedError()

    def sign_statement(self, statement, node_name, key_file, node_id):
        raise NotImplementedError()

    def validate_signature(self, enctext, cert_file, cert_type, node_name, node_id):
        raise NotImplementedError()


ASSERT_XPATH = "".join([f"/*[local-name()='{n}']" for n in ["Response", "EncryptedAssertion", "Assertion"]])


class CryptoBackendXmlSec1(CryptoBackend):
    """
    CryptoBackend implementation using external binary 1 to sign
    and verify XML documents.
    """

    __DEBUG = 0

    def __init__(self, xmlsec_binary, delete_tmpfiles=True, **kwargs):
        CryptoBackend.__init__(self, **kwargs)
        if not isinstance(xmlsec_binary, str):
            raise ValueError("xmlsec_binary should be of type string")
        self.xmlsec = xmlsec_binary
        self.delete_tmpfiles = delete_tmpfiles
        try:
            self.non_xml_crypto = RSACrypto(kwargs["rsa_key"])
        except KeyError:
            pass

    @property
    def version(self):
        com_list = [self.xmlsec, "--version"]
        pof = Popen(com_list, stderr=PIPE, stdout=PIPE)
        content, _ = pof.communicate()
        content = content.decode("ascii")
        try:
            return content.split(" ")[1]
        except IndexError:
            return "0.0.0"

    def encrypt(self, text, recv_key, template, session_key_type, xpath=""):
        """

        :param text: The text to be compiled
        :param recv_key: Filename of a file where the key resides
        :param template: Filename of a file with the pre-encryption part
        :param session_key_type: Type and size of a new session key
            'des-192' generates a new 192 bits DES key for DES3 encryption
        :param xpath: What should be encrypted
        :return:
        """
        logger.debug("Encryption input len: %d", len(text))
        tmp = make_temp(text, decode=False, delete_tmpfiles=self.delete_tmpfiles)
        com_list = [
            self.xmlsec,
            "--encrypt",
            "--pubkey-cert-pem",
            recv_key,
            "--session-key",
            session_key_type,
            "--xml-data",
            tmp.name,
        ]

        if xpath:
            com_list.extend(["--node-xpath", xpath])

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [template])
        except XmlsecError as e:
            raise EncryptError(com_list) from e

        return output

    def encrypt_assertion(self, statement, enc_key, template, key_type="des-192", node_xpath=None, node_id=None):
        """
        Will encrypt an assertion

        :param statement: A XML document that contains the assertion to encrypt
        :param enc_key: File name of a file containing the encryption key
        :param template: A template for the encryption part to be added.
        :param key_type: The type of session key to use.
        :return: The encrypted text
        """

        if isinstance(statement, SamlBase):
            statement = pre_encrypt_assertion(statement)

        tmp = make_temp(str(statement), decode=False, delete_tmpfiles=self.delete_tmpfiles)
        tmp2 = make_temp(str(template), decode=False, delete_tmpfiles=self.delete_tmpfiles)

        if not node_xpath:
            node_xpath = ASSERT_XPATH

        com_list = [
            self.xmlsec,
            "--encrypt",
            "--pubkey-cert-pem",
            enc_key,
            "--session-key",
            key_type,
            "--xml-data",
            tmp.name,
            "--node-xpath",
            node_xpath,
        ]

        if node_id:
            com_list.extend(["--node-id", node_id])

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [tmp2.name])
        except XmlsecError as e:
            raise EncryptError(com_list) from e

        return output.decode("utf-8")

    def decrypt(self, enctext, key_file):
        """

        :param enctext: XML document containing an encrypted part
        :param key_file: The key to use for the decryption
        :return: The decrypted document
        """

        logger.debug("Decrypt input len: %d", len(enctext))
        tmp = make_temp(enctext, decode=False, delete_tmpfiles=self.delete_tmpfiles)

        com_list = [
            self.xmlsec,
            "--decrypt",
            "--privkey-pem",
            key_file,
            "--id-attr:Id",
            ENC_KEY_CLASS,
        ]

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [tmp.name])
        except XmlsecError as e:
            raise DecryptError(com_list) from e

        return output.decode("utf-8")

    def sign_statement(self, statement, node_name, key_file, node_id):
        """
        Sign an XML statement.

        :param statement: The statement to be signed
        :param node_name: string like 'urn:oasis:names:...:Assertion'
        :param key_file: The file where the key can be found
        :param node_id:
        :return: The signed statement
        """
        if isinstance(statement, SamlBase):
            statement = str(statement)

        tmp = make_temp(statement, suffix=".xml", decode=False, delete_tmpfiles=self.delete_tmpfiles)

        com_list = [
            self.xmlsec,
            "--sign",
            "--privkey-pem",
            key_file,
            "--id-attr:ID",
            node_name,
        ]

        if node_id:
            com_list.extend(["--node-id", node_id])

        try:
            (stdout, stderr, output) = self._run_xmlsec(com_list, [tmp.name])
        except XmlsecError as e:
            raise SignatureError(com_list) from e

        # this does not work if --store-signatures is used
        if output:
            return output.decode("utf-8")
        if stdout:
            return stdout.decode("utf-8")
        raise SignatureError(stderr)

    def validate_signature(self, signedtext, cert_file, cert_type, node_name, node_id):
        """
        Validate signature on XML document.

        :param signedtext: The XML document as a string
        :param cert_file: The public key that was used to sign the document
        :param cert_type: The file type of the certificate
        :param node_name: The name of the class that is signed
        :param node_id: The identifier of the node
        :return: Boolean True if the signature was correct otherwise False.
        """
        if not isinstance(signedtext, bytes):
            signedtext = signedtext.encode("utf-8")

        tmp = make_temp(signedtext, suffix=".xml", decode=False, delete_tmpfiles=self.delete_tmpfiles)

        com_list = [
            self.xmlsec,
            "--verify",
            "--enabled-reference-uris",
            "empty,same-doc",
            "--enabled-key-data",
            "raw-x509-cert",
            f"--pubkey-cert-{cert_type}",
            cert_file,
            "--id-attr:ID",
            node_name,
        ]

        if node_id:
            com_list.extend(["--node-id", node_id])

        try:
            (_stdout, stderr, _output) = self._run_xmlsec(com_list, [tmp.name])
        except XmlsecError as e:
            raise SignatureError(com_list) from e

        return parse_xmlsec_verify_output(stderr, self.version_nums)

    def _run_xmlsec(self, com_list, extra_args):
        """
        Common code to invoke xmlsec and parse the output.
        :param com_list: Key-value parameter list for xmlsec
        :param extra_args: Positional parameters to be appended after all
            key-value parameters
        :result: Whatever xmlsec wrote to an --output temporary file
        """
        with NamedTemporaryFile(suffix=".xml") as ntf:
            com_list.extend(["--output", ntf.name])
            if self.version_nums >= (1, 3):
                com_list.extend(['--lax-key-search'])
            com_list += extra_args

            logger.debug("xmlsec command: %s", " ".join(com_list))

            pof = Popen(com_list, stderr=PIPE, stdout=PIPE)
            p_out, p_err = pof.communicate()
            p_out = p_out.decode()
            p_err = p_err.decode()

            if pof.returncode != 0:
                errmsg = f"returncode={pof.returncode}\nerror={p_err}\noutput={p_out}"
                logger.error(errmsg)
                raise XmlsecError(errmsg)

            ntf.seek(0)
            return p_out, p_err, ntf.read()


class CryptoBackendXMLSecurity(CryptoBackend):
    """
    CryptoBackend implementation using pyXMLSecurity to sign and verify
    XML documents.

    Encrypt and decrypt is currently unsupported by pyXMLSecurity.

    pyXMLSecurity uses lxml (libxml2) to parse XML data, but otherwise
    try to get by with native Python code. It does native Python RSA
    signatures, or alternatively PyKCS11 to offload cryptographic work
    to an external PKCS#11 module.
    """

    def __init__(self):
        CryptoBackend.__init__(self)

    @property
    def version(self):
        try:
            import xmlsec
            return xmlsec.__version__
        except (ImportError, AttributeError):
            return "0.0.0"

    def sign_statement(self, statement, node_name, key_file, node_id):
        """
        Sign an XML statement.

        The parameters actually used in this CryptoBackend
        implementation are :

        :param statement: XML as string
        :param node_name: Name of the node to sign
        :param key_file: xmlsec key_spec string(), filename,
            'pkcs11://' URI or PEM data
        :returns: Signed XML as string
        """
        import lxml.etree
        import xmlsec

        xml = xmlsec.parse_xml(statement)
        signed = xmlsec.sign(xml, key_file)
        signed_str = lxml.etree.tostring(signed, xml_declaration=False, encoding="UTF-8")
        if not isinstance(signed_str, str):
            signed_str = signed_str.decode("utf-8")
        return signed_str

    def validate_signature(self, signedtext, cert_file, cert_type, node_name, node_id):
        """
        Validate signature on XML document.

        The parameters actually used in this CryptoBackend
        implementation are :

        :param signedtext: The signed XML data as string
        :param cert_file: xmlsec key_spec string(), filename,
            'pkcs11://' URI or PEM data
        :param cert_type: string, must be 'pem' for now
        :returns: True on successful validation, False otherwise
        """
        if cert_type != "pem":
            raise Unsupported("Only PEM certs supported here")

        import xmlsec

        xml = xmlsec.parse_xml(signedtext)

        try:
            return xmlsec.verify(xml, cert_file)
        except xmlsec.XMLSigException:
            return False


def security_context(conf):
    """Creates a security context based on the configuration

    :param conf: The configuration, this is a Config instance
    :return: A SecurityContext instance
    """
    if not conf:
        return None

    try:
        metadata = conf.metadata
    except AttributeError:
        metadata = None

    sec_backend = None

    if conf.crypto_backend == "xmlsec1":
        xmlsec_binary = conf.xmlsec_binary

        if not xmlsec_binary:
            try:
                _path = conf.xmlsec_path
            except AttributeError:
                _path = []
            xmlsec_binary = get_xmlsec_binary(_path)

        # verify that xmlsec is where it's supposed to be
        if not os.path.exists(xmlsec_binary):
            # if not os.access(, os.F_OK):
            err_msg = "xmlsec binary not found: {binary}"
            err_msg = err_msg.format(binary=xmlsec_binary)
            raise SigverError(err_msg)

        crypto = _get_xmlsec_cryptobackend(xmlsec_binary, delete_tmpfiles=conf.delete_tmpfiles)

        _file_name = conf.getattr("key_file", "")
        if _file_name:
            try:
                rsa_key = import_rsa_key_from_file(_file_name)
            except Exception as err:
                logger.error(f"Cannot import key from {_file_name}: {err}")
                raise
            else:
                sec_backend = RSACrypto(rsa_key)
    elif conf.crypto_backend == "XMLSecurity":
        # new and somewhat untested pyXMLSecurity crypto backend.
        crypto = CryptoBackendXMLSecurity()
    else:
        err_msg = "Unknown crypto_backend {backend}"
        err_msg = err_msg.format(backend=conf.crypto_backend)
        raise SigverError(err_msg)

    enc_key_files = []
    if conf.encryption_keypairs is not None:
        for _encryption_keypair in conf.encryption_keypairs:
            if "key_file" in _encryption_keypair:
                enc_key_files.append(_encryption_keypair["key_file"])

    return SecurityContext(
        crypto,
        conf.key_file,
        cert_file=conf.cert_file,
        metadata=metadata,
        only_use_keys_in_metadata=conf.only_use_keys_in_metadata,
        cert_handler_extra_class=conf.cert_handler_extra_class,
        generate_cert_info=conf.generate_cert_info,
        tmp_cert_file=conf.tmp_cert_file,
        tmp_key_file=conf.tmp_key_file,
        validate_certificate=conf.validate_certificate,
        enc_key_files=enc_key_files,
        encryption_keypairs=conf.encryption_keypairs,
        sec_backend=sec_backend,
        delete_tmpfiles=conf.delete_tmpfiles,
    )


def encrypt_cert_from_item(item):
    _encrypt_cert = None
    try:
        try:
            _elem = extension_elements_to_elements(item.extensions.extension_elements, [pefim, ds])
        except Exception:
            _elem = extension_elements_to_elements(item.extension_elements[0].children, [pefim, ds])

        for _tmp_elem in _elem:
            if isinstance(_tmp_elem, SPCertEnc):
                for _tmp_key_info in _tmp_elem.key_info:
                    if _tmp_key_info.x509_data is not None and len(_tmp_key_info.x509_data) > 0:
                        _encrypt_cert = _tmp_key_info.x509_data[0].x509_certificate.text
                        break
    except Exception:
        pass

    if _encrypt_cert is not None:
        wrapped_cert, unwrapped_cert = get_pem_wrapped_unwrapped(_encrypt_cert)
        _encrypt_cert = wrapped_cert
    return _encrypt_cert


class CertHandlerExtra:
    def __init__(self):
        pass

    def use_generate_cert_func(self):
        raise Exception("use_generate_cert_func function must be implemented")

    def generate_cert(self, generate_cert_info, root_cert_string, root_key_string):
        raise Exception("generate_cert function must be implemented")
        # Excepts to return (cert_string, key_string)

    def use_validate_cert_func(self):
        raise Exception("use_validate_cert_func function must be implemented")

    def validate_cert(self, cert_str, root_cert_string, root_key_string):
        raise Exception("validate_cert function must be implemented")
        # Excepts to return True/False


class CertHandler:
    def __init__(
        self,
        security_context,
        cert_file=None,
        cert_type="pem",
        key_file=None,
        key_type="pem",
        generate_cert_info=None,
        cert_handler_extra_class=None,
        tmp_cert_file=None,
        tmp_key_file=None,
        verify_cert=False,
    ):
        """
        Initiates the class for handling certificates. Enables the certificates
        to either be a single certificate as base functionality or makes it
        possible to generate a new certificate for each call to the function.

        :param security_context:
        :param cert_file:
        :param cert_type:
        :param key_file:
        :param key_type:
        :param generate_cert_info:
        :param cert_handler_extra_class:
        :param tmp_cert_file:
        :param tmp_key_file:
        :param verify_cert:
        """

        self._verify_cert = False
        self._generate_cert = False
        # This cert do not have to be valid, it is just the last cert to be
        # validated.
        self._last_cert_verified = None
        self._last_validated_cert = None
        if cert_type == "pem" and key_type == "pem":
            self._verify_cert = verify_cert is True
            self._security_context = security_context
            self._osw = OpenSSLWrapper()
            if key_file and os.path.isfile(key_file):
                self._key_str = self._osw.read_str_from_file(key_file, key_type)
            else:
                self._key_str = ""
            if cert_file and os.path.isfile(cert_file):
                self._cert_str = self._osw.read_str_from_file(cert_file, cert_type)
            else:
                self._cert_str = ""

            self._tmp_cert_str = self._cert_str
            self._tmp_key_str = self._key_str
            self._tmp_cert_file = tmp_cert_file
            self._tmp_key_file = tmp_key_file

            self._cert_info = None
            self._generate_cert_func_active = False
            if (
                generate_cert_info is not None
                and len(self._cert_str) > 0
                and len(self._key_str) > 0
                and tmp_key_file is not None
                and tmp_cert_file is not None
            ):
                self._generate_cert = True
                self._cert_info = generate_cert_info
                self._cert_handler_extra_class = cert_handler_extra_class

    def verify_cert(self, cert_file):
        if self._verify_cert:
            if cert_file and os.path.isfile(cert_file):
                cert_str = self._osw.read_str_from_file(cert_file, "pem")
            else:
                return False
            self._last_validated_cert = cert_str
            if self._cert_handler_extra_class is not None and self._cert_handler_extra_class.use_validate_cert_func():
                self._cert_handler_extra_class.validate_cert(cert_str, self._cert_str, self._key_str)
            else:
                valid, mess = self._osw.verify(self._cert_str, cert_str)
                logger.info("CertHandler.verify_cert: %s", mess)
                return valid
        return True

    def generate_cert(self):
        return self._generate_cert

    def update_cert(self, active=False, client_crt=None):
        if (self._generate_cert and active) or client_crt is not None:
            if client_crt is not None:
                self._tmp_cert_str = client_crt
                # No private key for signing
                self._tmp_key_str = ""
            elif self._cert_handler_extra_class is not None and self._cert_handler_extra_class.use_generate_cert_func():
                (self._tmp_cert_str, self._tmp_key_str) = self._cert_handler_extra_class.generate_cert(
                    self._cert_info, self._cert_str, self._key_str
                )
            else:
                self._tmp_cert_str, self._tmp_key_str = self._osw.create_certificate(self._cert_info, request=True)
                self._tmp_cert_str = self._osw.create_cert_signed_certificate(
                    self._cert_str, self._key_str, self._tmp_cert_str
                )
                valid, mess = self._osw.verify(self._cert_str, self._tmp_cert_str)
            self._osw.write_str_to_file(self._tmp_cert_file, self._tmp_cert_str)
            self._osw.write_str_to_file(self._tmp_key_file, self._tmp_key_str)
            self._security_context.key_file = self._tmp_key_file
            self._security_context.cert_file = self._tmp_cert_file
            self._security_context.key_type = "pem"
            self._security_context.cert_type = "pem"
            self._security_context.my_cert = read_cert_from_file(
                self._security_context.cert_file, self._security_context.cert_type
            )


# How to get a rsa pub key fingerprint from a certificate
# openssl x509 -inform pem -noout -in server.crt -pubkey > publickey.pem
# openssl rsa -inform pem -noout -in publickey.pem -pubin -modulus
class SecurityContext:
    my_cert = None

    def __init__(
        self,
        crypto,
        key_file="",
        key_type="pem",
        cert_file="",
        cert_type="pem",
        metadata=None,
        template="",
        encrypt_key_type="des-192",
        only_use_keys_in_metadata=False,
        cert_handler_extra_class=None,
        generate_cert_info=None,
        tmp_cert_file=None,
        tmp_key_file=None,
        validate_certificate=None,
        enc_key_files=None,
        enc_key_type="pem",
        encryption_keypairs=None,
        enc_cert_type="pem",
        sec_backend=None,
        delete_tmpfiles=True,
    ):

        if not isinstance(crypto, CryptoBackend):
            raise ValueError("crypto should be of type CryptoBackend")
        self.crypto = crypto

        if sec_backend and not isinstance(sec_backend, RSACrypto):
            raise ValueError("sec_backend should be of type RSACrypto")
        self.sec_backend = sec_backend

        # Your private key for signing
        self.key_file = key_file
        self.key_type = key_type

        # Your public key for signing
        self.cert_file = cert_file
        self.cert_type = cert_type

        # Your private key for encryption
        self.enc_key_files = enc_key_files
        self.enc_key_type = enc_key_type

        # Your public key for encryption
        self.encryption_keypairs = encryption_keypairs
        self.enc_cert_type = enc_cert_type

        self.my_cert = read_cert_from_file(cert_file, cert_type)

        self.cert_handler = CertHandler(
            self,
            cert_file,
            cert_type,
            key_file,
            key_type,
            generate_cert_info,
            cert_handler_extra_class,
            tmp_cert_file,
            tmp_key_file,
            validate_certificate,
        )

        self.cert_handler.update_cert(True)

        self.metadata = metadata
        self.only_use_keys_in_metadata = only_use_keys_in_metadata

        if not template:
            fp = str(_resource_files(_data_template).joinpath("template_enc.xml"))
            self.template = str(fp)
        else:
            self.template = template

        self.encrypt_key_type = encrypt_key_type
        self.delete_tmpfiles = delete_tmpfiles

    def correctly_signed(self, xml, must=False):
        logger.debug("verify correct signature")
        return self.correctly_signed_response(xml, must)

    def encrypt(self, text, recv_key="", template="", key_type=""):
        """
        xmlsec encrypt --pubkey-pem pub-userkey.pem
            --session-key aes128-cbc --xml-data doc-plain.xml
            --output doc-encrypted.xml session-key-template.xml

        :param text: Text to encrypt
        :param recv_key: A file containing the receivers public key
        :param template: A file containing the XMLSEC template
        :param key_type: The type of session key to use
        :result: An encrypted XML text
        """
        if not key_type:
            key_type = self.encrypt_key_type
        if not template:
            template = self.template

        return self.crypto.encrypt(text, recv_key, template, key_type)

    def encrypt_assertion(self, statement, enc_key, template, key_type="des-192", node_xpath=None):
        """
        Will encrypt an assertion

        :param statement: A XML document that contains the assertion to encrypt
        :param enc_key: File name of a file containing the encryption key
        :param template: A template for the encryption part to be added.
        :param key_type: The type of session key to use.
        :return: The encrypted text
        """
        return self.crypto.encrypt_assertion(statement, enc_key, template, key_type, node_xpath)

    def decrypt_keys(self, enctext, keys=None):
        """Decrypting an encrypted text by the use of a private key.

        :param enctext: The encrypted text as a string
        :param keys: Keys to try to decrypt enctext with
        :return: The decrypted text
        """
        key_files = []

        if not isinstance(keys, list):
            keys = [keys]

        keys_filtered = (key for key in keys if key)
        keys_encoded = (key.encode("ascii") if not isinstance(key, bytes) else key for key in keys_filtered)
        key_files = list(make_temp(key, decode=False, delete_tmpfiles=self.delete_tmpfiles) for key in keys_encoded)
        key_file_names = list(tmp.name for tmp in key_files)

        dectext = self.decrypt(enctext, key_file=key_file_names)
        return dectext

    def decrypt(self, enctext, key_file=None):
        """Decrypting an encrypted text by the use of a private key.

        :param enctext: The encrypted text as a string
        :return: The decrypted text
        """
        if not isinstance(key_file, list):
            key_file = [key_file]

        key_files = [key for key in itertools.chain(key_file, self.enc_key_files) if key]
        for key_file in key_files:
            try:
                dectext = self.crypto.decrypt(enctext, key_file)
            except XmlsecError:
                continue
            else:
                if dectext:
                    return dectext

        errmsg = "No key was able to decrypt the ciphertext. Keys tried: {keys}"
        errmsg = errmsg.format(keys=key_files)
        raise DecryptError(errmsg)

    def verify_signature(self, signedtext, cert_file=None, cert_type="pem", node_name=NODE_NAME, node_id=None):
        """Verifies the signature of a XML document.

        :param signedtext: The XML document as a string
        :param cert_file: The public key that was used to sign the document
        :param cert_type: The file type of the certificate
        :param node_name: The name of the class that is signed
        :param node_id: The identifier of the node
        :return: Boolean True if the signature was correct otherwise False.
        """
        # This is only for testing purposes, otherwise when would you receive
        # stuff that is signed with your key !?
        if not cert_file:
            cert_file = self.cert_file
            cert_type = self.cert_type

        return self.crypto.validate_signature(
            signedtext,
            cert_file=cert_file,
            cert_type=cert_type,
            node_name=node_name,
            node_id=node_id,
        )

    def _check_signature(
        self, decoded_xml, item, node_name=NODE_NAME, origdoc=None, must=False, only_valid_cert=False, issuer=None
    ):
        try:
            _issuer = item.issuer.text.strip()
        except AttributeError:
            _issuer = None

        if _issuer is None:
            try:
                _issuer = issuer.text.strip()
            except AttributeError:
                _issuer = None

        # More trust in certs from metadata then certs in the XML document
        if self.metadata:
            try:
                _certs = self.metadata.certs(_issuer, "any", "signing")
            except KeyError:
                _certs = []
            certs = []

            for cert_name, cert in _certs:
                if isinstance(cert, str):
                    content = pem_format(cert)
                    tmp = make_temp(content, suffix=".pem", decode=False, delete_tmpfiles=self.delete_tmpfiles)
                    certs.append(tmp)
                else:
                    certs.append(cert)
        else:
            certs = []

        if not certs and not self.only_use_keys_in_metadata:
            logger.debug("==== Certs from instance ====")
            certs = [
                make_temp(content=pem_format(cert), suffix=".pem", decode=False, delete_tmpfiles=self.delete_tmpfiles)
                for cert in cert_from_instance(item)
            ]
        else:
            logger.debug("==== Certs from metadata ==== %s: %s ====", _issuer, certs)

        if not certs:
            raise MissingKey(_issuer)

        try:
            validate_doc_with_schema(str(item))
        except XMLSchemaError as e:
            error_context = {
                "message": "Signature verification failed. Invalid document format.",
                "reason": str(e),
                "ID": item.id,
                "issuer": _issuer,
                "type": node_name,
                "document": decoded_xml,
            }
            raise SignatureError(error_context) from e

        # saml-core section "5.4 XML Signature Profile" defines constrains on the
        # xmldsig-core facilities. It explicitly dictates that enveloped signatures
        # are the only signatures allowed. This means that:
        # * Assertion/RequestType/ResponseType elements must have an ID attribute
        # * signatures must have a single Reference element
        # * the Reference element must have a URI attribute
        # * the URI attribute contains an anchor
        # * the anchor points to the enclosing element's ID attribute
        signed_info = item.signature.signed_info
        references = signed_info.reference
        signatures_must_have_a_single_reference_element = len(references) == 1
        the_Reference_element_must_have_a_URI_attribute = signatures_must_have_a_single_reference_element and hasattr(
            references[0], "uri"
        )
        the_URI_attribute_contains_an_anchor = (
            the_Reference_element_must_have_a_URI_attribute
            and references[0].uri.startswith("#")
            and len(references[0].uri) > 1
        )
        the_anchor_points_to_the_enclosing_element_ID_attribute = (
            the_URI_attribute_contains_an_anchor and references[0].uri == f"#{item.id}"
        )

        # SAML implementations SHOULD use Exclusive Canonicalization,
        # with or without comments
        canonicalization_method_is_c14n = signed_info.canonicalization_method.algorithm in ALLOWED_CANONICALIZATIONS

        # Signatures in SAML messages SHOULD NOT contain transforms other than the
        # - enveloped signature transform
        #   (with the identifier http://www.w3.org/2000/09/xmldsig#enveloped-signature)
        # - or the exclusive canonicalization transforms
        #   (with the identifier http://www.w3.org/2001/10/xml-exc-c14n#
        #   or http://www.w3.org/2001/10/xml-exc-c14n#WithComments).
        transform_algos = [transform.algorithm for transform in references[0].transforms.transform]
        tranform_algos_valid = ALLOWED_TRANSFORMS.intersection(transform_algos)
        transform_algos_n = len(transform_algos)
        tranform_algos_valid_n = len(tranform_algos_valid)

        the_number_of_transforms_is_one_or_two = (
            signatures_must_have_a_single_reference_element and 1 <= transform_algos_n <= 2
        )
        all_transform_algs_are_allowed = (
            the_number_of_transforms_is_one_or_two and transform_algos_n == tranform_algos_valid_n
        )
        the_enveloped_signature_transform_is_defined = (
            the_number_of_transforms_is_one_or_two and TRANSFORM_ENVELOPED in transform_algos
        )

        # The <ds:Object> element is not defined for use with SAML signatures,
        # and SHOULD NOT be present.
        # Since it can be used in service of an attacker by carrying unsigned data,
        # verifiers SHOULD reject signatures that contain a <ds:Object> element.
        object_element_is_not_present = not item.signature.object

        validators = {
            "signatures must have a single reference element": (signatures_must_have_a_single_reference_element),
            "the Reference element must have a URI attribute": (the_Reference_element_must_have_a_URI_attribute),
            "the URI attribute contains an anchor": (the_URI_attribute_contains_an_anchor),
            "the anchor points to the enclosing element ID attribute": (
                the_anchor_points_to_the_enclosing_element_ID_attribute
            ),
            "canonicalization method is c14n": canonicalization_method_is_c14n,
            "the number of transforms is one or two": (the_number_of_transforms_is_one_or_two),
            "all transform algs are allowed": all_transform_algs_are_allowed,
            "the enveloped signature transform is defined": (the_enveloped_signature_transform_is_defined),
            "object element is not present": object_element_is_not_present,
        }
        if not all(validators.values()):
            error_context = {
                "message": "Signature failed to meet constraints on xmldsig",
                "validators": validators,
                "item ID": item.id,
                "reference URI": item.signature.signed_info.reference[0].uri,
                "issuer": _issuer,
                "node name": node_name,
                "xml document": decoded_xml,
            }
            raise SignatureError(error_context)

        verified = False
        last_pem_file = None

        for pem_fd in certs:
            try:
                last_pem_file = pem_fd.name
                if self.verify_signature(
                    decoded_xml,
                    pem_fd.name,
                    node_name=node_name,
                    node_id=item.id,
                ):
                    verified = True
                    break
            except XmlsecError as exc:
                logger.error("check_sig: %s", str(exc))
            except Exception as exc:
                logger.error("check_sig: %s", str(exc))
                raise

        if verified or only_valid_cert:
            if not self.cert_handler.verify_cert(last_pem_file):
                raise CertificateError("Invalid certificate!")
        else:
            raise SignatureError("Failed to verify signature")

        return item

    def check_signature(self, item, node_name=NODE_NAME, origdoc=None, must=False, issuer=None):
        """

        :param item: Parsed entity
        :param node_name: The name of the node/class/element that is signed
        :param origdoc: The original XML string
        :param must:
        :return:
        """
        return self._check_signature(
            origdoc,
            item,
            node_name,
            origdoc,
            must=must,
            issuer=issuer,
        )

    def correctly_signed_message(self, decoded_xml, msgtype, must=False, origdoc=None, only_valid_cert=False):
        """Check if a request is correctly signed, if we have metadata for
        the entity that sent the info use that, if not use the key that are in
        the message if any.

        :param decoded_xml: The SAML message as an XML infoset (a string)
        :param msgtype: SAML protocol message type
        :param must: Whether there must be a signature
        :param origdoc:
        :return:
        """

        attr = f"{msgtype}_from_string"
        _func = getattr(saml, attr, None)
        _func = getattr(samlp, attr, _func)

        msg = _func(decoded_xml)
        if not msg:
            raise TypeError(f"Not a {msgtype}")

        if not msg.signature:
            if must:
                err_msg = "Required signature missing on {type}"
                err_msg = err_msg.format(type=msgtype)
                raise SignatureError(err_msg)
            else:
                return msg

        return self._check_signature(
            decoded_xml, msg, class_name(msg), origdoc, must=must, only_valid_cert=only_valid_cert
        )

    def correctly_signed_authn_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(
            decoded_xml, "authn_request", must, origdoc, only_valid_cert=only_valid_cert
        )

    def correctly_signed_authn_query(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, "authn_query", must, origdoc, only_valid_cert)

    def correctly_signed_logout_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, "logout_request", must, origdoc, only_valid_cert)

    def correctly_signed_logout_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, "logout_response", must, origdoc, only_valid_cert)

    def correctly_signed_attribute_query(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, "attribute_query", must, origdoc, only_valid_cert)

    def correctly_signed_authz_decision_query(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "authz_decision_query", must, origdoc, only_valid_cert)

    def correctly_signed_authz_decision_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "authz_decision_response", must, origdoc, only_valid_cert)

    def correctly_signed_name_id_mapping_request(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "name_id_mapping_request", must, origdoc, only_valid_cert)

    def correctly_signed_name_id_mapping_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "name_id_mapping_response", must, origdoc, only_valid_cert)

    def correctly_signed_artifact_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, "artifact_request", must, origdoc, only_valid_cert)

    def correctly_signed_artifact_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "artifact_response", must, origdoc, only_valid_cert)

    def correctly_signed_manage_name_id_request(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "manage_name_id_request", must, origdoc, only_valid_cert)

    def correctly_signed_manage_name_id_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "manage_name_id_response", must, origdoc, only_valid_cert)

    def correctly_signed_assertion_id_request(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "assertion_id_request", must, origdoc, only_valid_cert)

    def correctly_signed_assertion_id_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs
    ):
        return self.correctly_signed_message(decoded_xml, "assertion", must, origdoc, only_valid_cert)

    def correctly_signed_response(
        self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, require_response_signature=False, **kwargs
    ):
        """Check if a instance is correctly signed, if we have metadata for
        the IdP that sent the info use that, if not use the key that are in
        the message if any.

        :param decoded_xml: The SAML message as a XML string
        :param must: Whether there must be a signature
        :param origdoc:
        :param only_valid_cert:
        :param require_response_signature:
        :return: None if the signature can not be verified otherwise an instance
        """

        response = samlp.any_response_from_string(decoded_xml)
        if not response:
            raise TypeError("Not a Response")

        if response.signature:
            if "do_not_verify" in kwargs:
                pass
            else:
                self._check_signature(decoded_xml, response, class_name(response), origdoc)
        elif require_response_signature:
            raise SignatureError("Signature missing for response")

        return response

    def sign_statement_using_xmlsec(self, statement, **kwargs):
        """Deprecated function. See sign_statement()."""
        return self.sign_statement(statement, **kwargs)

    def sign_statement(self, statement, node_name, key=None, key_file=None, node_id=None):
        """Sign a SAML statement.

        :param statement: The statement to be signed
        :param node_name: string like 'urn:oasis:names:...:Assertion'
        :param key: The key to be used for the signing, either this or
        :param key_file: The file where the key can be found
        :param node_id:
        :return: The signed statement
        """
        if not key_file and key:
            content = str(key).encode()
            tmp = make_temp(content, suffix=".pem", delete_tmpfiles=self.delete_tmpfiles)
            key_file = tmp.name

        if not key and not key_file:
            key_file = self.key_file

        return self.crypto.sign_statement(
            statement,
            node_name,
            key_file,
            node_id,
        )

    def sign_assertion(self, statement, **kwargs):
        """Sign a SAML assertion.

        See sign_statement() for the kwargs.

        :param statement: The statement to be signed
        :return: The signed statement
        """
        return self.sign_statement(statement, class_name(saml.Assertion()), **kwargs)

    def sign_attribute_query_using_xmlsec(self, statement, **kwargs):
        """Deprecated function. See sign_attribute_query()."""
        return self.sign_attribute_query(statement, **kwargs)

    def sign_attribute_query(self, statement, **kwargs):
        """Sign a SAML attribute query.

        See sign_statement() for the kwargs.

        :param statement: The statement to be signed
        :return: The signed statement
        """
        return self.sign_statement(statement, class_name(samlp.AttributeQuery()), **kwargs)

    def multiple_signatures(self, statement, to_sign, key=None, key_file=None, sign_alg=None, digest_alg=None):
        """
        Sign multiple parts of a statement

        :param statement: The statement that should be sign, this is XML text
        :param to_sign: A list of (items, id) tuples that specifies what to sign
        :param key: A key that should be used for doing the signing
        :param key_file: A file that contains the key to be used
        :return: A possibly multiple signed statement
        """
        for (item, sid) in to_sign:
            if not sid:
                if not item.id:
                    sid = item.id = sid()
                else:
                    sid = item.id

            if not item.signature:
                item.signature = pre_signature_part(
                    ident=sid,
                    public_key=self.cert_file,
                    sign_alg=sign_alg,
                    digest_alg=digest_alg,
                )

            statement = self.sign_statement(
                statement,
                class_name(item),
                key=key,
                key_file=key_file,
                node_id=sid,
            )

        return statement


# XXX FIXME calls DefaultSignature - remove to unveil chain of calls without proper args
def pre_signature_part(
    ident,
    public_key=None,
    identifier=None,
    digest_alg=None,
    sign_alg=None,
):
    """
    If an assertion is to be signed the signature part has to be preset
    with which algorithms to be used, this function returns such a
    preset part.

    :param ident: The identifier of the assertion, so you know which assertion
        was signed
    :param public_key: The base64 part of a PEM file
    :param identifier:
    :return: A preset signature part
    """

    # XXX
    if not digest_alg:
        digest_alg = ds.DefaultSignature().get_digest_alg()
    if not sign_alg:
        sign_alg = ds.DefaultSignature().get_sign_alg()

    signature_method = ds.SignatureMethod(algorithm=sign_alg)
    canonicalization_method = ds.CanonicalizationMethod(algorithm=TRANSFORM_C14N)
    trans0 = ds.Transform(algorithm=TRANSFORM_ENVELOPED)
    trans1 = ds.Transform(algorithm=TRANSFORM_C14N)
    transforms = ds.Transforms(transform=[trans0, trans1])
    digest_method = ds.DigestMethod(algorithm=digest_alg)

    reference = ds.Reference(
        uri=f"#{ident}", digest_value=ds.DigestValue(), transforms=transforms, digest_method=digest_method
    )

    signed_info = ds.SignedInfo(
        signature_method=signature_method, canonicalization_method=canonicalization_method, reference=reference
    )

    signature = ds.Signature(signed_info=signed_info, signature_value=ds.SignatureValue())

    if identifier:
        signature.id = f"Signature{identifier}"

    # XXX remove - do not embed the cert
    if public_key:
        x509_data = ds.X509Data(x509_certificate=[ds.X509Certificate(text=public_key)])
        key_info = ds.KeyInfo(x509_data=x509_data)
        signature.key_info = key_info

    return signature


# <?xml version="1.0" encoding="UTF-8"?>
# <EncryptedData Id="ED" Type="http://www.w3.org/2001/04/xmlenc#Element"
# xmlns="http://www.w3.org/2001/04/xmlenc#">
#     <EncryptionMethod Algorithm="http://www.w3
# .org/2001/04/xmlenc#tripledes-cbc"/>
#     <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
#       <EncryptedKey Id="EK" xmlns="http://www.w3.org/2001/04/xmlenc#">
#         <EncryptionMethod Algorithm="http://www.w3
# .org/2001/04/xmlenc#rsa-1_5"/>
#         <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
#           <ds:KeyName>my-rsa-key</ds:KeyName>
#         </ds:KeyInfo>
#         <CipherData>
#           <CipherValue>
#           </CipherValue>
#         </CipherData>
#         <ReferenceList>
#           <DataReference URI="#ED"/>
#         </ReferenceList>
#       </EncryptedKey>
#     </ds:KeyInfo>
#     <CipherData>
#       <CipherValue>
#       </CipherValue>
#     </CipherData>
# </EncryptedData>


def pre_encryption_part(
    *,
    msg_enc=TRIPLE_DES_CBC,
    key_enc=RSA_OAEP_MGF1P,
    key_name=None,
    encrypted_key_id=None,
    encrypted_data_id=None,
    encrypt_cert=None,
):
    ek_id = encrypted_key_id or f"EK_{gen_random_key()}"
    ed_id = encrypted_data_id or f"ED_{gen_random_key()}"
    msg_encryption_method = EncryptionMethod(algorithm=msg_enc)
    key_encryption_method = EncryptionMethod(algorithm=key_enc)

    x509_data = ds.X509Data(x509_certificate=ds.X509Certificate(text=encrypt_cert)) if encrypt_cert else None
    key_name = ds.KeyName(text=key_name) if key_name else None
    key_info = ds.KeyInfo(key_name=key_name, x509_data=x509_data) if key_name or x509_data else None

    encrypted_key = EncryptedKey(
        id=ek_id,
        encryption_method=key_encryption_method,
        key_info=key_info,
        cipher_data=CipherData(cipher_value=CipherValue(text="")),
    )
    key_info = ds.KeyInfo(encrypted_key=encrypted_key)
    encrypted_data = EncryptedData(
        id=ed_id,
        type="http://www.w3.org/2001/04/xmlenc#Element",
        encryption_method=msg_encryption_method,
        key_info=key_info,
        cipher_data=CipherData(cipher_value=CipherValue(text="")),
    )
    return encrypted_data


def pre_encrypt_assertion(response):
    """
    Move the assertion to within a encrypted_assertion
    :param response: The response with one assertion
    :return: The response but now with the assertion within an
        encrypted_assertion.
    """
    assertion = response.assertion
    response.assertion = None
    response.encrypted_assertion = EncryptedAssertion()
    if assertion is not None:
        if isinstance(assertion, list):
            response.encrypted_assertion.add_extension_elements(assertion)
        else:
            response.encrypted_assertion.add_extension_element(assertion)
    return response


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--list-sigalgs", dest="listsigalgs", action="store_true", help="List implemented signature algorithms"
    )
    args = parser.parse_args()

    if args.listsigalgs:
        print("\n".join([key for key, value in SIGNER_ALGS.items()]))
