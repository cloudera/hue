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
import huesaml.conf

__all__ = ['SAML_CONFIG', 'SAML_ATTRIBUTE_MAPPING', 'SAML_CREATE_UNKNOWN_USER']


SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': huesaml.conf.XMLSEC_BINARY.get(),

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': huesaml.conf.ENTITY_ID.get(),

  # directory with attribute mapping
  'attribute_map_dir': huesaml.conf.ATTRIBUTE_MAP_DIR.get(),

  # this block states what services we provide
  'service': {
    'sp' : {
      'name': 'example',
      'endpoints': {
        # url and binding to the assetion consumer service view
        # do not change the binding or service name
        'assertion_consumer_service': [
          (huesaml.conf.ASSERTION_CONSUMER_SERVICE_URI.get(), saml2.BINDING_HTTP_POST),
        ],
        # url and binding to the single logout service view
        # do not change the binding or service name
        'single_logout_service': [
          (huesaml.conf.SINGLE_LOGOUT_SERVICE_URI.get(), saml2.BINDING_HTTP_REDIRECT),
        ],
      },

      'allow_unsolicited': huesaml.conf.ALLOW_UNSOLICITED.get(),

      # attributes that this project need to identify a user
      'required_attributes': huesaml.conf.REQUIRED_ATTRIBUTES.get(),

      # attributes that may be useful to have but not required
      'optional_attributes': huesaml.conf.OPTIONAL_ATTRIBUTES.get(),
    },
  },

  # where the remote metadata is stored
  'metadata': {
    'local': huesaml.conf.METADATA_FILE.get(),
  },

  # set to 1 to output debugging information
  'debug': 1,

  # certificate
  'key_file': huesaml.conf.KEY_FILE.get(),
  'cert_file': huesaml.conf.CERT_FILE.get()
}

SAML_ATTRIBUTE_MAPPING = huesaml.conf.USER_ATTRIBUTE_MAPPING.get()
SAML_CREATE_UNKNOWN_USER = huesaml.conf.CREATE_USERS_ON_LOGIN.get()