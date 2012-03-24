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

USE_CHERRYPY_SERVER = Config(
  key="use_cherrypy_server",
  help="If set to true, CherryPy will be used. Otherwise, Spawning will be used as the webserver.",
  type=coerce_bool,
  default=False)

HTTP_HOST = Config(
  key="http_host",
  help="HTTP Host to bind to",
  type=str,
  default="0.0.0.0")
HTTP_PORT = Config(
  key="http_port",
  help="HTTP Port to bind to",
  type=int,
  default=8888)
SSL_CERTIFICATE = Config(
  key="ssl_certificate",
  help="Filename of SSL Certificate",
  default=None)
SSL_PRIVATE_KEY = Config(
  key="ssl_private_key",
  help="Filename of SSL RSA Private Key",
  default=None)
ENABLE_SERVER = Config(
  key="enable_server",
  help="If set to false, runcpserver will not actually start the web server.  Used if Apache is being used as a WSGI container.",
  type=coerce_bool,
  default=True)
CHERRYPY_SERVER_THREADS = Config(
  key="cherrypy_server_threads",
  help="Number of threads used by the CherryPy web server.",
  type=int,
  default=10)
SECRET_KEY = Config(
  key="secret_key",
  help="Used in hashing algorithms for sessions.",
  default="")

USER_ACCESS_HISTORY_SIZE = Config(
  key="user_access_history_size",
  help="Number of user access to remember per view per user.",
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
  help='Configuration options for connecting to an external SMTP server',
  members=dict(
    HOST = Config(
      key="host",
      help="The SMTP server for email notification delivery",
      type=str,
      default="localhost"
    ),

    PORT = Config(
      key="port",
      help="The SMTP server port",
      type=int,
      default=25
    ),

    USER = Config(
      key="user",
      help="The username for the SMTP host",
      type=str,
      default=""
    ),

    PASSWORD = Config(
      key="password",
      help="The password for the SMTP user",
      type=str,
      default=""
    ),

    USE_TLS = Config(
      key="tls",
      help="Whether to use a TLS (secure) connection when talking to the SMTP server",
      type=coerce_bool,
      default=False
    ),

    DEFAULT_FROM= Config(
      key="default_from_email",
      help="Default email address to use for various automated notification from Hue",
      type=str,
      dynamic_default=default_from_email
    ),
  )
)

DATABASE = ConfigSection(
  key='database',
  help="""Configuration options for specifying the Desktop Database.
          For more info, see http://docs.djangoproject.com/en/1.1/ref/settings/#database-engine""",
  members=dict(
    ENGINE=Config(
      key='engine',
      help='Database engine, eg postgresql, mysql, sqlite3, or oracle',
      type=str,
      default='sqlite3',
    ),
    NAME=Config(
      key='name',
      help='Database name, or path to DB if using sqlite3',
      type=str,
      default=get_desktop_root('desktop.db'),
    ),
    USER=Config(
      key='user',
      help='Database username',
      type=str,
      default='',
    ),
    PASSWORD=Config(
      key='password',
      help='Database password',
      type=str,
      default='',
    ),
    HOST=Config(
      key='host',
      help='Database host',
      type=str,
      default='',
    ),
    PORT=Config(
      key='port',
      help='Database port',
      type=int,
      default=0,
    ),
  )
)

KERBEROS = ConfigSection(
  key="kerberos",
  help="""Configuration options for specifying Hue's kerberos integration for
          secured Hadoop clusters.""",
  members=dict(
    HUE_KEYTAB=Config(
      key='hue_keytab',
      help="Path to a Kerberos keytab file containing Hue's service credentials.",
      type=str,
      default=None),
    HUE_PRINCIPAL=Config(
      key='hue_principal',
      help="Kerberos principal name for hue. Typically 'hue/hostname.foo.com'",
      type=str,
      default="hue/%s" % socket.getfqdn()),
    KEYTAB_REINIT_FREQUENCY=Config(
      key='reinit_frequency',
      help="Frequency in seconds with which Hue will renew its keytab",
      type=int,
      default=60*60), #1h
    CCACHE_PATH=Config(
      key='ccache_path',
      help="Path to keep kerberos credentials cached",
      private=True,
      type=str,
      default="/tmp/hue_krb5_ccache",
    ),
    KINIT_PATH=Config(
      key='kinit_path',
      help="Path to kerberos 'kinit' command",
      type=str,
      default="kinit", # use PATH!
    )
  )
)

# See python's documentation for time.tzset for valid values.
TIME_ZONE = Config(
  key="time_zone",
  help="Time zone name",
  type=str,
  default=os.environ.get("TZ", "America/Los_Angeles")
)

DEFAULT_SITE_ENCODING = Config(
  key='default_site_encoding',
  help='Default system-wide unicode encoding',
  type=str,
  default='utf-8'
)

SERVER_USER = Config(
  key="server_user",
  help="Username to run servers as",
  type=str,
  default="hue")
SERVER_GROUP = Config(
  key="server_group",
  help="Group to run servers as",
  type=str,
  default="hue")


AUTH = ConfigSection(
  key="auth",
  help="Configuration options for user authentication into the web application",
  members=dict(
    BACKEND=Config("backend",
                   default="desktop.auth.backend.AllowFirstUserDjangoBackend",
                   help="Authentication backend.  Common settings are "
                        "django.contrib.auth.backends.ModelBackend (fully Django backend), " + 
                        "desktop.auth.backend.AllowAllBackend (allows everyone), " +
                        "desktop.auth.backend.AllowFirstUserDjangoBackend (relies on Django and user manager, after the first login), "),
    USER_AUGMENTOR=Config("user_augmentor",
                   default="desktop.auth.backend.DefaultUserAugmentor",
                   help="Class which defines extra accessor methods for User objects."),
))

LDAP = ConfigSection(
  key="ldap",
  help="Configuration options for LDAP connectivity",
  members=dict(
    BASE_DN=Config("base_dn",
                   default=None,
                   help="The base LDAP distinguished name to use for LDAP search."),
    NT_DOMAIN=Config("nt_domain",
                     default=None,
                     help="The NT domain used for LDAP authentication."),
    LDAP_URL=Config("ldap_url",
                     default=None,
                     help="The LDAP URL to connect to."),
    LDAP_CERT=Config("ldap_cert",
                     default=None,
                     help="The LDAP certificate for authentication over TLS."),
    LDAP_USERNAME_PATTERN=Config("ldap_username_pattern",
                                 default=None,
                                 help="A pattern to use for constructing LDAP usernames."),
    BIND_DN=Config("bind_dn",
                   default=None,
                   help="The distinguished name to bind as, when importing from LDAP."),
    BIND_PASSWORD=Config("bind_password",
                   default=None,
                   help="The password for the bind user."),

    USERS = ConfigSection(
      key="users",
      help="Configuration for LDAP user schema and search",
      members=dict(
        USER_FILTER=Config("user_filter",
                           default="objectclass=*",
                           help="A base filter for use when searching for users."),
        USER_NAME_ATTR=Config("user_name_attr",
                              default="sAMAccountName",
                              help="The username attribute in the LDAP schema. "
                                   "Typically, this is 'sAMAccountName' for AD and 'uid' "
                                   "for other LDAP systems."),
      )
    ),

    GROUPS = ConfigSection(
      key="groups",
      help="Configuration for LDAP group schema and search",
      members=dict(
        GROUP_FILTER=Config("group_filter",
                           default="objectclass=*",
                           help="A base filter for use when searching for groups."),
        GROUP_NAME_ATTR=Config("group_name_attr",
                              default="cn",
                              help="The group name attribute in the LDAP schema. "
                                  "Typically, this is 'cn'."),
        GROUP_MEMBER_ATTR=Config("group_member_attr",
                                 default="member",
                                 help="The LDAP attribute which specifies the "
                                      "members of a group."),
      )
    ),
))



LOCAL_FILESYSTEMS = UnspecifiedConfigSection(
  key="local_filesystems",
  help="Paths on the local file system that users should be able to browse",
  each=ConfigSection(
    members=dict(
      PATH=Config("path",
                  required=True,
                  help="The path on the local FS"))))

def default_feedback_url():
  """A version-specific URL."""
  return "http://groups.google.com/a/cloudera.org/group/hue-user"
  
FEEDBACK_URL = Config(
  key="feedback_url",
  help="Link for 'feedback' tab.",
  type=str,
  dynamic_default=default_feedback_url
)

SEND_DBUG_MESSAGES = Config(
  key="send_dbug_messages",
  help="Whether to send dbug messages from JavaScript to the server logs.",
  type=coerce_bool,
  default=False
)

DATABASE_LOGGING = Config(
  key="database_logging",
  help="If true, log all database requests.",
  type=coerce_bool,
  default=False)

DJANGO_DEBUG_MODE = Config(
  key="django_debug_mode",
  help="Enable or disable django debug mode.",
  type=coerce_bool,
  default=True
)

HTTP_500_DEBUG_MODE = Config(
  key='http_500_debug_mode',
  help='Enable or disable debugging information in the 500 internal server error response. '
       'Note that the debugging information may contain sensitive data. '
       'If django_debug_mode is True, this is automatically enabled.',
  type=coerce_bool,
  default=True
)


def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from desktop.lib import i18n

  res = [ ]
  if not SECRET_KEY.get():
    res.append((SECRET_KEY, "Secret key should be configured as a random string."))

  # Validate SSL setup
  if SSL_CERTIFICATE.get():
    res.extend(validate_path(SSL_CERTIFICATE, is_dir=False))
    if not SSL_PRIVATE_KEY.get():
      res.append((SSL_PRIVATE_KEY, "SSL private key file should be set to enable HTTPS."))
    else:
      res.extend(validate_path(SSL_PRIVATE_KEY, is_dir=False))

  # Validate encoding
  if not i18n.validate_encoding(DEFAULT_SITE_ENCODING.get()):
    res.append((DEFAULT_SITE_ENCODING, "Encoding not supported."))

  # Validate kerberos
  if KERBEROS.HUE_KEYTAB.get() is not None:
    res.extend(validate_path(KERBEROS.HUE_KEYTAB, is_dir=False))
    # Keytab should not be world or group accessible
    kt_stat = os.stat(KERBEROS.HUE_KEYTAB.get())
    if stat.S_IMODE(kt_stat.st_mode) & 0077:
      res.append((KERBEROS.HUE_KEYTAB,
                  "Keytab should have 0600 permissions (has %o)" %
                  stat.S_IMODE(kt_stat.st_mode)))

    res.extend(validate_path(KERBEROS.KINIT_PATH, is_dir=False))
    res.extend(validate_path(KERBEROS.CCACHE_PATH, is_dir=False))

  for broken_app in appmanager.BROKEN_APPS:
    res.append(('Working Hadoop', 'App %s requires Hadoop but Hadoop is not present.' % (broken_app,)))

  if LDAP.NT_DOMAIN.get() is not None or \
      LDAP.LDAP_USERNAME_PATTERN.get() is not None:
    if LDAP.LDAP_URL.get() is None:
      res.append((LDAP.LDAP_URL,
                  "LDAP is only partially configured. An LDAP URL must be provided."))

  if LDAP.LDAP_URL.get() is not None:
    if LDAP.NT_DOMAIN.get() is None and \
        LDAP.LDAP_USERNAME_PATTERN.get() is None:
      res.append(LDAP.LDAP_URL,
                  "LDAP is only partially configured. An NT Domain or username "
                  "search pattern must be provided.")

  if LDAP.LDAP_USERNAME_PATTERN.get() is not None and \
      '<username>' not in LDAP.LDAP_USERNAME_PATTERN.get():
      res.append(LDAP.LDAP_USERNAME_PATTERN,
                 "The LDAP username pattern should contain the special"
                 "<username> replacement string for authentication.")


  return res
