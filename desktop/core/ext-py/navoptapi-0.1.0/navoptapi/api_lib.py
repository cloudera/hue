
from base64 import urlsafe_b64encode
from collections import namedtuple
from collections import OrderedDict

from email.utils import formatdate

import json
import logging
import platform

from urlparse import urlsplit

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from requests import Request, Session

import six


LOG = logging.getLogger('ccscli.navopt')
ROOT_LOGGER = logging.getLogger('')
LOG_FORMAT = ('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

# Used to specify anonymous (unsigned) request signature
UNSIGNED = object()
DEFAULT_PROFILE_NAME = 'default'
ReadOnlyCredentials = namedtuple('ReadOnlyCredentials',
                                 ['access_key_id', 'private_key', 'method'])
VERSION = "0.1.0"


class Serializer(object):
    DEFAULT_ENCODING = 'utf-8'

    def serialize_to_request(self, parameters, operation_model):
        # Don't serialize any parameter with a None value.
        filtered_parameters = OrderedDict(
            (k, v) for k, v in parameters.items() if v is not None)

        serialized = {}
        # serialized['method'] = operation_model.http['method']
        # serialized['headers'] = {'Content-Type': 'application/json'}
        # serialized['url_path'] = operation_model.http['requestUri']

        serialized_body = OrderedDict()
        if len(filtered_parameters) != 0:
            self._serialize(serialized_body, filtered_parameters, None)

        serialized['body'] = json.dumps(serialized_body).encode(self.DEFAULT_ENCODING)

        return serialized

    def _serialize(self, serialized, value, shape, key=None):
        # serialize_method_name = '_serialize_type_%s' % shape.type_name
        # method = getattr(self, serialize_method_name, self._default_serialize)
        self._default_serialize(serialized, value, shape, key)

    def _serialize_type_object(self, serialized, value, shape, key):
        if key is not None:
            # If a key is provided, this is a result of a recursive call, so we
            # need to add a new child dict as the value of the passed in dict.
            # Below we will add all the structure members to the new serialized
            # dictionary we just created.
            serialized[key] = OrderedDict()
            serialized = serialized[key]

        for member_key, member_value in value.items():
            member_shape = shape.members[member_key]
            self._serialize(serialized, member_value, member_shape, member_key)

    def _serialize_type_array(self, serialized, value, shape, key):
        array_obj = []
        serialized[key] = array_obj
        for array_item in value:
            wrapper = {}
            # JSON list serialization is the only case where we aren't setting
            # a key on a dict.  We handle this by using a __current__ key on a
            # wrapper dict to serialize each list item before appending it to
            # the serialized list.
            self._serialize(wrapper, array_item, shape.member, "__current__")
            array_obj.append(wrapper["__current__"])

    def _default_serialize(self, serialized, value, shape, key):
        if key:
            serialized[key] = value
        else:
            for member_key, member_value in value.items():
                serialized[member_key] = member_value


class Credentials(object):
    """
    Holds the credentials needed to authenticate requests.
    """

    def __init__(self, access_key_id, private_key, method):
        self.access_key_id = access_key_id
        self.private_key = private_key
        self.method = method
        self._normalize()

    def ensure_unicode(self, s, encoding='utf-8', errors='strict'):
        if isinstance(s, six.text_type):
            return s
        return unicode(s, encoding, errors)

    def _normalize(self):
        self.access_key_id = self.ensure_unicode(self.access_key_id)
        self.private_key = self.ensure_unicode(self.private_key)

    def get_frozen_credentials(self):
        return ReadOnlyCredentials(self.access_key_id,
                                   self.private_key,
                                   self.method)


class RSAv1Auth(object):
    """
    RSA signing with a SHA-256 hash returning a base64 encoded signature.
    """
    AUTH_METHOD_NAME = 'rsav1'

    def __init__(self, credentials):
        self.credentials = credentials

    def sign_string(self, string_to_sign):
        try:
            # We expect the private key to be the an PKCS8 pem formatted string.
            key = RSA.importKey(self.credentials.private_key)
        except:
            message = \
                "Failed to import private key from: '%s'. The private key is " \
                "corrupted or it is not in PKCS8 PEM format. The private key " \
                "was extracted either from 'env' (environment variables), " \
                "'shared-credentials-file' (a profile in the shared " \
                "credential file, by default under ~/.ccs/credentials), or " \
                "'auth-config-file' (a file containing the credentials whose " \
                "location was supplied on the command line.)" % \
                self.credentials.method
            LOG.debug(message, exc_info=True)
            raise Exception(message)
        # We sign the hash.
        h = SHA256.new(string_to_sign.encode('utf-8'))
        signer = PKCS1_v1_5.new(key)
        return urlsafe_b64encode(signer.sign(h)).strip().decode('utf-8')

    def canonical_standard_headers(self, headers):
        interesting_headers = ['content-type', 'x-ccs-date']
        hoi = []
        if 'x-ccs-date' in headers:
            raise Exception("x-ccs-date found in headers!")
        headers['x-ccs-date'] = self._get_date()
        for ih in interesting_headers:
            found = False
            for key in headers:
                lk = key.lower()
                if headers[key] is not None and lk == ih:
                    hoi.append(headers[key].strip())
                    found = True
            if not found:
                hoi.append('')
        return '\n'.join(hoi)

    def canonical_string(self, method, split, headers):
        cs = method.upper() + '\n'
        cs += self.canonical_standard_headers(headers) + '\n'
        cs += split.path + '\n'
        cs += RSAv1Auth.AUTH_METHOD_NAME
        return cs

    def get_signature(self, method, split, headers):
        string_to_sign = self.canonical_string(method, split, headers)
        LOG.debug('StringToSign:\n%s', string_to_sign)
        return self.sign_string(string_to_sign)

    def add_auth(self, request):
        if self.credentials is None:
            return
        LOG.debug("Calculating signature using RSAv1Auth.")
        LOG.debug('HTTP request method: %s', request.method)
        split = urlsplit(request.url)
        signature = self.get_signature(request.method,
                                       split,
                                       request.headers)
        self._inject_signature(request, signature)

    def _get_date(self):
        return formatdate(usegmt=True)

    def _inject_signature(self, request, signature):
        if 'x-ccs-auth' in request.headers:
            raise Exception("x-ccs-auth found in headers!")
        request.headers['x-ccs-auth'] = self._get_signature_header(signature)

    def _get_signature_header(self, signature):
        auth_params = OrderedDict()
        auth_params['access_key_id'] = self.credentials.access_key_id
        auth_params['auth_method'] = RSAv1Auth.AUTH_METHOD_NAME
        encoded_auth_params = json.dumps(auth_params).encode('utf-8')
        return "%s.%s" % (
            urlsafe_b64encode(encoded_auth_params).strip().decode('utf-8'),
            signature)

AUTH_TYPE_MAPS = {
    RSAv1Auth.AUTH_METHOD_NAME: RSAv1Auth,
}


class RequestSigner(object):
    """
    An object to sign requests before they go out over the wire using
    one of the authentication mechanisms defined in ``auth.py``.
    """
    def __init__(self, signature_version, credentials):
        self._signature_version = signature_version
        self._credentials = credentials

    @property
    def signature_version(self):
        return self._signature_version

    def sign(self, request):
        """
        Sign a request before it goes out over the wire.
        """
        if self._signature_version != UNSIGNED:
            signer = self.get_auth_instance(self._signature_version)
            signer.add_auth(request)

    def get_auth_instance(self, signature_version, **kwargs):
        """
        Get an auth instance which can be used to sign a request
        using the given signature version.
        """
        cls = AUTH_TYPE_MAPS.get(signature_version)
        if cls is None:
            return
        # If there's no credentials provided (i.e credentials is None),
        # then we'll pass a value of "None" over to the auth classes,
        # which already handle the cases where no credentials have
        # been provided.
        frozen_credentials = self._credentials.get_frozen_credentials()
        kwargs['credentials'] = frozen_credentials
        auth = cls(**kwargs)
        return auth


class ApiLib(object):

    def __init__(self, service_name, host_name, access_key, private_key):
        # get Credentials
        self._access_key = access_key
        self._private_key = private_key
        self._endpoint_url = "http://"+host_name+":8982/"+service_name+"/"
        self._service_name = service_name
        self._cred = Credentials(access_key, private_key,
                                 method='shared-credentials-file')
        self._signer = RequestSigner(RSAv1Auth.AUTH_METHOD_NAME, self._cred)

    def _build_user_agent_header(self):
        return 'CCSCLI/%s Python/%s %s/%s' % (VERSION,
                                              platform.python_version(),
                                              platform.system(),
                                              platform.release())

    def _encode_headers(self, headers):
        # In place encoding of headers to utf-8 if they are unicode.
        for key, value in headers.items():
            if isinstance(value, six.text_type):
                # We have to do this because request.headers is not
                # normal dictionary.  It has the (unintuitive) behavior
                # of aggregating repeated setattr calls for the same
                # key value.  For example:
                # headers['foo'] = 'a'; headers['foo'] = 'b'
                # list(headers) will print ['foo', 'foo'].
                del headers[key]
                headers[key] = value.encode('utf-8')

    def call_api(self, operation_name, params):
        if not operation_name or not params:
            return

        api_session = Session()
        api_url = self._endpoint_url + operation_name
        req = Request('POST', api_url)
        prepped = req.prepare()
        self._encode_headers(prepped.headers)
        prepped.headers['Content-Type'] = 'application/json'
        prepped.headers['User-Agent'] = self._build_user_agent_header()
        self._signer.sign(prepped)
        # prepare the body
        serializer = Serializer()
        serial_obj = serializer.serialize_to_request(params, None)
        prepped.prepare_body(serial_obj['body'], None)
        print "The object:", serial_obj
        resp = api_session.send(prepped)
        return resp
