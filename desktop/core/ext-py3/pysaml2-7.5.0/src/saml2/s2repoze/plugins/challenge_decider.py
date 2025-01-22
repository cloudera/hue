import re

from paste.httpheaders import CONTENT_TYPE
from paste.httpheaders import REQUEST_METHOD
from paste.httpheaders import USER_AGENT
from paste.request import construct_url
from repoze.who.interfaces import IRequestClassifier
import zope.interface


_DAV_METHODS = (
    "OPTIONS",
    "PROPFIND",
    "PROPPATCH",
    "MKCOL",
    "LOCK",
    "UNLOCK",
    "TRACE",
    "DELETE",
    "COPY",
    "MOVE",
)

_DAV_USERAGENTS = (
    "Microsoft Data Access Internet Publishing Provider",
    "WebDrive",
    "Zope External Editor",
    "WebDAVFS",
    "Goliath",
    "neon",
    "davlib",
    "wsAPI",
    "Microsoft-WebDAV",
)


def my_request_classifier(environ):
    """Returns one of the classifiers 'dav', 'xmlpost', or 'browser',
    depending on the imperative logic below"""
    request_method = REQUEST_METHOD(environ)
    if request_method in _DAV_METHODS:
        return "dav"
    useragent = USER_AGENT(environ)
    if useragent:
        for agent in _DAV_USERAGENTS:
            if useragent.find(agent) != -1:
                return "dav"
    if request_method == "POST":
        if CONTENT_TYPE(environ) == "text/xml":
            return "xmlpost"
        elif CONTENT_TYPE(environ) == "application/soap+xml":
            return "soap"
    return "browser"


zope.interface.directlyProvides(my_request_classifier, IRequestClassifier)


class MyChallengeDecider:
    def __init__(self, path_login="", path_logout=""):
        self.path_login = path_login
        self.path_logout = path_logout

    def __call__(self, environ, status, _headers):
        if status.startswith("401 "):
            return True
        else:
            if "samlsp.pending" in environ:
                return True

            uri = environ.get("REQUEST_URI", None)
            if uri is None:
                uri = construct_url(environ)

            # require and challenge for logout and inform the challenge plugin that it is a logout we want
            for regex in self.path_logout:
                if regex.match(uri) is not None:
                    environ["samlsp.logout"] = True
                    return True

            # If the user is already authent, whatever happens(except logout),
            #   don't make a challenge
            if "repoze.who.identity" in environ:
                return False

            # require a challenge for login
            for regex in self.path_login:
                if regex.match(uri) is not None:
                    return True

        return False


def make_plugin(path_login=None, path_logout=None):
    if path_login is None:
        raise ValueError("must include path_login in configuration")

    # make regexp out of string passed via the config file
    list_login = []
    for arg in path_login.splitlines():
        carg = arg.lstrip()
        if carg != "":
            list_login.append(re.compile(carg))

    list_logout = []
    if path_logout is not None:
        for arg in path_logout.splitlines():
            carg = arg.lstrip()
            if carg != "":
                list_logout.append(re.compile(carg))

    plugin = MyChallengeDecider(list_login, list_logout)

    return plugin
