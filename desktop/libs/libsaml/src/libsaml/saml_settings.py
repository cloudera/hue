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

import saml2
import desktop.conf
import libsaml.conf

from desktop.lib import security_util


__all__ = ['SAML_CONFIG', 'SAML_ATTRIBUTE_MAPPING', 'SAML_CREATE_UNKNOWN_USER']


BASE_URL = "%(protocol)s%(host)s:%(port)d" % {
  'protocol': desktop.conf.is_https_enabled() and 'https://' or 'http://',
  'host':  desktop.conf.HTTP_HOST.get() == '0.0.0.0' and security_util.get_localhost_name() or desktop.conf.HTTP_HOST.get(),
  'port':  desktop.conf.HTTP_PORT.get()
}

ENTITY_ID = libsaml.conf.ENTITY_ID.get().replace('<base_url>', BASE_URL)


SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': libsaml.conf.XMLSEC_BINARY.get(),

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': ENTITY_ID,

  # directory with attribute mapping
  'attribute_map_dir': libsaml.conf.ATTRIBUTE_MAP_DIR.get(),

  # this block states what services we provide
  'service': {
    'sp' : {
      'name': 'hue',
      'name_id_format': libsaml.conf.NAME_ID_FORMAT.get(),
      'endpoints': {
        # url and binding to the assetion consumer service view
        # do not change the binding or service name
        'assertion_consumer_service': [
          ("%s/saml2/acs/" % BASE_URL, saml2.BINDING_HTTP_POST),
        ],
        # url and binding to the logout service view
        # do not change the binding or service name
        'single_logout_service': [
          ("%s/saml2/ls/" % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
          ("%s/saml2/ls/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
        ],
      },

      'allow_unsolicited': str(libsaml.conf.ALLOW_UNSOLICITED.get()).lower(),

      # attributes that this project need to identify a user
      'required_attributes': libsaml.conf.REQUIRED_ATTRIBUTES.get(),

      # attributes that may be useful to have but not required
      'optional_attributes': libsaml.conf.OPTIONAL_ATTRIBUTES.get(),

      'logout_requests_signed': str(libsaml.conf.LOGOUT_REQUESTS_SIGNED.get()).lower(),
      'authn_requests_signed': str(libsaml.conf.AUTHN_REQUESTS_SIGNED.get()).lower()
    },
  },

  # where the remote metadata is stored
  'metadata': {
    'local': [ libsaml.conf.METADATA_FILE.get() ],
  },

  # set to 1 to output debugging information
  'debug': 1,

  # certificate
  'key_file': libsaml.conf.KEY_FILE.get(),
  'cert_file': libsaml.conf.CERT_FILE.get()
}

SAML_ATTRIBUTE_MAPPING = libsaml.conf.USER_ATTRIBUTE_MAPPING.get()
SAML_CREATE_UNKNOWN_USER = libsaml.conf.CREATE_USERS_ON_LOGIN.get()

if libsaml.conf.USERNAME_SOURCE.get() == 'nameid':
  SAML_USE_NAME_ID_AS_USERNAME = True
