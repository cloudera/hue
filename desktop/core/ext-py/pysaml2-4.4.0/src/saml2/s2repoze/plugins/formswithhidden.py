import urllib

from paste.httpheaders import CONTENT_LENGTH
from paste.httpheaders import CONTENT_TYPE
from paste.httpheaders import LOCATION
from paste.httpexceptions import HTTPFound

from paste.request import parse_dict_querystring
from paste.request import parse_formvars
from paste.request import construct_url

from zope.interface import implements

from repoze.who.interfaces import IChallenger
from repoze.who.interfaces import IIdentifier
from repoze.who.plugins.form import FormPlugin

_DEFAULT_FORM = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" >
<html>
<head>
    <title>Demo Organization Log In</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body>
    <div>
        <strong>Demo Organization Log In</strong>
    </div>
    <form name="foo" method=POST action="?__do_login=true">
        <input type="text" name="login">
        <input type="password" name="password">
        <input name="submit" type="submit" value="Logga in">
        %s
    </form>
</body>
</html>
"""

HIDDEN_PRE_LINE = """<input type=hidden name="%s" value="%s">"""

class FormHiddenPlugin(FormPlugin):

    implements(IChallenger, IIdentifier)

    # IIdentifier
    def identify(self, environ):
        logger = environ.get('repoze.who.logger','')
        logger.info("formplugin identify")
        #logger and logger.info("environ keys: %s", environ.keys())
        query = parse_dict_querystring(environ)
        # If the extractor finds a special query string on any request,
        # it will attempt to find the values in the input body.
        if query.get(self.login_form_qs):
            form = parse_formvars(environ)
            from StringIO import StringIO
            # we need to replace wsgi.input because we've read it
            # this smells funny
            environ['wsgi.input'] = StringIO()
            form.update(query)
            qinfo = {}
            for key, val in form.items():
                if key.startswith("_") and key.endswith("_"):
                    qinfo[key[1:-1]] = val
            if qinfo:
                environ["s2repoze.qinfo"] = qinfo
            try:
                login = form['login']
                password = form['password']
            except KeyError:
                return None
            del query[self.login_form_qs]
            query.update(qinfo)
            environ['QUERY_STRING'] = urllib.urlencode(query)
            environ['repoze.who.application'] = HTTPFound(
                                                    construct_url(environ))
            credentials = {'login':login, 'password':password}
            max_age = form.get('max_age', None)
            if max_age is not None:
                credentials['max_age'] = max_age
            return credentials

        return None

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        logger = environ.get('repoze.who.logger','')
        logger.info("formplugin challenge")
        if app_headers:
            location = LOCATION(app_headers)
            if location:
                headers = list(app_headers) + list(forget_headers)
                return HTTPFound(headers = headers)

        query = parse_dict_querystring(environ)
        hidden = []
        for key, val in query.items():
            hidden.append(HIDDEN_PRE_LINE % ("_%s_" % key, val))

        logger.info("hidden: %s", hidden)
        form = self.formbody or _DEFAULT_FORM
        form = form % "\n".join(hidden)

        if self.formcallable is not None:
            form = self.formcallable(environ)
        def auth_form(environ, start_response):
            content_length = CONTENT_LENGTH.tuples(str(len(form)))
            content_type = CONTENT_TYPE.tuples('text/html')
            headers = content_length + content_type + forget_headers
            start_response('200 OK', headers)
            return [form]

        return auth_form


def make_plugin(login_form_qs='__do_login', rememberer_name=None, form=None):
    if rememberer_name is None:
        raise ValueError(
            'must include rememberer key (name of another IIdentifier plugin)')
    if form is not None:
        form = open(form).read()
    plugin = FormHiddenPlugin(login_form_qs, rememberer_name, form)
    return plugin

