""" Simple BFG application demonstrating use of repoze.who in "hybrid" mode.

- repoze.who middleware intercepts and validates existing request credentials,
  leaving 'REMOTE_USER' in the WSGI environ if they are OK.

- Application handles login / logout directly, using the repoze.who API
  to validate credentials and set headers.
"""
import logging
import os
import sys
from StringIO import StringIO

from paste.httpserver import serve
from repoze.bfg.authentication import RemoteUserAuthenticationPolicy
from repoze.bfg.authorization import ACLAuthorizationPolicy
from repoze.bfg.configuration import Configurator
from repoze.bfg.security import Allow
from repoze.bfg.security import Authenticated
from repoze.bfg.security import DENY_ALL
from repoze.bfg.security import Everyone
from repoze.who.api import get_api
from repoze.who.interfaces import IChallenger
from repoze.who.middleware import PluggableAuthenticationMiddleware as PAM
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.redirector import RedirectorPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin
from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider
from webob import Response
from webob.exc import HTTPFound

LINK = ' <p><a href="%(url)s">%(title)s</a></p>'

ACTIONS = {
    'root': {'url': '/', 'title': 'Root'},   
    'protected': {'url': '/protected.html', 'title': 'Protected'},   
    'login': {'url': '/login.html', 'title': 'Login'},   
    'logout': {'url': '/logout.html', 'title': 'Logout'},   
}

def _actions(request):
    names = ['root']
    if 'REMOTE_USER' in request.environ:
        names.append('protected')
        names.append('logout')
    else:
        names.append('login')
    return '\n'.join([LINK % ACTIONS[x] for x in names])
    

PAGE = """\
<html>
<body>
 <h1>%(page_title)s</h1>
%(actions)s
</body>
</html>
"""

def unprotected(request):
    return Response(PAGE % {'page_title': 'Unprotected Page',
                            'actions': _actions(request),
                           })

def protected(request):
    return Response(PAGE % {'page_title': 'protected Page',
                            'actions': _actions(request),
                           })


LOGIN_FORM = """\
<html>
<body>
 <h1> Log In </h1>
 <form method="POST">
 %(came_from)s
 <p>%(message)s</p>
 <p>Login name: <input type="text" name="login" /></p>
 <p>Password: <input type="password" name="password" /></p>
 <p><input type="submit" name="form.login" value="Log In"/></p>
 </form>
</body>
</html>
"""

def login(request):
    message = ''
    info = {}

    # Remember any 'came_from', for redirection on succcesful login.
    came_from = request.params.get('came_from')
    if came_from is not None:
        info['came_from'] = (
        '<input type="hidden" name="came_from" value="%s" />' % came_from)
    else:
        info['came_from'] = ''

    who_api = get_api(request.environ)
    if 'form.login' in request.POST:
        # Validate credentials.
        creds = {}
        creds['login'] = request.POST['login']
        creds['password'] = request.POST['password']
        authenticated, headers = who_api.login(creds)

        if authenticated:
            # Redirect to 'came_from', or to root.
            # headers here are "remember" headers, setting the
            # auth_tkt cookies.
            return HTTPFound(location=came_from or '/',
                             headers=headers)

        else:
            message = 'Invalid login.'
    else:
        # Forcefully forget any existing credentials.
        _, headers = who_api.login({})

    # Headers here are "forget" headers, clearing the auth_tkt cookies.
    request.response_headerlist = headers

    if 'REMOTE_USER' in request.environ:
        del request.environ['REMOTE_USER']

    info['message'] = message

    return Response(LOGIN_FORM % info)


def logout(request):
    # Use repoze.who API to get "forget" headers.
    who_api = get_api(request.environ)
    return HTTPFound(location='/', headers=who_api.logout())


class Root(object):
    __acl__ = [(Allow, Authenticated, ('view_protected',)),
               (Allow, Everyone, ('view',)),
               DENY_ALL,
              ]

def get_root(*args, **kw):
    return Root()


if __name__ == '__main__':
    # Configure the BFG application

    ## Set up security policies, root object, etc.
    authentication_policy=RemoteUserAuthenticationPolicy()
    authorization_policy=ACLAuthorizationPolicy()
    config = Configurator(
                root_factory=get_root,
                default_permission='view',
                authentication_policy=authentication_policy,
                authorization_policy=authorization_policy,
               )
    config.begin()

    ## Configure views
    config.add_view(unprotected)
    config.add_view(protected, 'protected.html', permission='view_protected')
    config.add_view(login, 'login.html')
    config.add_view(logout, 'logout.html')
    config.end()

    ## Create the app object.
    app = config.make_wsgi_app()

    # Configure the repoze.who middleware:

    ## fake .htpasswd authentication source
    io = StringIO()
    for name, password in [('admin', 'admin'),
                           ('user', 'user')]:
        io.write('%s:%s\n' % (name, password))
    io.seek(0)
    def cleartext_check(password, hashed):
        return password == hashed
    htpasswd = HTPasswdPlugin(io, cleartext_check)

    ## other plugins
    basicauth = BasicAuthPlugin('repoze.who')
    auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt', digest_algo="sha512")
    redirector = RedirectorPlugin(login_url='/login.html')
    redirector.classifications = {IChallenger:['browser'] } # only for browser

    ## group / order plugins by function
    identifiers = [('auth_tkt', auth_tkt),
                   ('basicauth', basicauth)]
    authenticators = [('auth_tkt', auth_tkt),
                      ('htpasswd', htpasswd)]
    challengers = [('redirector', redirector),
                   ('basicauth', basicauth)]
    mdproviders = []

    ## set up who logging, if desired
    log_stream = None
    if os.environ.get('WHO_LOG'):
        log_stream = sys.stdout

    # Wrap the middleware around the application.
    middleware = PAM(app,
                     identifiers,
                     authenticators,
                     challengers,
                     mdproviders,
                     default_request_classifier,
                     default_challenge_decider,
                     log_stream = log_stream,
                     log_level = logging.DEBUG
                    )

    # Serve up the WSGI stack.
    serve(middleware, host='0.0.0.0')
