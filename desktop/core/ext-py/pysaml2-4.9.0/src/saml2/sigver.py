""" Functions connected to signing and verifying.
Based on the use of xmlsec1 binaries and not the python xmlsec module.
"""
from OpenSSL import crypto

import base64
import hashlib
import itertools
import logging
import os
import ssl
import six

from time import mktime
from binascii import hexlify

from six.moves.urllib import parse

import saml2.cryptography.asymmetric
import saml2.cryptography.pki

from tempfile import NamedTemporaryFile, mkdtemp
from subprocess import Popen
from subprocess import PIPE

from saml2 import samlp
from saml2 import SamlBase
from saml2 import SAMLError
from saml2 import extension_elements_to_elements
from saml2 import class_name
from saml2 import saml
from saml2 import ExtensionElement
from saml2 import VERSION

from saml2.cert import OpenSSLWrapper
from saml2.extension import pefim
from saml2.extension.pefim import SPCertEnc
from saml2.saml import EncryptedAssertion

import saml2.xmldsig as ds

from saml2.s_utils import sid
from saml2.s_utils import Unsupported

from saml2.time_util import instant
from saml2.time_util import utc_now
from saml2.time_util import str_to_time

from saml2.xmldsig import SIG_RSA_SHA1
from saml2.xmldsig import SIG_RSA_SHA224
from saml2.xmldsig import SIG_RSA_SHA256
from saml2.xmldsig import SIG_RSA_SHA384
from saml2.xmldsig import SIG_RSA_SHA512
from saml2.xmlenc import EncryptionMethod
from saml2.xmlenc import EncryptedKey
from saml2.xmlenc import CipherData
from saml2.xmlenc import CipherValue
from saml2.xmlenc import EncryptedData


logger = logging.getLogger(__name__)

SIG = '{{{ns}#}}{attribute}'.format(ns=ds.NAMESPACE, attribute='Signature')

RSA_1_5 = 'http://www.w3.org/2001/04/xmlenc#rsa-1_5'
TRIPLE_DES_CBC = 'http://www.w3.org/2001/04/xmlenc#tripledes-cbc'


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
    pass


class CertificateError(SigverError):
    pass


def read_file(*args, **kwargs):
    with open(*args, **kwargs) as handler:
        return handler.read()


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
        statement = statement[len(XMLTAG):]
        if statement[0] == '\n':
            statement = statement[1:]
    elif statement.startswith(PREFIX1):
        statement = statement[len(PREFIX1):]
        if statement[0] == '\n':
            statement = statement[1:]
    elif statement.startswith(PREFIX2):
        statement = statement[len(PREFIX2):]
        if statement[0] == '\n':
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
    if os.name == 'posix':
        bin_name = ['xmlsec1']
    elif os.name == 'nt':
        bin_name = ['xmlsec.exe', 'xmlsec1.exe']
    else:  # Default !?
        bin_name = ['xmlsec1']

    if paths:
        for bname in bin_name:
            for path in paths:
                fil = os.path.join(path, bname)
                try:
                    if os.lstat(fil):
                        return fil
                except OSError:
                    pass

    for path in os.environ['PATH'].split(os.pathsep):
        for bname in bin_name:
            fil = os.path.join(path, bname)
            try:
                if os.lstat(fil):
                    return fil
            except OSError:
                pass

    raise SigverError('Cannot find {binary}'.format(binary=bin_name))


def _get_xmlsec_cryptobackend(path=None, search_paths=None):
    """
    Initialize a CryptoBackendXmlSec1 crypto backend.

    This function is now internal to this module.
    """
    if path is None:
        path = get_xmlsec_binary(paths=search_paths)
    return CryptoBackendXmlSec1(path)


NODE_NAME = 'urn:oasis:names:tc:SAML:2.0:assertion:Assertion'
ENC_NODE_NAME = 'urn:oasis:names:tc:SAML:2.0:assertion:EncryptedAssertion'
ENC_KEY_CLASS = 'EncryptedKey'


def _make_vals(val, klass, seccont, klass_inst=None, prop=None, part=False,
               base64encode=False, elements_to_sign=None):
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
        cinst = _instance(klass, val, seccont, base64encode=base64encode,
                          elements_to_sign=elements_to_sign)
    else:
        try:
            cinst = klass().set_text(val)
        except ValueError:
            if not part:
                cis = [
                    _make_vals(
                        sval,
                        klass,
                        seccont,
                        klass_inst,
                        prop,
                        True,
                        base64encode,
                        elements_to_sign)
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

    if 'text' in ava:
        instance.set_text(ava['text'], base64encode)

    for prop, klassdef in instance.c_children.values():
        if prop in ava:
            if isinstance(klassdef, list):
                # means there can be a list of values
                _make_vals(ava[prop], klassdef[0], seccont, instance, prop,
                           base64encode=base64encode,
                           elements_to_sign=elements_to_sign)
            else:
                cis = _make_vals(ava[prop], klassdef, seccont, instance, prop,
                                 True, base64encode, elements_to_sign)
                setattr(instance, prop, cis)

    if 'extension_elements' in ava:
        for item in ava['extension_elements']:
            instance.extension_elements.append(
                ExtensionElement(item['tag']).loadd(item))

    if 'extension_attributes' in ava:
        for key, val in ava['extension_attributes'].items():
            instance.extension_attributes[key] = val

    if 'signature' in ava:
        elements_to_sign.append((class_name(instance), instance.id))

    return instance


def signed_instance_factory(instance, seccont, elements_to_sign=None):
    """

    :param instance: The instance to be signed or not
    :param seccont: The security context
    :param elements_to_sign: Which parts if any that should be signed
    :return: A class instance if not signed otherwise a string
    """
    if elements_to_sign:
        signed_xml = instance
        if not isinstance(instance, six.string_types):
            signed_xml = instance.to_string()
        for (node_name, nodeid) in elements_to_sign:
            signed_xml = seccont.sign_statement(
                signed_xml, node_name=node_name, node_id=nodeid)
        return signed_xml
    else:
        return instance


def make_temp(string, suffix='', decode=True, delete=True):
    """ xmlsec needs files in some cases where only strings exist, hence the
    need for this function. It creates a temporary file with the
    string as only content.

    :param string: The information to be placed in the file
    :param suffix: The temporary file might have to have a specific
        suffix in certain circumstances.
    :param decode: The input string might be base64 coded. If so it
        must, in some cases, be decoded before being placed in the file.
    :return: 2-tuple with file pointer ( so the calling function can
        close the file) and filename (which is for instance needed by the
        xmlsec function).
    """
    ntf = NamedTemporaryFile(suffix=suffix, delete=delete)
    # Python3 tempfile requires byte-like object
    if not isinstance(string, six.binary_type):
        string = string.encode('utf-8')

    if decode:
        ntf.write(base64.b64decode(string))
    else:
        ntf.write(string)
    ntf.seek(0)
    return ntf, ntf.name


def split_len(seq, length):
    return [seq[i:i + length] for i in range(0, len(seq), length)]


M2_TIME_FORMAT = '%b %d %H:%M:%S %Y'


def to_time(_time):
    assert _time.endswith(' GMT')
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
        assert cert.has_expired() == 0
        assert not OpenSSLWrapper().certificate_not_valid_yet(cert)
        return True
    except AssertionError:
        return False
    except AttributeError:
        return False


def cert_from_key_info(key_info, ignore_age=False):
    """ Get all X509 certs from a KeyInfo instance. Care is taken to make sure
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
        cert = '\n'.join(split_len(''.join([s.strip() for s in
                                            cert.split()]), 64))
        if ignore_age or active_cert(cert):
            res.append(cert)
        else:
            logger.info('Inactive cert')
    return res


def cert_from_key_info_dict(key_info, ignore_age=False):
    """ Get all X509 certs from a KeyInfo dictionary. Care is taken to make sure
    that the certs are continues sequences of bytes.

    All certificates appearing in an X509Data element MUST relate to the
    validation key by either containing it or being part of a certification
    chain that terminates in a certificate containing the validation key.

    :param key_info: The KeyInfo dictionary
    :return: A possibly empty list of certs in their text representation
    """
    res = []
    if 'x509_data' not in key_info:
        return res

    for x509_data in key_info['x509_data']:
        x509_certificate = x509_data['x509_certificate']
        cert = x509_certificate['text'].strip()
        cert = '\n'.join(split_len(''.join(
            [s.strip() for s in cert.split()]), 64))
        if ignore_age or active_cert(cert):
            res.append(cert)
        else:
            logger.info('Inactive cert')
    return res


def cert_from_instance(instance):
    """ Find certificates that are part of an instance

    :param instance: An instance
    :return: possible empty list of certificates
    """
    if instance.signature:
        if instance.signature.key_info:
            return cert_from_key_info(instance.signature.key_info,
                                      ignore_age=True)
    return []


def extract_rsa_key_from_x509_cert(pem):
    cert = saml2.cryptography.pki.load_pem_x509_certificate(pem)
    return cert.public_key()


def pem_format(key):
    return '\n'.join([
        '-----BEGIN CERTIFICATE-----',
        key,
        '-----END CERTIFICATE-----'
    ]).encode('ascii')


def import_rsa_key_from_file(filename, passphrase=None):
    data = read_file(filename, 'rb')
    passphrase = bytes(passphrase) if passphrase else None
    key = saml2.cryptography.asymmetric.load_pem_private_key(data, passphrase)
    return key


def parse_xmlsec_output(output):
    """ Parse the output from xmlsec to try to find out if the
    command was successfull or not.

    :param output: The output from Popen
    :return: A boolean; True if the command was a success otherwise False
    """
    for line in output.splitlines():
        if line == 'OK':
            return True
        elif line == 'FAIL':
            raise XmlsecError(output)
    raise XmlsecError(output)


def sha1_digest(msg):
    return hashlib.sha1(msg).digest()

class NamedPipe(object):
    def __init__(self):
        self._tempdir = mkdtemp()
        self.name = os.path.join(self._tempdir, 'fifo')

        try:
            os.mkfifo(self.name)
        except:
            os.rmdir(self._tempdir)

    def close(self):
        os.remove(self.name)
        os.rmdir(self._tempdir)

class Signer(object):
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
        return saml2.cryptography.asymmetric.key_sign(
                key or self.key, msg, self.digest)

    def verify(self, msg, sig, key=None):
        return saml2.cryptography.asymmetric.key_verify(
                key or self.key, sig, msg, self.digest)


SIGNER_ALGS = {
    SIG_RSA_SHA1: RSASigner(saml2.cryptography.asymmetric.hashes.SHA1()),
    SIG_RSA_SHA224: RSASigner(saml2.cryptography.asymmetric.hashes.SHA224()),
    SIG_RSA_SHA256: RSASigner(saml2.cryptography.asymmetric.hashes.SHA256()),
    SIG_RSA_SHA384: RSASigner(saml2.cryptography.asymmetric.hashes.SHA384()),
    SIG_RSA_SHA512: RSASigner(saml2.cryptography.asymmetric.hashes.SHA512()),
}

REQ_ORDER = [
    'SAMLRequest',
    'RelayState',
    'SigAlg',
]

RESP_ORDER = [
    'SAMLResponse',
    'RelayState',
    'SigAlg',
]


class RSACrypto(object):
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
        signer = crypto.get_signer(saml_msg['SigAlg'], sigkey)
    except KeyError:
        raise Unsupported('Signature algorithm: {alg}'.format(
            alg=saml_msg['SigAlg']))
    else:
        if saml_msg['SigAlg'] in SIGNER_ALGS:
            if 'SAMLRequest' in saml_msg:
                _order = REQ_ORDER
            elif 'SAMLResponse' in saml_msg:
                _order = RESP_ORDER
            else:
                raise Unsupported(
                    'Verifying signature on something that should not be '
                    'signed')
            _args = saml_msg.copy()
            del _args['Signature']  # everything but the signature
            string = '&'.join(
                [parse.urlencode({k: _args[k]}) for k in _order if k in
                 _args]).encode('ascii')

            if cert:
                _key = extract_rsa_key_from_x509_cert(pem_format(cert))
            else:
                _key = sigkey

            _sign = base64.b64decode(saml_msg['Signature'])

            return bool(signer.verify(string, _sign, _key))


def make_str(txt):
    if isinstance(txt, six.string_types):
        return txt
    else:
        return txt.decode()


def read_cert_from_file(cert_file, cert_type):
    """ Reads a certificate from a file. The assumption is that there is
    only one certificate in the file

    :param cert_file: The name of the file
    :param cert_type: The certificate type
    :return: A base64 encoded certificate as a string or the empty string
    """

    if not cert_file:
        return ''

    if cert_type == 'pem':
        _a = read_file(cert_file, 'rb').decode()
        _b = _a.replace('\r\n', '\n')
        lines = _b.split('\n')

        for pattern in (
                '-----BEGIN CERTIFICATE-----',
                '-----BEGIN PUBLIC KEY-----'):
            if pattern in lines:
                lines = lines[lines.index(pattern) + 1:]
                break
        else:
            raise CertificateError('Strange beginning of PEM file')

        for pattern in (
                '-----END CERTIFICATE-----',
                '-----END PUBLIC KEY-----'):
            if pattern in lines:
                lines = lines[:lines.index(pattern)]
                break
        else:
            raise CertificateError('Strange end of PEM file')
        return make_str(''.join(lines).encode())

    if cert_type in ['der', 'cer', 'crt']:
        data = read_file(cert_file, 'rb')
        _cert = base64.b64encode(data)
        return make_str(_cert)


class CryptoBackend(object):
    def version(self):
        raise NotImplementedError()

    def encrypt(self, text, recv_key, template, key_type):
        raise NotImplementedError()

    def encrypt_assertion(self, statement, enc_key, template, key_type, node_xpath):
        raise NotImplementedError()

    def decrypt(self, enctext, key_file, id_attr, passphrase=None):
        raise NotImplementedError()

    def sign_statement(self, statement, node_name, key_file, node_id, id_attr, passphrase=None):
        raise NotImplementedError()

    def validate_signature(self, enctext, cert_file, cert_type, node_name, node_id, id_attr):
        raise NotImplementedError()


ASSERT_XPATH = ''.join([
    '/*[local-name()=\'{name}\']'.format(name=n)
    for n in ['Response', 'EncryptedAssertion', 'Assertion']
])


class CryptoBackendXmlSec1(CryptoBackend):
    """
    CryptoBackend implementation using external binary 1 to sign
    and verify XML documents.
    """

    __DEBUG = 0

    def __init__(self, xmlsec_binary, **kwargs):
        CryptoBackend.__init__(self, **kwargs)
        assert (isinstance(xmlsec_binary, six.string_types))
        self.xmlsec = xmlsec_binary
        self._xmlsec_delete_tmpfiles = os.environ.get(
            'PYSAML2_KEEP_XMLSEC_TMP', False
        )

        try:
            self.non_xml_crypto = RSACrypto(kwargs['rsa_key'])
        except KeyError:
            pass

    def version(self):
        com_list = [self.xmlsec, '--version']
        pof = Popen(com_list, stderr=PIPE, stdout=PIPE)
        content, _ = pof.communicate()
        content = content.decode('ascii')
        try:
            return content.split(' ')[1]
        except IndexError:
            return ''

    def encrypt(self, text, recv_key, template, session_key_type, xpath=''):
        """

        :param text: The text to be compiled
        :param recv_key: Filename of a file where the key resides
        :param template: Filename of a file with the pre-encryption part
        :param session_key_type: Type and size of a new session key
            'des-192' generates a new 192 bits DES key for DES3 encryption
        :param xpath: What should be encrypted
        :return:
        """
        logger.debug('Encryption input len: %d', len(text))
        _, fil = make_temp(text, decode=False)

        com_list = [
            self.xmlsec,
            '--encrypt',
            '--pubkey-cert-pem', recv_key,
            '--session-key', session_key_type,
            '--xml-data', fil,
        ]

        if xpath:
            com_list.extend(['--node-xpath', xpath])

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [template])
        except XmlsecError as e:
            six.raise_from(EncryptError(com_list), e)

        return output

    def encrypt_assertion(self, statement, enc_key, template, key_type='des-192', node_xpath=None, node_id=None):
        """
        Will encrypt an assertion

        :param statement: A XML document that contains the assertion to encrypt
        :param enc_key: File name of a file containing the encryption key
        :param template: A template for the encryption part to be added.
        :param key_type: The type of session key to use.
        :return: The encrypted text
        """
        if six.PY2:
            _str = unicode
        else:
            _str = str

        if isinstance(statement, SamlBase):
            statement = pre_encrypt_assertion(statement)

        _, fil = make_temp(
            _str(statement), decode=False, delete=self._xmlsec_delete_tmpfiles
        )
        _, tmpl = make_temp(_str(template), decode=False)

        if not node_xpath:
            node_xpath = ASSERT_XPATH

        com_list = [
            self.xmlsec,
            '--encrypt',
            '--pubkey-cert-pem', enc_key,
            '--session-key', key_type,
            '--xml-data', fil,
            '--node-xpath', node_xpath,
        ]

        if node_id:
            com_list.extend(['--node-id', node_id])

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [tmpl])
        except XmlsecError as e:
            six.raise_from(EncryptError(com_list), e)

        return output.decode('utf-8')

    def decrypt(self, enctext, key_file, id_attr, passphrase=None):
        """

        :param enctext: XML document containing an encrypted part
        :param key_file: The key to use for the decryption
        :return: The decrypted document
        """

        logger.debug('Decrypt input len: %d', len(enctext))
        _, fil = make_temp(enctext, decode=False)

        com_list = [
            self.xmlsec,
            '--decrypt',
            '--id-attr:{id_attr}'.format(id_attr=id_attr),
            ENC_KEY_CLASS,
        ]

        try:
            (_stdout, _stderr, output) = self._run_xmlsec(com_list, [fil],
                                                          key_file=key_file,
                                                          passphrase=passphrase)
        except XmlsecError as e:
            six.raise_from(DecryptError(com_list), e)

        return output.decode('utf-8')

    def sign_statement(self, statement, node_name, key_file, node_id, id_attr, passphrase=None):
        """
        Sign an XML statement.

        :param statement: The statement to be signed
        :param node_name: string like 'urn:oasis:names:...:Assertion'
        :param key_file: The file where the key can be found
        :param node_id:
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :return: The signed statement
        """
        if isinstance(statement, SamlBase):
            statement = str(statement)

        _, fil = make_temp(
            "%s" % statement,
            suffix='.xml',
            decode=False,
            delete=self._xmlsec_delete_tmpfiles,
        )

        com_list = [
            self.xmlsec,
            '--sign',
            '--id-attr:{id_attr_name}'.format(id_attr_name=id_attr),
            node_name,
        ]

        if node_id:
            com_list.extend(['--node-id', node_id])

        try:
            (stdout, stderr, output) = self._run_xmlsec(com_list, [fil],
                                                        key_file=key_file,
                                                        passphrase=passphrase)
        except XmlsecError as e:
            raise SignatureError(com_list)

        # this does not work if --store-signatures is used
        if output:
            return output.decode("utf-8")
        if stdout:
            return stdout.decode("utf-8")
        raise SignatureError(stderr)

    def validate_signature(self, signedtext, cert_file, cert_type, node_name, node_id, id_attr):
        """
        Validate signature on XML document.

        :param signedtext: The XML document as a string
        :param cert_file: The public key that was used to sign the document
        :param cert_type: The file type of the certificate
        :param node_name: The name of the class that is signed
        :param node_id: The identifier of the node
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :return: Boolean True if the signature was correct otherwise False.
        """
        if not isinstance(signedtext, six.binary_type):
            signedtext = signedtext.encode('utf-8')

        _, fil = make_temp(
            signedtext,
            suffix='.xml',
            decode=False,
            delete=self._xmlsec_delete_tmpfiles,
        )

        com_list = [
            self.xmlsec,
            '--verify',
            '--enabled-reference-uris', 'empty,same-doc',
            '--pubkey-cert-{type}'.format(type=cert_type), cert_file,
            '--id-attr:{id_attr_name}'.format(id_attr_name=id_attr),
            node_name,
        ]

        if node_id:
            com_list.extend(['--node-id', node_id])

        try:
            (_stdout, stderr, _output) = self._run_xmlsec(com_list, [fil])
        except XmlsecError as e:
            six.raise_from(SignatureError(com_list), e)

        return parse_xmlsec_output(stderr)

    def _run_xmlsec(self, com_list, extra_args, key_file=None, passphrase=None):
        """
        Common code to invoke xmlsec and parse the output.
        :param com_list: Key-value parameter list for xmlsec
        :param extra_args: Positional parameters to be appended after all
            key-value parameters
        :result: Whatever xmlsec wrote to an --output temporary file
        """
        with NamedTemporaryFile(suffix='.xml', delete=self._xmlsec_delete_tmpfiles) as ntf:
            com_list.extend(['--output', ntf.name])

            # Unfortunately there's no safe way to pass a password to xmlsec1.
            # Instead, we'll decrypt the certificate and write it into a named pipe,
            # which we'll pass to xmlsec1.
            named_pipe = None
            if key_file is not None:
                if passphrase is not None:
                    named_pipe = NamedPipe()

                    # Decrypt the certificate, but don't write it into the FIFO
                    # until after we've started xmlsec1.
                    key_content = ''
                    with open(key_file, 'r') as f:
                        key_content = f.read()
                    key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_content, passphrase=str(passphrase))

                    key_file = named_pipe.name

                com_list.extend(["--privkey-pem", key_file])

            com_list += extra_args

            logger.debug('xmlsec command: %s', ' '.join(com_list))

            pof = Popen(com_list, stderr=PIPE, stdout=PIPE)

            if named_pipe is not None:
                # Finally, write the key into our named pipe.
                try:
                    with open(named_pipe.name, 'wb') as f:
                        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
                finally:
                    named_pipe.close()

            p_out, p_err = pof.communicate()
            p_out = p_out.decode()
            p_err = p_err.decode()

            if pof.returncode != 0:
                errmsg = "returncode={code}\nerror={err}\noutput={out}".format(
                    code=pof.returncode, err=p_err, out=p_out
                )
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

    def version(self):
        # XXX if XMLSecurity.__init__ included a __version__, that would be
        # better than static 0.0 here.
        return 'XMLSecurity 0.0'

    def sign_statement(self, statement, node_name, key_file, node_id, id_attr, passphrase=None):
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
        import xmlsec
        import lxml.etree

        assert passphrase is None, "Encrypted key files is not supported"

        xml = xmlsec.parse_xml(statement)
        signed = xmlsec.sign(xml, key_file)
        signed_str = lxml.etree.tostring(signed, xml_declaration=False, encoding="UTF-8")
        if not isinstance(signed_str, six.string_types):
            signed_str = signed_str.decode("utf-8")
        return signed_str

    def validate_signature(self, signedtext, cert_file, cert_type, node_name, node_id, id_attr):
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
        if cert_type != 'pem':
            raise Unsupported('Only PEM certs supported here')

        import xmlsec
        xml = xmlsec.parse_xml(signedtext)

        try:
            return xmlsec.verify(xml, cert_file)
        except xmlsec.XMLSigException:
            return False


def security_context(conf):
    """ Creates a security context based on the configuration

    :param conf: The configuration, this is a Config instance
    :return: A SecurityContext instance
    """
    if not conf:
        return None

    try:
        metadata = conf.metadata
    except AttributeError:
        metadata = None

    try:
        id_attr = conf.id_attr_name
    except AttributeError:
        id_attr = None

    sec_backend = None

    if conf.crypto_backend == 'xmlsec1':
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
            err_msg = 'xmlsec binary not found: {binary}'
            err_msg = err_msg.format(binary=xmlsec_binary)
            raise SigverError(err_msg)

        crypto = _get_xmlsec_cryptobackend(xmlsec_binary)

        _file_name = conf.getattr('key_file', '')
        if _file_name:
            try:
                rsa_key = import_rsa_key_from_file(_file_name, passphrase=conf.key_file_passphrase)
            except Exception as err:
                logger.error('Cannot import key from {file}: {err_msg}'.format(
                    file=_file_name, err_msg=err))
                raise
            else:
                sec_backend = RSACrypto(rsa_key)
    elif conf.crypto_backend == 'XMLSecurity':
        # new and somewhat untested pyXMLSecurity crypto backend.
        crypto = CryptoBackendXMLSecurity()
    else:
        err_msg = 'Unknown crypto_backend {backend}'
        err_msg = err_msg.format(backend=conf.crypto_backend)
        raise SigverError(err_msg)

    enc_key_files = []
    if conf.encryption_keypairs is not None:
        for _encryption_keypair in conf.encryption_keypairs:
            if 'key_file' in _encryption_keypair:
                enc_key_files.append(_encryption_keypair['key_file'])

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
            key_file_passphrase=conf.key_file_passphrase,
            enc_key_files=enc_key_files,
            encryption_keypairs=conf.encryption_keypairs,
            sec_backend=sec_backend,
            id_attr=id_attr)


def encrypt_cert_from_item(item):
    _encrypt_cert = None
    try:
        try:
            _elem = extension_elements_to_elements(
                item.extensions.extension_elements, [pefim, ds])
        except:
            _elem = extension_elements_to_elements(
                item.extension_elements[0].children,
                [pefim, ds])

        for _tmp_elem in _elem:
            if isinstance(_tmp_elem, SPCertEnc):
                for _tmp_key_info in _tmp_elem.key_info:
                    if _tmp_key_info.x509_data is not None and len(
                            _tmp_key_info.x509_data) > 0:
                        _encrypt_cert = _tmp_key_info.x509_data[
                            0].x509_certificate.text
                        break
    except Exception as _exception:
        pass

    if _encrypt_cert is not None:
        if _encrypt_cert.find('-----BEGIN CERTIFICATE-----\n') == -1:
            _encrypt_cert = '-----BEGIN CERTIFICATE-----\n' + _encrypt_cert
        if _encrypt_cert.find('\n-----END CERTIFICATE-----') == -1:
            _encrypt_cert = _encrypt_cert + '\n-----END CERTIFICATE-----'
    return _encrypt_cert


class CertHandlerExtra(object):
    def __init__(self):
        pass

    def use_generate_cert_func(self):
        raise Exception('use_generate_cert_func function must be implemented')

    def generate_cert(self, generate_cert_info, root_cert_string,
                      root_key_string):
        raise Exception('generate_cert function must be implemented')
        # Excepts to return (cert_string, key_string)

    def use_validate_cert_func(self):
        raise Exception('use_validate_cert_func function must be implemented')

    def validate_cert(self, cert_str, root_cert_string, root_key_string):
        raise Exception('validate_cert function must be implemented')
        # Excepts to return True/False


class CertHandler(object):
    def __init__(
            self,
            security_context,
            cert_file=None, cert_type='pem',
            key_file=None, key_type='pem',
            generate_cert_info=None,
            cert_handler_extra_class=None,
            tmp_cert_file=None,
            tmp_key_file=None,
            verify_cert=False):
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
        if cert_type == 'pem' and key_type == 'pem':
            self._verify_cert = verify_cert is True
            self._security_context = security_context
            self._osw = OpenSSLWrapper()
            if key_file and os.path.isfile(key_file):
                self._key_str = self._osw.read_str_from_file(key_file, key_type)
            else:
                self._key_str = ''
            if cert_file and os.path.isfile(cert_file):
                self._cert_str = self._osw.read_str_from_file(cert_file,
                                                              cert_type)
            else:
                self._cert_str = ''

            self._tmp_cert_str = self._cert_str
            self._tmp_key_str = self._key_str
            self._tmp_cert_file = tmp_cert_file
            self._tmp_key_file = tmp_key_file

            self._cert_info = None
            self._generate_cert_func_active = False
            if generate_cert_info is not None \
                    and len(self._cert_str) > 0 \
                    and len(self._key_str) > 0 \
                    and tmp_key_file is not None \
                    and tmp_cert_file is not None:
                self._generate_cert = True
                self._cert_info = generate_cert_info
                self._cert_handler_extra_class = cert_handler_extra_class

    def verify_cert(self, cert_file):
        if self._verify_cert:
            if cert_file and os.path.isfile(cert_file):
                cert_str = self._osw.read_str_from_file(cert_file, 'pem')
            else:
                return False
            self._last_validated_cert = cert_str
            if self._cert_handler_extra_class is not None and \
                    self._cert_handler_extra_class.use_validate_cert_func():
                self._cert_handler_extra_class.validate_cert(
                    cert_str, self._cert_str, self._key_str)
            else:
                valid, mess = self._osw.verify(self._cert_str, cert_str)
                logger.info('CertHandler.verify_cert: %s', mess)
                return valid
        return True

    def generate_cert(self):
        return self._generate_cert

    def update_cert(self, active=False, client_crt=None):
        if (self._generate_cert and active) or client_crt is not None:
            if client_crt is not None:
                self._tmp_cert_str = client_crt
                # No private key for signing
                self._tmp_key_str = ''
            elif self._cert_handler_extra_class is not None and \
                    self._cert_handler_extra_class.use_generate_cert_func():
                (self._tmp_cert_str, self._tmp_key_str) = \
                    self._cert_handler_extra_class.generate_cert(
                        self._cert_info, self._cert_str, self._key_str)
            else:
                self._tmp_cert_str, self._tmp_key_str = self._osw \
                    .create_certificate(self._cert_info, request=True)
                self._tmp_cert_str = self._osw.create_cert_signed_certificate(
                    self._cert_str, self._key_str, self._tmp_cert_str)
                valid, mess = self._osw.verify(self._cert_str,
                                               self._tmp_cert_str)
            self._osw.write_str_to_file(self._tmp_cert_file, self._tmp_cert_str)
            self._osw.write_str_to_file(self._tmp_key_file, self._tmp_key_str)
            self._security_context.key_file = self._tmp_key_file
            self._security_context.cert_file = self._tmp_cert_file
            self._security_context.key_type = 'pem'
            self._security_context.cert_type = 'pem'
            self._security_context.my_cert = read_cert_from_file(
                self._security_context.cert_file,
                self._security_context.cert_type)


# How to get a rsa pub key fingerprint from a certificate
# openssl x509 -inform pem -noout -in server.crt -pubkey > publickey.pem
# openssl rsa -inform pem -noout -in publickey.pem -pubin -modulus
class SecurityContext(object):
    DEFAULT_ID_ATTR_NAME = 'ID'
    my_cert = None

    def __init__(
            self,
            crypto,
            key_file='', key_type='pem',
            cert_file='', cert_type='pem',
            metadata=None,
            template='',
            encrypt_key_type='des-192',
            only_use_keys_in_metadata=False,
            cert_handler_extra_class=None,
            generate_cert_info=None,
            tmp_cert_file=None, tmp_key_file=None,
            validate_certificate=None,
            key_file_passphrase=None,
            enc_key_files=None, enc_key_type='pem',
            encryption_keypairs=None,
            enc_cert_type='pem',
            sec_backend=None,
            id_attr=''):

        self.id_attr = id_attr or SecurityContext.DEFAULT_ID_ATTR_NAME

        self.crypto = crypto
        assert (isinstance(self.crypto, CryptoBackend))

        if sec_backend:
            assert (isinstance(sec_backend, RSACrypto))
        self.sec_backend = sec_backend

        # Your private key for signing
        self.key_file = key_file
        self.key_file_passphrase = key_file_passphrase
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
                cert_file, cert_type,
                key_file, key_type,
                generate_cert_info,
                cert_handler_extra_class,
                tmp_cert_file,
                tmp_key_file,
                validate_certificate)

        self.cert_handler.update_cert(True)

        self.metadata = metadata
        self.only_use_keys_in_metadata = only_use_keys_in_metadata

        if not template:
            this_dir, this_filename = os.path.split(__file__)
            self.template = os.path.join(this_dir, 'xml_template', 'template.xml')
        else:
            self.template = template

        self.encrypt_key_type = encrypt_key_type
        # keep certificate files to debug xmlsec invocations
        if os.environ.get('PYSAML2_KEEP_XMLSEC_TMP', None):
            self._xmlsec_delete_tmpfiles = False
        else:
            self._xmlsec_delete_tmpfiles = True

    def correctly_signed(self, xml, must=False):
        logger.debug('verify correct signature')
        return self.correctly_signed_response(xml, must)

    def encrypt(self, text, recv_key='', template='', key_type=''):
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

    def encrypt_assertion(self, statement, enc_key, template, key_type='des-192', node_xpath=None):
        """
        Will encrypt an assertion

        :param statement: A XML document that contains the assertion to encrypt
        :param enc_key: File name of a file containing the encryption key
        :param template: A template for the encryption part to be added.
        :param key_type: The type of session key to use.
        :return: The encrypted text
        """
        return self.crypto.encrypt_assertion(
                statement, enc_key, template, key_type, node_xpath)

    def decrypt_keys(self, enctext, keys=None, id_attr=''):
        """ Decrypting an encrypted text by the use of a private key.

        :param enctext: The encrypted text as a string
        :param keys: Keys to try to decrypt enctext with
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :return: The decrypted text
        """
        key_files = []
        passphrase = self.key_file_passphrase

        if not isinstance(keys, list):
            keys = [keys]

        keys = [key for key in keys if key]
        for key in keys:
            if not isinstance(key, six.binary_type):
                key = key.encode("ascii")
            _, key_file = make_temp(key, decode=False, delete=False)
            key_files.append(key_file)

        try:
            dectext = self.decrypt(enctext, key_file=key_files, id_attr=id_attr, passphrase=passphrase)
        except DecryptError as e:
            raise
        else:
            return dectext
        finally:
            for key_file in key_files:
                os.unlink(key_file)

    def decrypt(self, enctext, key_file=None, id_attr='', passphrase=None):
        """ Decrypting an encrypted text by the use of a private key.

        :param enctext: The encrypted text as a string
        :return: The decrypted text
        """
        if key_file is None or len(key_file) == 0:
            key_file = self.key_file
        if passphrase is None:
            passphrase = self.key_file_passphrase

        if not id_attr:
            id_attr = self.id_attr

        if not isinstance(key_file, list):
            key_file = [key_file]

        key_files = [
            key for key in itertools.chain(key_file, self.enc_key_files) if key
        ]
        for key_file in key_files:
            try:
                dectext = self.crypto.decrypt(enctext, key_file, id_attr, passphrase=passphrase)
            except XmlsecError as e:
                continue
            else:
                if dectext:
                    return dectext

        errmsg = "No key was able to decrypt the ciphertext. Keys tried: {keys}"
        errmsg = errmsg.format(keys=key_files)
        raise DecryptError(errmsg)

    def verify_signature(self, signedtext, cert_file=None, cert_type='pem', node_name=NODE_NAME, node_id=None, id_attr=''):
        """ Verifies the signature of a XML document.

        :param signedtext: The XML document as a string
        :param cert_file: The public key that was used to sign the document
        :param cert_type: The file type of the certificate
        :param node_name: The name of the class that is signed
        :param node_id: The identifier of the node
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :return: Boolean True if the signature was correct otherwise False.
        """
        # This is only for testing purposes, otherwise when would you receive
        # stuff that is signed with your key !?
        if not cert_file:
            cert_file = self.cert_file
            cert_type = self.cert_type

        if not id_attr:
            id_attr = self.id_attr

        return self.crypto.validate_signature(
                signedtext,
                cert_file=cert_file,
                cert_type=cert_type,
                node_name=node_name,
                node_id=node_id,
                id_attr=id_attr)

    def _check_signature(self, decoded_xml, item, node_name=NODE_NAME, origdoc=None, id_attr='', must=False, only_valid_cert=False, issuer=None):
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
                _certs = self.metadata.certs(_issuer, 'any', 'signing')
            except KeyError:
                _certs = []
            certs = []

            for cert in _certs:
                if isinstance(cert, six.string_types):
                    certs.append(
                        make_temp(
                            pem_format(cert),
                            suffix='.pem',
                            decode=False,
                            delete=self._xmlsec_delete_tmpfiles,
                        )
                    )
                else:
                    certs.append(cert)
        else:
            certs = []

        if not certs and not self.only_use_keys_in_metadata:
            logger.debug('==== Certs from instance ====')
            certs = [
                make_temp(
                    pem_format(cert),
                    suffix='.pem',
                    decode=False,
                    delete=self._xmlsec_delete_tmpfiles,
                )
                for cert in cert_from_instance(item)
            ]
        else:
            logger.debug('==== Certs from metadata ==== %s: %s ====', _issuer, certs)

        if not certs:
            raise MissingKey(_issuer)

        verified = False
        last_pem_file = None

        for _, pem_file in certs:
            try:
                last_pem_file = pem_file

                if origdoc is not None:
                    try:
                        if self.verify_signature(origdoc, pem_file,
                                                 node_name=node_name,
                                                 node_id=item.id,
                                                 id_attr=id_attr):
                            verified = True
                            break
                    except Exception:
                        if self.verify_signature(decoded_xml, pem_file,
                                                 node_name=node_name,
                                                 node_id=item.id,
                                                 id_attr=id_attr):
                            verified = True
                            break
                else:
                    if self.verify_signature(decoded_xml, pem_file,
                                             node_name=node_name,
                                             node_id=item.id, id_attr=id_attr):
                        verified = True
                        break
            except XmlsecError as exc:
                logger.error('check_sig: %s', exc)
                pass
            except Exception as exc:
                logger.error('check_sig: %s', exc)
                raise

        if verified or only_valid_cert:
            if not self.cert_handler.verify_cert(last_pem_file):
                raise CertificateError('Invalid certificate!')
        else:
            raise SignatureError('Failed to verify signature')

        return item

    def check_signature(self, item, node_name=NODE_NAME, origdoc=None, id_attr='', must=False, issuer=None):
        """

        :param item: Parsed entity
        :param node_name: The name of the node/class/element that is signed
        :param origdoc: The original XML string
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :param must:
        :return:
        """
        return self._check_signature(
                origdoc,
                item,
                node_name,
                origdoc,
                id_attr=id_attr,
                must=must,
                issuer=issuer)

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

        attr = '{type}_from_string'.format(type=msgtype)
        _func = getattr(saml, attr, None)
        _func = getattr(samlp, attr, _func)

        msg = _func(decoded_xml)
        if not msg:
            raise TypeError('Not a {type}'.format(type=msgtype))

        if not msg.signature:
            if must:
                err_msg = 'Required signature missing on {type}'
                err_msg = err_msg.format(type=msgtype)
                raise SignatureError(err_msg)
            else:
                return msg

        return self._check_signature(
                decoded_xml,
                msg,
                class_name(msg),
                origdoc,
                must=must,
                only_valid_cert=only_valid_cert)

    def correctly_signed_authn_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'authn_request', must, origdoc, only_valid_cert=only_valid_cert)

    def correctly_signed_authn_query(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'authn_query', must, origdoc, only_valid_cert)

    def correctly_signed_logout_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'logout_request', must, origdoc, only_valid_cert)

    def correctly_signed_logout_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'logout_response', must, origdoc, only_valid_cert)

    def correctly_signed_attribute_query(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'attribute_query', must, origdoc, only_valid_cert)

    def correctly_signed_authz_decision_query(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'authz_decision_query', must, origdoc, only_valid_cert)

    def correctly_signed_authz_decision_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'authz_decision_response', must, origdoc, only_valid_cert)

    def correctly_signed_name_id_mapping_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'name_id_mapping_request', must, origdoc, only_valid_cert)

    def correctly_signed_name_id_mapping_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'name_id_mapping_response', must, origdoc, only_valid_cert)

    def correctly_signed_artifact_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'artifact_request', must, origdoc, only_valid_cert)

    def correctly_signed_artifact_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'artifact_response', must, origdoc, only_valid_cert)

    def correctly_signed_manage_name_id_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'manage_name_id_request', must, origdoc, only_valid_cert)

    def correctly_signed_manage_name_id_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'manage_name_id_response', must, origdoc, only_valid_cert)

    def correctly_signed_assertion_id_request(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'assertion_id_request', must, origdoc, only_valid_cert)

    def correctly_signed_assertion_id_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, **kwargs):
        return self.correctly_signed_message(decoded_xml, 'assertion', must, origdoc, only_valid_cert)

    def correctly_signed_response(self, decoded_xml, must=False, origdoc=None, only_valid_cert=False, require_response_signature=False, **kwargs):
        """ Check if a instance is correctly signed, if we have metadata for
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
            raise TypeError('Not a Response')

        if response.signature:
            if 'do_not_verify' in kwargs:
                pass
            else:
                self._check_signature(decoded_xml, response,
                                      class_name(response), origdoc)
        elif require_response_signature:
            raise SignatureError('Signature missing for response')

        return response

    def sign_statement_using_xmlsec(self, statement, **kwargs):
        """ Deprecated function. See sign_statement(). """
        return self.sign_statement(statement, **kwargs)

    def sign_statement(self, statement, node_name, key=None, key_file=None, node_id=None, id_attr='', passphrase=None):
        """Sign a SAML statement.

        :param statement: The statement to be signed
        :param node_name: string like 'urn:oasis:names:...:Assertion'
        :param key: The key to be used for the signing, either this or
        :param key_file: The file where the key can be found
        :param node_id:
        :param id_attr: The attribute name for the identifier, normally one of
            'id','Id' or 'ID'
        :return: The signed statement
        """
        if not id_attr:
            id_attr = self.id_attr

        if not key_file and key:
            _, key_file = make_temp(str(key).encode(), '.pem')

        if not key and not key_file:
            key_file = self.key_file

        if not passphrase:
            passphrase = self.key_file_passphrase

        return self.crypto.sign_statement(
                statement,
                node_name,
                key_file,
                node_id,
                id_attr, passphrase=passphrase)

    def sign_assertion_using_xmlsec(self, statement, **kwargs):
        """ Deprecated function. See sign_assertion(). """
        return self.sign_statement(
                statement, class_name(saml.Assertion()), **kwargs)

    def sign_assertion(self, statement, **kwargs):
        """Sign a SAML assertion.

        See sign_statement() for the kwargs.

        :param statement: The statement to be signed
        :return: The signed statement
        """
        return self.sign_statement(
                statement, class_name(saml.Assertion()), **kwargs)

    def sign_attribute_query_using_xmlsec(self, statement, **kwargs):
        """ Deprecated function. See sign_attribute_query(). """
        return self.sign_attribute_query(statement, **kwargs)

    def sign_attribute_query(self, statement, **kwargs):
        """Sign a SAML attribute query.

        See sign_statement() for the kwargs.

        :param statement: The statement to be signed
        :return: The signed statement
        """
        return self.sign_statement(
                statement, class_name(samlp.AttributeQuery()), **kwargs)

    def multiple_signatures(self, statement, to_sign, key=None, key_file=None, sign_alg=None, digest_alg=None, passphrase=None):
        """
        Sign multiple parts of a statement

        :param statement: The statement that should be sign, this is XML text
        :param to_sign: A list of (items, id, id attribute name) tuples that
            specifies what to sign
        :param key: A key that should be used for doing the signing
        :param key_file: A file that contains the key to be used
        :return: A possibly multiple signed statement
        """
        for (item, sid, id_attr) in to_sign:
            if not sid:
                if not item.id:
                    sid = item.id = sid()
                else:
                    sid = item.id

            if not item.signature:
                item.signature = pre_signature_part(
                        sid,
                        self.cert_file,
                        sign_alg=sign_alg,
                        digest_alg=digest_alg)

            statement = self.sign_statement(
                    statement,
                    class_name(item),
                    key=key,
                    key_file=key_file,
                    node_id=sid,
                    id_attr=id_attr, passphrase=passphrase)

        return statement


def pre_signature_part(ident, public_key=None, identifier=None, digest_alg=None, sign_alg=None):
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

    if not digest_alg:
        digest_alg = ds.DefaultSignature().get_digest_alg()
    if not sign_alg:
        sign_alg = ds.DefaultSignature().get_sign_alg()
    signature_method = ds.SignatureMethod(algorithm=sign_alg)
    canonicalization_method = ds.CanonicalizationMethod(
        algorithm=ds.ALG_EXC_C14N)
    trans0 = ds.Transform(algorithm=ds.TRANSFORM_ENVELOPED)
    trans1 = ds.Transform(algorithm=ds.ALG_EXC_C14N)
    transforms = ds.Transforms(transform=[trans0, trans1])
    digest_method = ds.DigestMethod(algorithm=digest_alg)

    reference = ds.Reference(
            uri='#{id}'.format(id=ident),
            digest_value=ds.DigestValue(),
            transforms=transforms,
            digest_method=digest_method)

    signed_info = ds.SignedInfo(
            signature_method=signature_method,
            canonicalization_method=canonicalization_method,
            reference=reference)

    signature = ds.Signature(
            signed_info=signed_info,
            signature_value=ds.SignatureValue())

    if identifier:
        signature.id = 'Signature{n}'.format(n=identifier)

    if public_key:
        x509_data = ds.X509Data(
            x509_certificate=[ds.X509Certificate(text=public_key)])
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


def pre_encryption_part(msg_enc=TRIPLE_DES_CBC, key_enc=RSA_1_5, key_name='my-rsa-key'):
    """

    :param msg_enc:
    :param key_enc:
    :param key_name:
    :return:
    """
    msg_encryption_method = EncryptionMethod(algorithm=msg_enc)
    key_encryption_method = EncryptionMethod(algorithm=key_enc)
    encrypted_key = EncryptedKey(
            id='EK',
            encryption_method=key_encryption_method,
            key_info=ds.KeyInfo(
                key_name=ds.KeyName(text=key_name)),
            cipher_data=CipherData(
                cipher_value=CipherValue(text='')))
    key_info = ds.KeyInfo(encrypted_key=encrypted_key)
    encrypted_data = EncryptedData(
        id='ED',
        type='http://www.w3.org/2001/04/xmlenc#Element',
        encryption_method=msg_encryption_method,
        key_info=key_info,
        cipher_data=CipherData(cipher_value=CipherValue(text='')))
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


def response_factory(sign=False, encrypt=False, sign_alg=None, digest_alg=None,
                     **kwargs):
    response = samlp.Response(id=sid(), version=VERSION,
                              issue_instant=instant())

    if sign:
        response.signature = pre_signature_part(
            kwargs['id'], sign_alg=sign_alg, digest_alg=digest_alg)
    if encrypt:
        pass

    for key, val in kwargs.items():
        setattr(response, key, val)

    return response


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--list-sigalgs', dest='listsigalgs',
            action='store_true',
            help='List implemented signature algorithms')
    args = parser.parse_args()

    if args.listsigalgs:
        print('\n'.join([key for key, value in SIGNER_ALGS.items()]))
