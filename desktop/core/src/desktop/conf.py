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
"""General configuration for core Desktop features (authentication, etc)"""

from desktop import appmanager
from desktop.lib.conf import Config, ConfigSection, UnspecifiedConfigSection
from desktop.lib.conf import coerce_bool, validate_path
from desktop.lib.paths import get_desktop_root
import os
import socket
import stat
from django.utils.translation import ugettext_lazy as _

USE_CHERRYPY_SERVER = Config(
  key="use_cherrypy_server",
  help=_("If set to true, CherryPy will be used. Otherwise, Spawning will be used as the webserver."),
  type=coerce_bool,
  default=False)

HTTP_HOST = Config(
  key="http_host",
  help=_("HTTP Host to bind to."),
  type=str,
  default="0.0.0.0")
HTTP_PORT = Config(
  key="http_port",
  help=_("HTTP Port to bind to."),
  type=int,
  default=8888)
SSL_CERTIFICATE = Config(
  key="ssl_certificate",
  help=_("Filename of SSL Certificate"),
  default=None)
SSL_PRIVATE_KEY = Config(
  key="ssl_private_key",
  help=_("Filename of SSL RSA Private Key"),
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
  default=10)
SECRET_KEY = Config(
  key="secret_key",
  help=_("Used in hashing algorithms for sessions."),
  default="")

USER_ACCESS_HISTORY_SIZE = Config(
  key="user_access_history_size",
  help=_("Number of user access to remember per view per user."),
  type=int,
  default=10)

def is_https_enabled():
  return bool(SSL_CERTIFICATE.get() and SSL_PRIVATE_KEY.get())

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
    except:
      fqdn = 'localhost'
    _default_from_email = "hue@" + fqdn
  return _default_from_email


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
      help=_("The SMTP server port"),
      type=int,
      default=25
    ),

    USER = Config(
      key="user",
      help=_("The username for the SMTP host"),
      type=str,
      default=""
    ),

    PASSWORD = Config(
      key="password",
      help=_("The password for the SMTP user"),
      type=str,
      default=""
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

DATABASE = ConfigSection(
  key='database',
  help=_("""Configuration options for specifying the Desktop Database.
          For more info, see http://docs.djangoproject.com/en/1.1/ref/settings/#database-engine"""),
  members=dict(
    ENGINE=Config(
      key='engine',
      help=_('Database engine, such as postgresql, mysql, sqlite3, or Oracle.'),
      type=str,
      default='sqlite3',
    ),
    NAME=Config(
      key='name',
      help=_('Database name, or path to DB if using sqlite3.'),
      type=str,
      default=get_desktop_root('desktop.db'),
    ),
    USER=Config(
      key='user',
      help=_('Database username'),
      type=str,
      default='',
    ),
    PASSWORD=Config(
      key='password',
      help=_('Database password'),
      type=str,
      default='',
    ),
    HOST=Config(
      key='host',
      help=_('Database host'),
      type=str,
      default='',
    ),
    PORT=Config(
      key='port',
      help=_('Database port'),
      type=int,
      default=0,
    ),
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
      help=_("Path to keep Kerberos credentials cached"),
      private=True,
      type=str,
      default="/tmp/hue_krb5_ccache",
    ),
    KINIT_PATH=Config(
      key='kinit_path',
      help=_("Path to Kerberos 'kinit' command"),
      type=str,
      default="kinit", # use PATH!
    )
  )
)

# See python's documentation for time.tzset for valid values.
TIME_ZONE = Config(
  key="time_zone",
  help=_("Time zone name"),
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
  help=_("Username to run servers as"),
  type=str,
  default="hue")
SERVER_GROUP = Config(
  key="server_group",
  help=_("Group to run servers as"),
  type=str,
  default="hue")


CUSTOM = ConfigSection(
  key="custom",
  help=_("Customizations to the UI."),
  members=dict(
    BANNER_TOP_HTML=Config("banner_top_html",
                   default="",
                   help=_("Top banner HTML code. This code will be placed in the navigation bar "
                        "so that it will reside at the top of the page in a fixed position. " +
                        "One common value is `<img src=\"http://www.example.com/example.gif\" />`")),
))

AUTH = ConfigSection(
  key="auth",
  help=_("Configuration options for user authentication into the web application."),
  members=dict(
    BACKEND=Config("backend",
                   default="desktop.auth.backend.AllowFirstUserDjangoBackend",
                   help=_("Authentication backend.  Common settings are "
                        "django.contrib.auth.backends.ModelBackend (fully Django backend), " + 
                        "desktop.auth.backend.AllowAllBackend (allows everyone), " +
                        "desktop.auth.backend.AllowFirstUserDjangoBackend (relies on Django and user manager, after the first login). ")),
    USER_AUGMENTOR=Config("user_augmentor",
                   default="desktop.auth.backend.DefaultUserAugmentor",
                   help=_("Class which defines extra accessor methods for User objects.")),
    PAM_SERVICE=Config("pam_service",
                  default="login",
                  help=_("The service to use when querying PAM."
                         "The service usually corresponds to a single filename in /etc/pam.d"))
))

LDAP = ConfigSection(
  key="ldap",
  help=_("Configuration options for LDAP connectivity"),
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
    LDAP_CERT=Config("ldap_cert",
                     default=None,
                     help=_("The LDAP certificate for authentication over TLS.")),
    LDAP_USERNAME_PATTERN=Config("ldap_username_pattern",
                                 default=None,
                                 help=_("A pattern to use for constructing LDAP usernames.")),
    BIND_DN=Config("bind_dn",
                   default=None,
                   help=_("The distinguished name to bind as, when importing from LDAP.")),
    BIND_PASSWORD=Config("bind_password",
                   default=None,
                   help=_("The password for the bind user.")),

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
      help=_("Configuration for LDAP group schema and search"),
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
      )
    ),
))



LOCAL_FILESYSTEMS = UnspecifiedConfigSection(
  key="local_filesystems",
  help=_("Paths on the local file system that users should be able to browse."),
  each=ConfigSection(
    members=dict(
      PATH=Config("path",
                  required=True,
                  help=_("The path on the local FS.")))))

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
  help=_("If true, log all database requests."),
  type=coerce_bool,
  default=False)

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

DJANGO_SERVER_EMAIL = Config(
  key='django_server_email',
  help=_('Email address that internal error messages should send as.'),
  default='hue@localhost.localdomain'
)

DJANGO_EMAIL_BACKEND = Config(
  key="django_email_backend",
  help=_("The Email backend to use."),
  type=str,
  default="django.core.mail.backends.smtp.EmailBackend"
)


def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from desktop.lib import i18n

  res = [ ]
  if not SECRET_KEY.get():
    res.append((SECRET_KEY, unicode(_("Secret key should be configured as a random string."))))

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
                  unicode(_("Keytab should have 0600 permissions (has %o).") %
                  stat.S_IMODE(kt_stat.st_mode))))

    res.extend(validate_path(KERBEROS.KINIT_PATH, is_dir=False))
    res.extend(validate_path(KERBEROS.CCACHE_PATH, is_dir=False))

  if LDAP.NT_DOMAIN.get() is not None or \
      LDAP.LDAP_USERNAME_PATTERN.get() is not None:
    if LDAP.LDAP_URL.get() is None:
      res.append((LDAP.LDAP_URL,
                  unicode(_("LDAP is only partially configured. An LDAP URL must be provided."))))

  if LDAP.LDAP_URL.get() is not None:
    if LDAP.NT_DOMAIN.get() is None and \
        LDAP.LDAP_USERNAME_PATTERN.get() is None:
      res.append(LDAP.LDAP_URL,
                  unicode(_("LDAP is only partially configured. An NT Domain or username "
                  "search pattern must be provided.")))

  if LDAP.LDAP_USERNAME_PATTERN.get() is not None and \
      '<username>' not in LDAP.LDAP_USERNAME_PATTERN.get():
      res.append(LDAP.LDAP_USERNAME_PATTERN,
                 unicode(_("The LDAP username pattern should contain the special"
                 "<username> replacement string for authentication.")))


  return res
