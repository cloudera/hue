import calendar
import six
from six.moves import http_cookiejar
import copy
import re
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urlencode
import requests
import time
from six.moves.http_cookies import SimpleCookie
from saml2.time_util import utc_now
from saml2 import class_name, SAMLError
from saml2.pack import http_form_post_message
from saml2.pack import http_post_message
from saml2.pack import make_soap_enveloped_saml_thingy
from saml2.pack import http_redirect_message

import logging

logger = logging.getLogger(__name__)

if requests.__version__ < "2.0.0":
    DICT_HEADERS = False
else:
    DICT_HEADERS = True

__author__ = 'rolandh'

ATTRS = {"version": None,
         "name": "",
         "value": None,
         "port": None,
         "port_specified": False,
         "domain": "",
         "domain_specified": False,
         "domain_initial_dot": False,
         "path": "",
         "path_specified": False,
         "secure": False,
         "expires": None,
         "discard": True,
         "comment": None,
         "comment_url": None,
         "rest": "",
         "rfc2109": True}

PAIRS = {
    "port": "port_specified",
    "domain": "domain_specified",
    "path": "path_specified"
}


class ConnectionError(SAMLError):
    pass


class HTTPError(SAMLError):
    pass


TIME_FORMAT = ["%d-%b-%Y %H:%M:%S %Z", "%d-%b-%y %H:%M:%S %Z",
               "%d %b %Y %H:%M:%S %Z"]


def _since_epoch(cdate):
    """
    :param cdate: date format 'Wed, 06-Jun-2012 01:34:34 GMT'
    :return: UTC time
    """

    if len(cdate) < 29:  # somethings broken
        if len(cdate) < 5:
            return utc_now()

    cdate = cdate[5:] # assume short weekday, i.e. do not support obsolete RFC 1036 date format
    t = -1
    for time_format in TIME_FORMAT :
        try:
            t = time.strptime(cdate, time_format)   # e.g. 18-Apr-2014 12:30:51 GMT
        except ValueError:
            pass
        else:
            break

    if t == -1:
        raise (Exception,
               'ValueError: Date "{0}" does not match any of: {1}'.format(
                   cdate,TIME_FORMAT))

    return calendar.timegm(t)


def set_list2dict(sl):
    return dict(sl)


def dict2set_list(dic):
    return [(k, v) for k, v in dic.items()]


class HTTPBase(object):
    def __init__(self, verify=True, ca_bundle=None, key_file=None,
                 cert_file=None):
        self.request_args = {"allow_redirects": False}
        #self.cookies = {}
        self.cookiejar = http_cookiejar.CookieJar()

        self.request_args["verify"] = verify
        if verify:
            if ca_bundle:
                self.request_args["verify"] = ca_bundle
            if key_file:
                self.request_args["cert"] = (cert_file, key_file)

        self.sec = None
        self.user = None
        self.passwd = None

    def cookies(self, url):
        """
        Return cookies that are matching the path and are still valid

        :param url:
        :return:
        """
        part = urlparse(url)

        #if part.port:
        #    _domain = "%s:%s" % (part.hostname, part.port)
        #else:
        _domain = part.hostname

        cookie_dict = {}
        now = utc_now()
        for _, a in list(self.cookiejar._cookies.items()):
            for _, b in a.items():
                for cookie in list(b.values()):
                    # print(cookie)
                    if cookie.expires and cookie.expires <= now:
                        continue
                    if not re.search("%s$" % cookie.domain, _domain):
                        continue
                    if not re.match(cookie.path, part.path):
                        continue

                    cookie_dict[cookie.name] = cookie.value

        return cookie_dict

    def set_cookie(self, kaka, request):
        """Returns a http_cookiejar.Cookie based on a set-cookie header line"""

        if not kaka:
            return

        part = urlparse(request.url)
        _domain = part.hostname
        logger.debug("%s: '%s'", _domain, kaka)

        for cookie_name, morsel in kaka.items():
            std_attr = ATTRS.copy()
            std_attr["name"] = cookie_name
            _tmp = morsel.coded_value
            if _tmp.startswith('"') and _tmp.endswith('"'):
                std_attr["value"] = _tmp[1:-1]
            else:
                std_attr["value"] = _tmp

            std_attr["version"] = 0
            # copy attributes that have values
            for attr in morsel.keys():
                if attr in ATTRS:
                    if morsel[attr]:
                        if attr == "expires":
                            std_attr[attr] = _since_epoch(morsel[attr])
                        elif attr == "path":
                            if morsel[attr].endswith(","):
                                std_attr[attr] = morsel[attr][:-1]
                            else:
                                std_attr[attr] = morsel[attr]
                        else:
                            std_attr[attr] = morsel[attr]
                elif attr == "max-age":
                    if morsel["max-age"]:
                        std_attr["expires"] = time.time() + int(morsel["max-age"])

            for att, item in PAIRS.items():
                if std_attr[att]:
                    std_attr[item] = True

            if std_attr["domain"]:
                if std_attr["domain"].startswith("."):
                    std_attr["domain_initial_dot"] = True
            else:
                std_attr["domain"] = _domain
                std_attr["domain_specified"] = True

            if morsel["max-age"] is 0:
                try:
                    self.cookiejar.clear(domain=std_attr["domain"],
                                         path=std_attr["path"],
                                         name=std_attr["name"])
                except ValueError:
                    pass
            elif std_attr["expires"] and std_attr["expires"] < utc_now():
                try:
                    self.cookiejar.clear(domain=std_attr["domain"],
                                         path=std_attr["path"],
                                         name=std_attr["name"])
                except ValueError:
                    pass
            else:
                new_cookie = http_cookiejar.Cookie(**std_attr)
                self.cookiejar.set_cookie(new_cookie)

    def send(self, url, method="GET", **kwargs):
        _kwargs = copy.copy(self.request_args)
        if kwargs:
            _kwargs.update(kwargs)

        if self.cookiejar:
            _cd = self.cookies(url)
            if _cd:
                _kwargs["cookies"] = _cd

        if self.user and self.passwd:
            _kwargs["auth"] = (self.user, self.passwd)

        if "headers" in _kwargs and isinstance(_kwargs["headers"], list):
            if DICT_HEADERS:
                # requests.request wants a dict of headers, not a list of tuples
                _kwargs["headers"] = dict(_kwargs["headers"])

        try:
            logger.debug("%s to %s", method, url)
            for arg in ["cookies", "data", "auth"]:
                try:
                    logger.debug("%s: %s", arg.upper(), _kwargs[arg])
                except KeyError:
                    pass
            r = requests.request(method, url, **_kwargs)
            logger.debug("Response status: %s", r.status_code)
        except requests.ConnectionError as exc:
            raise ConnectionError("%s" % exc)

        try:
            self.set_cookie(SimpleCookie(r.headers["set-cookie"]), r)
        except AttributeError:
            pass
        except KeyError:
            pass

        return r

    @staticmethod
    def use_http_post(message, destination, relay_state,
                           typ="SAMLRequest"):
        """
        Return a urlencoded message that should be POSTed to the recipient.

        :param message: The response
        :param destination: Where the response should be sent
        :param relay_state: The relay_state received in the request
        :param typ: Whether a Request, Response or Artifact
        :return: dictionary
        """
        if not isinstance(message, six.string_types):
            message = "%s" % (message,)

        return http_post_message(message, relay_state, typ)

    @staticmethod
    def use_http_form_post(message, destination, relay_state,
                           typ="SAMLRequest"):
        """
        Return a form that will automagically execute and POST the message
        to the recipient.

        :param message:
        :param destination:
        :param relay_state:
        :param typ: Whether a Request, Response or Artifact
        :return: dictionary
        """
        if not isinstance(message, six.string_types):
            message = "%s" % (message,)

        return http_form_post_message(message, destination, relay_state, typ)

    @staticmethod
    def use_http_artifact(message, destination="", relay_state=""):
        if relay_state:
            query = urlencode({"SAMLart": message,
                               "RelayState": relay_state})
        else:
            query = urlencode({"SAMLart": message})
        info = {
            "data": "",
            "url": "%s?%s" % (destination, query)
        }
        return info

    @staticmethod
    def use_http_uri(message, typ, destination="", relay_state=""):
        if "\n" in message:
            data = message.split("\n")[1]
        else:
            data = message.strip()
        if typ == "SAMLResponse":
            info = {
                "data": data,
                "headers": [
                    ("Content-Type", "application/samlassertion+xml"),
                    ("Cache-Control", "no-cache, no-store"),
                    ("Pragma", "no-cache")
                ]
            }
        elif typ == "SAMLRequest":
            # msg should be an identifier
            if relay_state:
                query = urlencode({"ID": message,
                                   "RelayState": relay_state})
            else:
                query = urlencode({"ID": message})
            info = {
                "data": "",
                "url": "%s?%s" % (destination, query)
            }
        else:
            raise NotImplemented

        return info

    def use_soap(self, request, destination="", soap_headers=None, sign=False,
                 **kwargs):
        """
        Construct the necessary information for using SOAP+POST

        :param request:
        :param destination:
        :param soap_headers:
        :param sign:
        :return: dictionary
        """
        headers = [("content-type", "application/soap+xml")]

        soap_message = make_soap_enveloped_saml_thingy(request, soap_headers)

        logger.debug("SOAP message: %s", soap_message)

        if sign and self.sec:
            _signed = self.sec.sign_statement(soap_message,
                                              class_name=class_name(request),
                                              node_id=request.id)
            soap_message = _signed

        return {"url": destination, "method": "POST",
                "data": soap_message, "headers": headers}

    def send_using_soap(self, request, destination, headers=None, sign=False):
        """
        Send a message using SOAP+POST

        :param request:
        :param destination:
        :param headers:
        :param sign:
        :return:
        """

        # _response = self.server.post(soap_message, headers, path=path)
        try:
            args = self.use_soap(request, destination, headers, sign)
            args["headers"] = dict(args["headers"])
            response = self.send(**args)
        except Exception as exc:
            logger.info("HTTPClient exception: %s", exc)
            raise

        if response.status_code == 200:
            logger.info("SOAP response: %s", response.text)
            return response
        else:
            raise HTTPError("%d:%s" % (response.status_code, response.content))

    def add_credentials(self, user, passwd):
        self.user = user
        self.passwd = passwd

    @staticmethod
    def use_http_get(message, destination, relay_state,
                     typ="SAMLRequest", sigalg="", signer=None, **kwargs):
        """
        Send a message using GET, this is the HTTP-Redirect case so
        no direct response is expected to this request.

        :param message:
        :param destination:
        :param relay_state:
        :param typ: Whether a Request, Response or Artifact
        :param sigalg: Which algorithm the signature function will use to sign
            the message
        :param signer: A signing function that can be used to sign the message
        :return: dictionary
        """
        if not isinstance(message, six.string_types):
            message = "%s" % (message,)

        return http_redirect_message(message, destination, relay_state, typ,
                                     sigalg, signer)
