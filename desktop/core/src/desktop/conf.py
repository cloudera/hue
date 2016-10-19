#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import os
import socket
import stat

from django.utils.translation import ugettext_lazy as _

from metadata.metadata_sites import get_navigator_audit_log_dir, get_navigator_audit_max_file_size

from desktop.redaction.engine import parse_redaction_policy_from_file
from desktop.lib.conf import Config, ConfigSection, UnspecifiedConfigSection,\
                             coerce_bool, coerce_csv, coerce_json_dict,\
                             validate_path, list_of_compiled_res, coerce_str_lowercase, \
                             coerce_password_from_script
from desktop.lib.i18n import force_unicode
from desktop.lib.paths import get_desktop_root


LOG = logging.getLogger(__name__)


def coerce_database(database):
  if database == 'mysql':
    return 'django.db.backends.mysql'
  elif database == 'postgres' or database == 'postgresql_psycopg2':
    return 'django.db.backends.postgresql_psycopg2'
  elif database == 'oracle':
    return 'django.db.backends.oracle'
  elif database in ('sqlite', 'sqlite3'):
    return 'django.db.backends.sqlite3'
  else:
    return str(database)


def coerce_port(port):
  try:
    port = int(port)
    if port == 0:
      port = ''
  except ValueError, e:
    port = ''
  return port


def coerce_file(path):
  if path and not os.path.isfile(path):
    raise Exception('File %s does not exist.' % path)
  return path


def coerce_timedelta(value):
  return datetime.timedelta(seconds=int(value))

def get_dn():
  """This function returns fqdn(if possible)"""
  val = []
  LOG = logging.getLogger(__name__)
  try:
    val.append(socket.getfqdn())
  except:
    LOG.warning("allowed_hosts value to '*'. It is a security risk")
    val.append('*')
  return val

def coerce_positive_integer(integer):
  integer = int(integer)

  if integer <= 0:
    raise Exception('integer is not positive')

  return integer

def is_https_enabled():
  """Hue is configured for HTTPS."""
  return bool(SSL_CERTIFICATE.get() and SSL_PRIVATE_KEY.get())

HTTP_HOST = Config(
  key="http_host",
  help=_("HTTP host to bind to."),
  type=str,
  default="0.0.0.0")

HTTP_PORT = Config(
  key="http_port",
  help=_("HTTP port to bind to."),
  type=int,
  default=8888)

HTTP_ALLOWED_METHODS = Config(
  key="http_allowed_methods",
  help=_("HTTP methods the server will be allowed to service."),
  type=coerce_csv,
  private=True,
  default=['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT'])

X_FRAME_OPTIONS = Config(
  key="http_x_frame_options",
  help=_("X-Frame-Options HTTP header value."),
  type=str,
  default="SAMEORIGIN")

SSL_CERTIFICATE = Config(
  key="ssl_certificate",
  help=_("Filename of SSL Certificate"),
  type=coerce_file,
  default=None)

SSL_PRIVATE_KEY = Config(
  key="ssl_private_key",
  help=_("Filename of SSL RSA Private Key"),
  type=coerce_file,
  default=None)

SSL_CERTIFICATE_CHAIN = Config(
  key="ssl_certificate_chain",
  help=_("Filename of SSL Certificate Chain"),
  type=coerce_file,
  default=None)

SSL_CIPHER_LIST = Config(
  key="ssl_cipher_list",
  help=_("List of allowed and disallowed ciphers"),

  # From https://wiki.mozilla.org/Security/Server_Side_TLS v3.7 default
  # recommendation, which should be compatible with Firefox 1, Chrome 1, IE 7,
  # Opera 5 and Safari 1.
  default=(
      "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:"
      "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:"
      "DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:"
      "kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:"
      "ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:"
      "ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:"
      "ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:"
      "DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:"
      "DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:"
      "AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:"
      "!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:"
      "!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA"
  ))

SSL_PASSWORD = Config(
  key="ssl_password",
  help=_("SSL password of the certificate"),
  default=None)

SSL_PASSWORD_SCRIPT = Config(
  key="ssl_password_script",
  help=_("Execute this script to produce the SSL password. This will be used when `ssl_password` is not set."),
  type=coerce_password_from_script,
  default=None)

SSL_CACERTS = Config(
  key="ssl_cacerts",
  help=_('Path to default Certificate Authority certificates.'),
  type=str,
  default='')

SSL_VALIDATE = Config(
  key="ssl_validate",
  help=_('Choose whether Hue should validate certificates received from the server.'),
  type=coerce_bool,
  default=True)

SECURE_HSTS_SECONDS = Config(
  key="secure_hsts_seconds",
  help=_('Strict-Transport-Security: max-age=31536000 This is a HTTP response header, Once a supported browser receives this header that browser will prevent any communications from being sent over HTTP to the specified domain and will instead send all communications over HTTPS.'),
  type=int,
  default=31536000)

SECURE_HSTS_INCLUDE_SUBDOMAINS = Config(
  key="secure_hsts_include_subdomains",
  help=_('Strict-Transport-Security: This is a HTTP response header, Once a supported browser receives this header that browser will prevent any communications from being sent over HTTP to the specified domain and will instead send all communications over HTTPS.'),
  type=coerce_bool,
  default=True)

SECURE_CONTENT_TYPE_NOSNIFF = Config(
  key="secure_content_type_nosniff",
  help=_('X-Content-Type-Options: nosniff This is a HTTP response header feature that helps prevent attacks based on MIME-type confusion.'),
  type=coerce_bool,
  default=True)

SECURE_BROWSER_XSS_FILTER = Config(
  key="secure_browser_xss_filter",
  help=_('X-Xss-Protection: \"1; mode=block\" This is a HTTP response header feature to force XSS protection.'),
  type=coerce_bool,
  default=True)

SECURE_CONTENT_SECURITY_POLICY = Config(
  key="secure_content_security_policy",
  help=_('X-Content-Type-Options: nosniff This is a HTTP response header feature that helps prevent attacks based on MIME-type confusion.'),
  type=str,
  default="script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net *.mathjax.org data:;"+
          "img-src 'self' *.google-analytics.com *.doubleclick.net http://*.tile.osm.org *.tile.osm.org *.gstatic.com data:;"+
          "style-src 'self' 'unsafe-inline';"+
          "connect-src 'self';"+
          "child-src 'self' data:;"+
          "object-src 'none'")

SECURE_SSL_REDIRECT = Config(
  key="secure_ssl_redirect",
  help=_('If all non-SSL requests should be permanently redirected to SSL.'),
  type=coerce_bool,
  dynamic_default=is_https_enabled)

SECURE_SSL_HOST = Config(
  key="secure_redirect_host",
  help=_('If all non-SSL requests should be permanently redirected to this SSL host.'),
  type=str,
  default="0.0.0.0")

SECURE_REDIRECT_EXEMPT = Config(
  key="secure_redirect_exempt",
  help=_('Comma separated list of strings representing the host/domain names that the Hue server can not serve https.'),
  type=coerce_csv,
  default=[])

# Deprecated by AUTH_PASSWORD
LDAP_PASSWORD = Config(
  key="ldap_password",
  help=_("LDAP password of the hue user used for LDAP authentications. For example for LDAP Authentication with HiveServer2/Impala."),
  private=True,
  default=None)

# Deprecated by AUTH_PASSWORD_SCRIPT
LDAP_PASSWORD_SCRIPT = Config(
  key="ldap_password_script",
  help=_("Execute this script to produce the LDAP password. This will be used when `ldap_password` is not set."),
  private=True,
  type=coerce_password_from_script,
  default=None)

# Deprecated by by AUTH_USERNAME
LDAP_USERNAME = Config(
  key="ldap_username",
  help=_("LDAP username of the hue user used for LDAP authentications. For example for LDAP Authentication with HiveServer2/Impala."),
  private=True,
  default="hue")

def get_auth_username():
  """Backward compatibility"""
  return LDAP_USERNAME.get()

AUTH_USERNAME = Config(
  key="auth_username",
  help=_("Auth username of the hue user used for authentications. For example for LDAP Authentication with HiveServer2/Impala."),
  dynamic_default=get_auth_username)

def get_auth_password():
  """Get from script or backward compatibility"""

  password = os.environ.get('HUE_AUTH_PASSWORD')
  if password is not None:
    return password

  password = AUTH_PASSWORD_SCRIPT.get()
  if password:
    return password

  password = os.environ.get('HUE_LDAP_PASSWORD')
  if password is not None:
    return password

  password = LDAP_PASSWORD.get() # 2 levels for backward compatibility
  if password:
    return password

  return LDAP_PASSWORD_SCRIPT.get()

AUTH_PASSWORD = Config(
  key="auth_password",
  help=_("LDAP/PAM/.. password of the hue user used for authentications. Inactive if empty. For example for LDAP Authentication with HiveServer2/Impala."),
  private=True,
  dynamic_default=get_auth_password)

AUTH_PASSWORD_SCRIPT = Config(
  key="auth_password_script",
  help=_("Execute this script to produce the auth password. This will be used when `auth_password` is not set."),
  private=True,
  type=coerce_password_from_script,
  default=None)

ENABLE_SERVER = Config(
  key="enable_server",
  help=_("If set to false, runcpserver will not actually start the web server.  Used if Apache is being used as a WSGI container."),
  type=coerce_bool,
  default=True)

CHERRYPY_SERVER_THREADS = Config(
  key="cherrypy_server_threads",
  help=_("Number of threads used by the CherryPy web server."),
  type=int,
  default=40)

SECRET_KEY = Config(
  key="secret_key",
  help=_("Used in hashing algorithms for sessions."),
  default="")

SECRET_KEY_SCRIPT = Config(
  key="secret_key_script",
  help=_("Execute this script to produce the Django secret key. This will be used when `secret_key` is not set."),
  type=coerce_password_from_script,
  private=True,
  default="")

USER_ACCESS_HISTORY_SIZE = Config(
  key="user_access_history_size",
  help=_("Number of user access to remember per view per user."),
  type=int,
  default=10)

COLLECT_USAGE = Config(
  key="collect_usage",
  help=_("Help improve Hue with anonymous usage analytics."
         "Use Google Analytics to see how many times an application or specific section of an application is used, nothing more."),
  type=coerce_bool,
  default=True)

LEAFLET_TILE_LAYER = Config(
  key="leaflet_tile_layer",
  help=_("Tile layer server URL for the Leaflet map charts. Read more on http://leafletjs.com/reference.html#tilelayer. Make sure you add the tile domain to the img-src section of the 'secure_content_security_policy' configuration parameter as well."),
  type=coerce_str_lowercase,
  default="http://{s}.tile.osm.org/{z}/{x}/{y}.png")

LEAFLET_TILE_LAYER_ATTRIBUTION = Config(
  key="leaflet_tile_layer_attribution",
  help=_("The copyright message for the specified Leaflet maps Tile Layer"),
  default='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors')

POLL_ENABLED = Config(
  key="poll_enabled",
  help=_("Use poll(2) in Hue thrift pool."),
  type=coerce_bool,
  private=True,
  default=True)

MIDDLEWARE = Config(
  key="middleware",
  help=_("Comma-separated list of Django middleware classes to use. " +
         "See https://docs.djangoproject.com/en/1.4/ref/middleware/ for " +
         "more details on middlewares in Django."),
  type=coerce_csv,
  default=[])

REDIRECT_WHITELIST = Config(
  key="redirect_whitelist",
  help=_("Comma-separated list of regular expressions, which match the redirect URL."
         "For example, to restrict to your local domain and FQDN, the following value can be used:"
         "  ^\/.*$,^http:\/\/www.mydomain.com\/.*$"),
  type=list_of_compiled_res(skip_empty=True),
  default='^(\/[a-zA-Z0-9]+.*|\/)$')

USE_X_FORWARDED_HOST = Config(
  key="use_x_forwarded_host",
  help=_("Enable X-Forwarded-Host header if the load balancer requires it."),
  type=coerce_bool,
  default=False)

SECURE_PROXY_SSL_HEADER = Config(
  key="secure_proxy_ssl_header",
  help=_("Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER."),
  type=coerce_bool,
  default=False)

APP_BLACKLIST = Config(
  key='app_blacklist',
  default='',
  type=coerce_csv,
  help=_('Comma separated list of apps to not load at server startup.')
)

DEMO_ENABLED = Config( # Internal and Temporary
  key="demo_enabled",
  help=_("To set to true in combination when using Hue demo backend."),
  type=coerce_bool,
  private=True,
  default=False)

LOG_REDACTION_FILE = Config(
  key="log_redaction_file",
  help=_("Use this file to parse and redact log message."),
  type=parse_redaction_policy_from_file,
  default=None)

ALLOWED_HOSTS = Config(
  key='allowed_hosts',
  dynamic_default=get_dn,
  type=coerce_csv,
  help=_('Comma separated list of strings representing the host/domain names that the Hue server can serve.')
)

def default_secure_cookie():
  """Enable secure cookies if HTTPS is enabled."""
  return is_https_enabled()

def default_ssl_cacerts():
  """Path to default Certificate Authority certificates"""
  return SSL_CACERTS.get()

def default_ssl_validate():
  """Choose whether Hue should validate certificates received from the server."""
  return SSL_VALIDATE.get()

#
# Email (SMTP) settings
#
_default_from_email = None
def default_from_email():
  """Email for hue@<host-fqdn>"""
  global _default_from_email
  if _default_from_email is None:
    try:
      fqdn = socket.getfqdn()
    except IOError:
      fqdn = 'localhost'
    _default_from_email = "hue@" + fqdn
  return _default_from_email


def default_database_options():
  """Database type dependent options"""
  if DATABASE.ENGINE.get().endswith('oracle'):
    return {'threaded': True}
  elif DATABASE.ENGINE.get().endswith('sqlite3'):
    return {'timeout': 30}
  else:
    return {}

def get_deprecated_login_lock_out_by_combination_browser_user_agent():
  """Return value of deprecated LOGIN_LOCK_OUT_BY_COMBINATION_BROWSER_USER_AGENT_AND_IP config"""
  return AUTH.LOGIN_LOCK_OUT_BY_COMBINATION_BROWSER_USER_AGENT_AND_IP.get()


SMTP = ConfigSection(
  key='smtp',
  help=_('Configuration options for connecting to an external SMTP server.'),
  members=dict(
    HOST = Config(
      key="host",
      help=_("The SMTP server for email notification delivery."),
      type=str,
      default="localhost"
    ),

    PORT = Config(
      key="port",
      help=_("The SMTP server port."),
      type=int,
      default=25
    ),

    USER = Config(
      key="user",
      help=_("The username for the SMTP host."),
      type=str,
      default=""
    ),

    PASSWORD = Config(
      key="password",
      help=_("The password for the SMTP user."),
      type=str,
      private=True,
      default="",
    ),

    PASSWORD_SCRIPT = Config(
      key="password_script",
      help=_("Execute this script to produce the SMTP user password. This will be used when the SMTP `password` is not set."),
      type=coerce_password_from_script,
      private=True,
      default="",
    ),

    USE_TLS = Config(
      key="tls",
      help=_("Whether to use a TLS (secure) connection when talking to the SMTP server."),
      type=coerce_bool,
      default=False
    ),

    DEFAULT_FROM= Config(
      key="default_from_email",
      help=_("Default email address to use for various automated notifications from Hue."),
      type=str,
      dynamic_default=default_from_email
    ),
  )
)

METRICS = ConfigSection(
  key='metrics',
  help=_("""Configuration options for metrics"""),
  members=dict(
    ENABLE_WEB_METRICS=Config(
      key='enable_web_metrics',
      help=_('Enable metrics URL "desktop/metrics"'),
      default=True,
      type=coerce_bool),
    LOCATION=Config(
      key='location',
      help=_('If specified, Hue will write metrics to this file'),
      type=str),
    COLLECTION_INTERVAL=Config(
      key='collection_interval',
      help=_('Time in milliseconds on how frequently to collect metrics'),
      type=coerce_positive_integer,
      default=30000),
  )
)

DATABASE = ConfigSection(
  key='database',
  help=_("""Configuration options for specifying the Desktop Database.
          For more info, see http://docs.djangoproject.com/en/1.4/ref/settings/#database-engine"""),
  members=dict(
    ENGINE=Config(
      key='engine',
      help=_('Database engine, such as postgresql_psycopg2, mysql, or sqlite3.'),
      type=coerce_database,
      default='django.db.backends.sqlite3',
    ),
    NAME=Config(
      key='name',
      help=_('Database name, or path to DB if using sqlite3.'),
      type=str,
      default=get_desktop_root('desktop.db'),
    ),
    USER=Config(
      key='user',
      help=_('Database username.'),
      type=str,
      default='',
    ),
    PASSWORD=Config(
      key='password',
      help=_('Database password.'),
      private=True,
      type=str,
      default="",
    ),
    PASSWORD_SCRIPT=Config(
      key='password_script',
      help=_('Execute this script to produce the database password. This will be used when `password` is not set.'),
      private=True,
      type=coerce_password_from_script,
      default="",
    ),
    HOST=Config(
      key='host',
      help=_('Database host.'),
      type=str,
      default='',
    ),
    PORT=Config(
      key='port',
      help=_('Database port.'),
      type=coerce_port,
      default='',
    ),
    OPTIONS=Config(
      key='options',
      help=_('Database options to send to the server when connecting.'),
      type=coerce_json_dict,
      dynamic_default=default_database_options
    )
  )
)

SESSION = ConfigSection(
  key='session',
  help=_("""Configuration options for specifying the Desktop session.
          For more info, see https://docs.djangoproject.com/en/1.4/topics/http/sessions/"""),
  members=dict(
    TTL=Config(
      key='ttl',
      help=_("The cookie containing the users' session ID will expire after this amount of time in seconds."),
      type=int,
      default=60*60*24*14,
    ),
    SECURE=Config(
      key='secure',
      help=_("The cookie containing the users' session ID will be secure. This should only be enabled with HTTPS."),
      type=coerce_bool,
      dynamic_default=default_secure_cookie,
    ),
    HTTP_ONLY=Config(
      key='http_only',
      help=_("The cookie containing the users' session ID will use the HTTP only flag."),
      type=coerce_bool,
      default=True,
    ),
    EXPIRE_AT_BROWSER_CLOSE=Config(
      key='expire_at_browser_close',
      help=_("Use session-length cookies. Logs out the user when she closes the browser window."),
      type=coerce_bool,
      default=False
    )
  )
)

KERBEROS = ConfigSection(
  key="kerberos",
  help=_("""Configuration options for specifying Hue's Kerberos integration for
          secured Hadoop clusters."""),
  members=dict(
    HUE_KEYTAB=Config(
      key='hue_keytab',
      help=_("Path to a Kerberos keytab file containing Hue's service credentials."),
      type=str,
      default=None),
    HUE_PRINCIPAL=Config(
      key='hue_principal',
      help=_("Kerberos principal name for Hue. Typically 'hue/hostname.foo.com'."),
      type=str,
      default="hue/%s" % socket.getfqdn()),
    KEYTAB_REINIT_FREQUENCY=Config(
      key='reinit_frequency',
      help=_("Frequency in seconds with which Hue will renew its keytab."),
      type=int,
      default=60*60), #1h
    CCACHE_PATH=Config(
      key='ccache_path',
      help=_("Path to keep Kerberos credentials cached."),
      private=True,
      type=str,
      default="/tmp/hue_krb5_ccache",
    ),
    KINIT_PATH=Config(
      key='kinit_path',
      help=_("Path to Kerberos 'kinit' command."),
      type=str,
      default="kinit", # use PATH!
    )
  )
)

SASL_MAX_BUFFER = Config(
  key="sasl_max_buffer",
  help=_("This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication."),
  default=2*1024*1024,  # 2 MB
  type=int
)

# See python's documentation for time.tzset for valid values.
TIME_ZONE = Config(
  key="time_zone",
  help=_("Time zone name."),
  type=str,
  default=os.environ.get("TZ", "America/Los_Angeles")
)

DEFAULT_SITE_ENCODING = Config(
  key='default_site_encoding',
  help=_('Default system-wide unicode encoding.'),
  type=str,
  default='utf-8'
)

SERVER_USER = Config(
  key="server_user",
  help=_("Username to run servers as."),
  type=str,
  default="hue")

SERVER_GROUP = Config(
  key="server_group",
  help=_("Group to run servers as."),
  type=str,
  default="hue")

DEFAULT_USER = Config(
  key="default_user",
  help=_("This should be the user running hue webserver"),
  type=str,
  default="hue")

DEFAULT_HDFS_SUPERUSER = Config(
  key="default_hdfs_superuser",
  help=_("This should be the hdfs super user"),
  type=str,
  default="hdfs")

CUSTOM = ConfigSection(
  key="custom",
  help=_("Customizations to the UI."),
  members=dict(
    BANNER_TOP_HTML=Config("banner_top_html",
                   default="",
                   help=_("Top banner HTML code. This code will be placed in the navigation bar "
                        "so that it will reside at the top of the page in a fixed position. " +
                        "One common value is `<img src=\"http://www.example.com/example.gif\" />`")),
    LOGIN_SPLASH_HTML=Config("login_splash_html",
                   default="",
                   help=_("The login splash HTML code. This code will be placed in the login page, "
                        "useful for security warning messages.")),
    CACHEABLE_TTL=Config("cacheable_ttl",
                   default=86400000,
                   type=int,
                   help=_("The cache TTL in milliseconds for the assist/autocomplete/etc calls. Set to 0 it disables the cache.")),
))

AUTH = ConfigSection(
  key="auth",
  help=_("Configuration options for user authentication into the web application."),
  members=dict(
    BACKEND=Config("backend",
                   default=["desktop.auth.backend.AllowFirstUserDjangoBackend"],
                   type=coerce_csv,
                   help=_("Authentication backend.  Common settings are "
                        "django.contrib.auth.backends.ModelBackend (fully Django backend), " +
                        "desktop.auth.backend.AllowAllBackend (allows everyone), " +
                        "desktop.auth.backend.AllowFirstUserDjangoBackend (relies on Django and user manager, after the first login). " +
                        "Multiple Authentication backends are supported by specifying a comma-separated list in order of priority.")),
    USER_AUGMENTOR=Config("user_augmentor",
                   default="desktop.auth.backend.DefaultUserAugmentor",
                   help=_("Class which defines extra accessor methods for User objects.")),
    PAM_SERVICE=Config("pam_service",
                  default="login",
                  help=_("The service to use when querying PAM. "
                         "The service usually corresponds to a single filename in /etc/pam.d")),
    REMOTE_USER_HEADER=Config("remote_user_header",
                        default="HTTP_REMOTE_USER",
                        help=_("When using the desktop.auth.backend.RemoteUserDjangoBackend, this sets "
                               "the normalized name of the header that contains the remote user. "
                               "The HTTP header in the request is converted to a key by converting "
                               "all characters to uppercase, replacing any hyphens with underscores "
                               "and adding an HTTP_ prefix to the name. So, for example, if the header "
                               "is called Remote-User that would be configured as HTTP_REMOTE_USER")),
    IGNORE_USERNAME_CASE = Config("ignore_username_case",
                                  help=_("Ignore the case of usernames when searching for existing users in Hue."),
                                  type=coerce_bool,
                                  default=True),
    FORCE_USERNAME_LOWERCASE = Config("force_username_lowercase",
                                      help=_("Force usernames to lowercase when creating new users."),
                                      type=coerce_bool,
                                      default=True),
    FORCE_USERNAME_UPPERCASE = Config("force_username_uppercase",
                                      help=_("Force usernames to uppercase when creating new users."),
                                      type=coerce_bool,
                                      default=False),
    EXPIRES_AFTER = Config("expires_after",
                            help=_("Users will expire after they have not logged in for 'n' amount of seconds."
                                   "A negative number means that users will never expire."),
                            type=int,
                            default=-1),
    EXPIRE_SUPERUSERS = Config("expire_superusers",
                                help=_("Apply 'expires_after' to superusers."),
                                type=coerce_bool,
                                default=True),
    IDLE_SESSION_TIMEOUT = Config("idle_session_timeout",
                            help=_("Users will automatically be logged out after 'n' seconds of inactivity."
                                   "A negative number means that idle sessions will not be timed out."),
                            type=int,
                            default=-1),
    CHANGE_DEFAULT_PASSWORD = Config(
                            key="change_default_password",
                            help=_("When set to true this will allow you to specify a password for "
                                   "the user when you create the user and then force them to change "
                                   "their password upon first login.  The default is false."),
                            type=coerce_bool,
                            default=False,
    ),
    LOGIN_FAILURE_LIMIT = Config(
      key="login_failure_limit",
      help=_("Number of login attempts allowed before a record is created for failed logins"),
      type=int,
      default=3,
    ),
    LOGIN_LOCK_OUT_AT_FAILURE = Config(
      key="login_lock_out_at_failure",
      help=_("After number of allowed login attempts are exceeded, do we lock out this IP and optionally user agent?"),
      type=coerce_bool,
      default=False,
    ),
    LOGIN_COOLOFF_TIME = Config(
      key="login_cooloff_time",
      help=_("If set, defines period of inactivity in seconds after which failed logins will be forgotten"),
      type=coerce_timedelta,
      default=None,
    ),
    # Deprecated by LOGIN_LOCK_OUT_USE_USER_AGENT
    LOGIN_LOCK_OUT_BY_COMBINATION_BROWSER_USER_AGENT_AND_IP=Config(
      key="login_lock_out_by_combination_browser_user_agent_and_ip",
      help=_("If True, lock out based on IP and browser user agent"),
      type=coerce_bool,
      default=False,
    ),
    LOGIN_LOCK_OUT_USE_USER_AGENT = Config(
      key="login_lock_out_use_user_agent",
      help=_("If True, lock out based on an IP address AND a user agent."
             "This means requests from different user agents but from the same IP are treated differently."),
      type=coerce_bool,
      dynamic_default=get_deprecated_login_lock_out_by_combination_browser_user_agent
    ),
    LOGIN_LOCK_OUT_BY_COMBINATION_USER_AND_IP = Config(
      key="login_lock_out_by_combination_user_and_ip",
      help=_("If True, lock out based on IP and user"),
      type=coerce_bool,
      default=False,
    ),
    BEHIND_REVERSE_PROXY = Config(
      key="behind_reverse_proxy",
      help=_("If True, it will look for the IP address from the header defined at reverse_proxy_header."),
      type=coerce_bool,
      default=False,
    ),
    REVERSE_PROXY_HEADER = Config(
      key="reverse_proxy_header",
      help=_("If behind_reverse_proxy is True, it will look for the IP address from this header. Default: HTTP_X_FORWARDED_FOR"),
      type=str,
      default="HTTP_X_FORWARDED_FOR",
    ),
))


LDAP = ConfigSection(
  key="ldap",
  help=_("Configuration options for LDAP connectivity."),
  members=dict(
    CREATE_USERS_ON_LOGIN = Config("create_users_on_login",
      help=_("Create users when they login with their LDAP credentials."),
      type=coerce_bool,
      default=True),
    SYNC_GROUPS_ON_LOGIN = Config("sync_groups_on_login",
      help=_("Synchronize a users groups when they login."),
      type=coerce_bool,
      default=False),
    IGNORE_USERNAME_CASE = Config("ignore_username_case",
      help=_("Ignore the case of usernames when searching for existing users in Hue."),
      type=coerce_bool,
      default=True),
    FORCE_USERNAME_LOWERCASE = Config("force_username_lowercase",
      help=_("Force usernames to lowercase when creating new users from LDAP."),
      type=coerce_bool,
      default=True),
    FORCE_USERNAME_UPPERCASE = Config("force_username_uppercase",
      help=_("Force usernames to uppercase when creating new users from LDAP."),
      type=coerce_bool,
      default=False),
    SUBGROUPS = Config("subgroups",
      help=_("Choose which kind of subgrouping to use: nested or suboordinate (deprecated)."),
      type=coerce_str_lowercase,
      default="suboordinate"),
    NESTED_MEMBERS_SEARCH_DEPTH = Config("nested_members_search_depth",
      help=_("Define the number of levels to search for nested members."),
      type=int,
      default=10),
    FOLLOW_REFERRALS = Config("follow_referrals",
      help=_("Whether or not to follow referrals."),
      type=coerce_bool,
      default=False),

    DEBUG = Config("debug",
      type=coerce_bool,
      default=False,
      help=_("Set to a value to enable python-ldap debugging.")),
    DEBUG_LEVEL = Config("debug_level",
      default=255,
      type=int,
      help=_("Sets the debug level within the underlying LDAP C lib.")),
    TRACE_LEVEL = Config("trace_level",
      default=0,
      type=int,
      help=_("Possible values for trace_level are 0 for no logging, 1 for only logging the method calls with arguments,"
             "2 for logging the method calls with arguments and the complete results and 9 for also logging the traceback of method calls.")),

    LDAP_SERVERS = UnspecifiedConfigSection(
      key="ldap_servers",
      help=_("LDAP server record."),
      each=ConfigSection(
        members=dict(
          BASE_DN=Config("base_dn",
                         default=None,
                         help=_("The base LDAP distinguished name to use for LDAP search.")),
          NT_DOMAIN=Config("nt_domain",
                           default=None,
                           help=_("The NT domain used for LDAP authentication.")),
          LDAP_URL=Config("ldap_url",
                           default=None,
                           help=_("The LDAP URL to connect to.")),
          USE_START_TLS=Config("use_start_tls",
                               default=True,
                               type=coerce_bool,
                               help=_("Use StartTLS when communicating with LDAP server.")),
          LDAP_CERT=Config("ldap_cert",
                           default=None,
                           help=_("A PEM-format file containing certificates for the CA's that Hue will trust for authentication over TLS. The certificate for the CA that signed the LDAP server certificate must be included among these certificates. See more here http://www.openldap.org/doc/admin24/tls.html.")),
          LDAP_USERNAME_PATTERN=Config("ldap_username_pattern",
                                       default=None,
                                       help=_("A pattern to use for constructing LDAP usernames.")),
          BIND_DN=Config("bind_dn",
                         default=None,
                         help=_("The distinguished name to bind as, when importing from LDAP.")),
          BIND_PASSWORD=Config("bind_password",
                               default=None,
                               private=True,
                               help=_("The password for the bind user.")),
          BIND_PASSWORD_SCRIPT=Config("bind_password_script",
                                    default=None,
                                    private=True,
                                    type=coerce_password_from_script,
                                    help=_("Execute this script to produce the LDAP bind user password. This will be used when `bind_password` is not set.")),
          SEARCH_BIND_AUTHENTICATION=Config("search_bind_authentication",
                                            default=True,
                                            type=coerce_bool,
                                            help=_("Use search bind authentication.")),
          FOLLOW_REFERRALS = Config("follow_referrals",
                                    help=_("Whether or not to follow referrals."),
                                    type=coerce_bool,
                                    default=False),

          DEBUG = Config("debug",
            type=coerce_bool,
            default=False,
            help=_("Set to a value to enable python-ldap debugging.")),
          DEBUG_LEVEL = Config("debug_level",
            default=255,
            type=int,
            help=_("Sets the debug level within the underlying LDAP C lib.")),
          TRACE_LEVEL = Config("trace_level",
            default=0,
            type=int,
            help=_("Possible values for trace_level are 0 for no logging, 1 for only logging the method calls with arguments,"
                   "2 for logging the method calls with arguments and the complete results and 9 for also logging the traceback of method calls.")),

          USERS = ConfigSection(
            key="users",
            help=_("Configuration for LDAP user schema and search."),
            members=dict(
              USER_FILTER=Config("user_filter",
                                 default="objectclass=*",
                                 help=_("A base filter for use when searching for users.")),
              USER_NAME_ATTR=Config("user_name_attr",
                                    default="sAMAccountName",
                                    help=_("The username attribute in the LDAP schema. "
                                         "Typically, this is 'sAMAccountName' for AD and 'uid' "
                                         "for other LDAP systems.")),
            )
          ),

          GROUPS = ConfigSection(
            key="groups",
            help=_("Configuration for LDAP group schema and search."),
            members=dict(
              GROUP_FILTER=Config("group_filter",
                                 default="objectclass=*",
                                 help=_("A base filter for use when searching for groups.")),
              GROUP_NAME_ATTR=Config("group_name_attr",
                                    default="cn",
                                    help=_("The group name attribute in the LDAP schema. "
                                        "Typically, this is 'cn'.")),
              GROUP_MEMBER_ATTR=Config("group_member_attr",
                                       default="member",
                                       help=_("The LDAP attribute which specifies the "
                                            "members of a group.")),
            ))))),

    # Every thing below here is deprecated and should be removed in an upcoming major release.
    BASE_DN=Config("base_dn",
                   default=None,
                   help=_("The base LDAP distinguished name to use for LDAP search.")),
    NT_DOMAIN=Config("nt_domain",
                     default=None,
                     help=_("The NT domain used for LDAP authentication.")),
    LDAP_URL=Config("ldap_url",
                     default=None,
                     help=_("The LDAP URL to connect to.")),
    USE_START_TLS=Config("use_start_tls",
                         default=True,
                         type=coerce_bool,
                         help=_("Use StartTLS when communicating with LDAP server.")),
    LDAP_CERT=Config("ldap_cert",
                     default=None,
                     help=_("A PEM-format file containing certificates for the CA's that Hue will trust for authentication over TLS. The certificate for the CA that signed the LDAP server certificate must be included among these certificates. See more here http://www.openldap.org/doc/admin24/tls.html.")),
    LDAP_USERNAME_PATTERN=Config("ldap_username_pattern",
                                 default=None,
                                 help=_("A pattern to use for constructing LDAP usernames.")),
    BIND_DN=Config("bind_dn",
                   default=None,
                   help=_("The distinguished name to bind as, when importing from LDAP.")),
    BIND_PASSWORD=Config("bind_password",
                   default=None,
                   private=True,
                   help=_("The password for the bind user.")),
    BIND_PASSWORD_SCRIPT=Config("bind_password_script",
                   default=None,
                   private=True,
                   type=coerce_password_from_script,
                   help=_("Execute this script to produce the LDAP bind user password. This will be used when `bind_password` is not set.")),
    SEARCH_BIND_AUTHENTICATION=Config("search_bind_authentication",
                   default=True,
                   type=coerce_bool,
                   help=_("Use search bind authentication.")),

    USERS = ConfigSection(
      key="users",
      help=_("Configuration for LDAP user schema and search."),
      members=dict(
        USER_FILTER=Config("user_filter",
                           default="objectclass=*",
                           help=_("A base filter for use when searching for users.")),
        USER_NAME_ATTR=Config("user_name_attr",
                              default="sAMAccountName",
                              help=_("The username attribute in the LDAP schema. "
                                   "Typically, this is 'sAMAccountName' for AD and 'uid' "
                                   "for other LDAP systems.")),
      )),

    GROUPS = ConfigSection(
      key="groups",
      help=_("Configuration for LDAP group schema and search."),
      members=dict(
        GROUP_FILTER=Config("group_filter",
                           default="objectclass=*",
                           help=_("A base filter for use when searching for groups.")),
        GROUP_NAME_ATTR=Config("group_name_attr",
                              default="cn",
                              help=_("The group name attribute in the LDAP schema. "
                                  "Typically, this is 'cn'.")),
        GROUP_MEMBER_ATTR=Config("group_member_attr",
                                 default="member",
                                 help=_("The LDAP attribute which specifies the "
                                      "members of a group.")),
      ))))


OAUTH = ConfigSection(
  key='oauth',
  help=_('Configuration options for Oauth 1.0 authentication'),
  members=dict(
    CONSUMER_KEY = Config(
      key="consumer_key",
      help=_("The Consumer key of the application."),
      type=str,
      default="XXXXXXXXXXXXXXXXXXXXX"
    ),

    CONSUMER_SECRET = Config(
      key="consumer_secret",
      help=_("The Consumer secret of the application."),
      type=str,
      default="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ),

    REQUEST_TOKEN_URL = Config(
      key="request_token_url",
      help=_("The Request token URL."),
      type=str,
      default="https://api.twitter.com/oauth/request_token"
    ),

    ACCESS_TOKEN_URL = Config(
      key="access_token_url",
      help=_("The Access token URL."),
      type=str,
      default="https://api.twitter.com/oauth/access_token"
    ),

    AUTHENTICATE_URL = Config(
      key="authenticate_url",
      help=_("The Authorize URL."),
      type=str,
      default="https://api.twitter.com/oauth/authorize"
    ),

  )
)


LOCAL_FILESYSTEMS = UnspecifiedConfigSection(
  key="local_filesystems",
  help=_("Paths on the local file system that users should be able to browse."),
  each=ConfigSection(
    members=dict(
      PATH=Config("path",
                  required=True,
                  help=_("The path on the local filesystem.")))))


def default_feedback_url():
  """A version-specific URL."""
  return "http://groups.google.com/a/cloudera.org/group/hue-user"

FEEDBACK_URL = Config(
  key="feedback_url",
  help=_("Link for 'feedback' tab."),
  type=str,
  dynamic_default=default_feedback_url
)

SEND_DBUG_MESSAGES = Config(
  key="send_dbug_messages",
  help=_("Whether to send debug messages from JavaScript to the server logs."),
  type=coerce_bool,
  default=False
)

DATABASE_LOGGING = Config(
  key="database_logging",
  help=_("Enable or disable database debug mode."),
  type=coerce_bool,
  default=False
)

DJANGO_ADMINS = UnspecifiedConfigSection(
  key="django_admins",
  help=_("Administrators that should receive error emails."),
  each=ConfigSection(
    members=dict(
      NAME=Config("name",
                  required=True,
                  help=_("The full name of the admin.")),
      EMAIL=Config("email",
                   required=True,
                   help=_("The email address of the admin.")))))

DJANGO_DEBUG_MODE = Config(
  key="django_debug_mode",
  help=_("Enable or disable Django debug mode."),
  type=coerce_bool,
  default=True
)

HTTP_500_DEBUG_MODE = Config(
  key='http_500_debug_mode',
  help=_('Enable or disable debugging information in the 500 internal server error response. '
       'Note that the debugging information may contain sensitive data. '
       'If django_debug_mode is True, this is automatically enabled.'),
  type=coerce_bool,
  default=True
)

MEMORY_PROFILER = Config(
  key='memory_profiler',
  help=_('Enable or disable memory profiling.'),
  type=coerce_bool,
  default=False)


AUDIT_EVENT_LOG_DIR = Config(
  key="audit_event_log_dir",
  help=_("The directory where to store the auditing logs. Auditing is disable if the value is empty."),
  type=str,
  dynamic_default=get_navigator_audit_log_dir
)

AUDIT_LOG_MAX_FILE_SIZE = Config(
  key="audit_log_max_file_size",
  help=_("Size in KB/MB/GB for audit log to rollover."),
  type=str,
  dynamic_default=get_navigator_audit_max_file_size
)

DJANGO_SERVER_EMAIL = Config(
  key='django_server_email',
  help=_('Email address that internal error messages should send as.'),
  default='hue@localhost.localdomain'
)

DJANGO_EMAIL_BACKEND = Config(
  key="django_email_backend",
  help=_("The email backend to use."),
  type=str,
  default="django.core.mail.backends.smtp.EmailBackend"
)

USE_NEW_AUTOCOMPLETER = Config( # To remove when it's working properly, not supported by old editor
  key='use_new_autocompleter',
  default=True,
  type=coerce_bool,
  help=_('Enable the new editor SQL autocompleter')
)

EDITOR_AUTOCOMPLETE_TIMEOUT = Config(
  key='editor_autocomplete_timeout',
  type=int,
  default=5000,
  help=_('Timeout value in ms for autocomplete of columns, tables, values etc. 0 = disabled')
)

USE_NEW_EDITOR = Config( # To remove in Hue 4
  key='use_new_editor',
  default=True,
  type=coerce_bool,
  help=_('Choose whether to show the new SQL editor.')
)

USE_NEW_SIDE_PANELS = Config( # To remove in Hue 4
  key='use_new_side_panels',
  default=False,
  type=coerce_bool,
  help=_('Choose whether to show extended left and right panels.')
)

USE_DEFAULT_CONFIGURATION = Config(
  key='use_default_configuration',
  default=False,
  type=coerce_bool,
  help=_('Enable saved default configurations for Hive, Impala, Spark, and Oozie.')
)

IS_HUE_4 = Config( # To remove in Hue 5
  key='is_hue_4',
  default=False,
  type=coerce_bool,
  help=_('Choose whether to enable the new interface.')
)


def validate_ldap(user, config):
  res = []

  if config.SEARCH_BIND_AUTHENTICATION.get():
    if config.LDAP_URL.get() is not None:
      bind_dn = config.BIND_DN.get()
      bind_password = get_ldap_bind_password(config)

      if bool(bind_dn) != bool(bind_password):
        if bind_dn == None:
          res.append((LDAP.BIND_DN,
                    unicode(_("If you set bind_password, then you must set bind_dn."))))
        else:
          res.append((LDAP.BIND_PASSWORD,
                      unicode(_("If you set bind_dn, then you must set bind_password."))))
  else:
    if config.NT_DOMAIN.get() is not None or \
        config.LDAP_USERNAME_PATTERN.get() is not None:
      if config.LDAP_URL.get() is None:
        res.append((config.LDAP_URL,
                    unicode(_("LDAP is only partially configured. An LDAP URL must be provided."))))

    if config.LDAP_URL.get() is not None:
      if config.NT_DOMAIN.get() is None and \
          config.LDAP_USERNAME_PATTERN.get() is None:
        res.append((config.LDAP_URL,
                    unicode(_("LDAP is only partially configured. An NT Domain or username "
                    "search pattern must be provided."))))

    if config.LDAP_USERNAME_PATTERN.get() is not None and \
        '<username>' not in config.LDAP_USERNAME_PATTERN.get():
        res.append((config.LDAP_USERNAME_PATTERN,
                   unicode(_("The LDAP username pattern should contain the special"
                   "<username> replacement string for authentication."))))

  return res

def validate_database():

  from django.db import connection

  res = []

  if connection.vendor == 'mysql':
      cursor = connection.cursor();

      try:
        innodb_table_count = cursor.execute('''
            SELECT *
            FROM information_schema.tables
            WHERE table_schema=DATABASE() AND engine = "innodb"''')

        total_table_count = cursor.execute('''
            SELECT *
            FROM information_schema.tables
            WHERE table_schema=DATABASE()''')

        # Promote InnoDB storage engine
        if innodb_table_count != total_table_count:
          res.append(('PREFERRED_STORAGE_ENGINE', unicode(_('''We recommend MySQL InnoDB engine over
                                                        MyISAM which does not support transactions.'''))))

        if innodb_table_count != 0 and innodb_table_count != total_table_count:
          res.append(('MYSQL_STORAGE_ENGINE', unicode(_('''All tables in the database must be of the same
                                                        storage engine type (preferably InnoDB).'''))))
      except Exception, ex:
        LOG.exception("Error in config validation of MYSQL_STORAGE_ENGINE: %s", ex)
  elif 'sqlite' in connection.vendor:
    res.append(('SQLITE_NOT_FOR_PRODUCTION_USE', unicode(_('SQLite is only recommended for development environments. '
        'It might cause the "Database is locked" error. Migrating to MySQL, Oracle or PostgreSQL is strongly recommended.'))))
  return res


def config_validator(user):
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from desktop.lib import i18n

  res = []
  if not get_secret_key():
    res.append((SECRET_KEY, unicode(_("Secret key should be configured as a random string. All sessions will be lost on restart"))))

  # Validate SSL setup
  if SSL_CERTIFICATE.get():
    res.extend(validate_path(SSL_CERTIFICATE, is_dir=False))
    if not SSL_PRIVATE_KEY.get():
      res.append((SSL_PRIVATE_KEY, unicode(_("SSL private key file should be set to enable HTTPS."))))
    else:
      res.extend(validate_path(SSL_PRIVATE_KEY, is_dir=False))

  # Validate encoding
  if not i18n.validate_encoding(DEFAULT_SITE_ENCODING.get()):
    res.append((DEFAULT_SITE_ENCODING, unicode(_("Encoding not supported."))))

  # Validate kerberos
  if KERBEROS.HUE_KEYTAB.get() is not None:
    res.extend(validate_path(KERBEROS.HUE_KEYTAB, is_dir=False))
    # Keytab should not be world or group accessible
    kt_stat = os.stat(KERBEROS.HUE_KEYTAB.get())
    if stat.S_IMODE(kt_stat.st_mode) & 0077:
      res.append((KERBEROS.HUE_KEYTAB,
                  force_unicode(_("Keytab should have 0600 permissions (has %o).") %
                  stat.S_IMODE(kt_stat.st_mode))))

    res.extend(validate_path(KERBEROS.KINIT_PATH, is_dir=False))
    res.extend(validate_path(KERBEROS.CCACHE_PATH, is_dir=False))

  if LDAP.LDAP_SERVERS.get():
    for ldap_record_key in LDAP.LDAP_SERVERS.get():
      res.extend(validate_ldap(user, LDAP.LDAP_SERVERS.get()[ldap_record_key]))
  else:
    res.extend(validate_ldap(user, LDAP))

  # Validate MYSQL storage engine of all tables
  res.extend(validate_database())

  # Validate if oozie email server is active
  from oozie.views.editor2 import _is_oozie_mail_enabled

  if not _is_oozie_mail_enabled(user):
    res.append(('OOZIE_EMAIL_SERVER', unicode(_('Email notifications is disabled for Workflows and Jobs as SMTP server is localhost.'))))

  return res

def get_redaction_policy():
  """
  Return the configured redaction policy.
  """

  return LOG_REDACTION_FILE.get()


def get_secret_key():
  secret_key = os.environ.get('HUE_SECRET_KEY')
  if secret_key is not None:
    return secret_key

  secret_key = SECRET_KEY.get()
  if not secret_key:
    secret_key = SECRET_KEY_SCRIPT.get()

  return secret_key


def get_ssl_password():
  password = os.environ.get('HUE_SSL_PASSWORD')
  if password is not None:
    return password

  password = SSL_PASSWORD.get()
  if not password:
    password = SSL_PASSWORD_SCRIPT.get()

  return password


def get_database_password():
  password = os.environ.get('HUE_DATABASE_PASSWORD')
  if password is not None:
    return password

  password = DATABASE.PASSWORD.get()
  if not password:
    password = DATABASE.PASSWORD_SCRIPT.get()

  return password


def get_smtp_password():
  password = os.environ.get('HUE_SMTP_PASSWORD')
  if password is not None:
    return password

  password = SMTP.PASSWORD.get()
  if not password:
    password = SMTP.PASSWORD_SCRIPT.get()

  return password


def get_ldap_bind_password(ldap_config):
  password = os.environ.get('HUE_LDAP_BIND_PASSWORD')
  if password is not None:
    return password

  password = ldap_config.BIND_PASSWORD.get()
  if not password:
    password = ldap_config.BIND_PASSWORD_SCRIPT.get()

  return password
