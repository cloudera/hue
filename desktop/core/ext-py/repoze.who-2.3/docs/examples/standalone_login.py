# Login application for demo SSO: using the repoze.who API.
from repoze.who.api import APIFactory
from repoze.who.config import WhoConfig
from webob import Request

LOGIN_FORM_TEMPLATE = """\
<html>
<head>
<title> Demo SSO Login </title>
</head>
<body>
<h1> Demo SSO Login </h1>
<p style="color: Red">%(message)s</p>
<form action="#" method="post">
 <input type="hidden" name="came_from" value="%(came_from)s" />
 <fieldset id="login_name_fs">
  <label for="login_name">Login Name</label>
  <input type="text" id="login_name" name="login_name" value="%(login_name)s" />
 </fieldset>
 <fieldset id="password_fs">
  <label for="password">Login Name</label>
  <input type="password" id="password" name="password" />
 </fieldset>
 <input type="submit" name="form.submitted" value="Log In" />
</form>
</body>
</html>
"""

MAX_AGE = '3600' # seconds

AUTH = {
    'phred': 'y4bb3d4bb4d00',
    'bharney': 'b3dr0ck',
}

# This config would normally be in a separate file:  inlined here for
# didactic purposes.
WHO_CONFIG = """\
[plugin:auth_tkt]
# identification + authorization
use = repoze.who.plugins.auth_tkt:make_plugin
secret = s33kr1t
cookie_name = auth_cookie
secure = True
include_ip = True
digest_algo = sha512

[general]
request_classifier = repoze.who.classifiers:default_request_classifier
challenge_decider = repoze.who.classifiers:default_challenge_decider
remote_user_key = REMOTE_USER

[identifiers]
plugins =
        auth_tkt

[authenticators]
plugins =
        auth_tkt

[challengers]
plugins =

[mdproviders]
plugins =
"""

# oh emacs python-mode, you disappoint me """

api_factory = None

def _configure_api_factory():
    global api_factory
    if api_factory is None:
        config = WhoConfig(here='/tmp') # XXX config file location
        config.parse(WHO_CONFIG)
        api_factory = APIFactory(identifiers=config.identifiers,
                                 authenticators=config.authenticators,
                                 challengers=config.challengers,
                                 mdproviders=config.mdproviders,
                                 request_classifier=config.request_classifier,
                                 challenge_decider=config.challenge_decider,
                                )
    return api_factory

def _validate(login_name, password):
    # Your application's logic goes here
    return AUTH.get(login_name) == password

def login(environ, start_response):
    request = Request(environ)
    message = ''
    if 'form.submitted' in request.POST:
        came_from = request.POST['came_from']
        login_name = request.POST['login_name']
        password = request.POST['password']
        remote_addr = environ['REMOTE_ADDR']
        tokens = userdata = ''
        if _validate(login_name, password):
            api = _configure_api_factory()(environ)
            headers = [('Location', came_from)]
            headers.extend(api.remember(login_name))
            start_response('302 Found', headers)
            return []
        message = 'Authentication failed'
    else:
        came_from = request.GET.get('came_from')
        login_name = ''

    body = LOGIN_FORM_TEMPLATE % {'message': message,
                                  'came_from': came_from,
                                  'login_name': login_name,
                                 }
    start_response('200 OK', [])
    return [body]

def main(global_config, **local_config):
    return login
