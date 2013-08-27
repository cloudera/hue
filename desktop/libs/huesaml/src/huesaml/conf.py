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

import os

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config, coerce_bool


BASEDIR = os.path.dirname(os.path.abspath(__file__))


def csv(value):
  if isinstance(value, str):
    return value.split(',')
  elif isinstance(value, list):
    return value
  return None

def dict_list_map(value):
  if isinstance(value, str):
    d = json.loads(value)
    return {k:(v,) for k, v in d.iteritems()}
  elif isinstance(value, dict):
    return value
  return None


XMLSEC_BINARY = Config(
  key="xmlsec_binary",
  default="/usr/local/bin/xmlsec1",
  type=str,
  help=_t("Xmlsec1 binary path. This program should be executable by the user running Hue."))

CREATE_USERS_ON_LOGIN = Config(
  key="create_users_on_login",
  default=True,
  type=coerce_bool,
  help=_t("Create users from IdP on login."))

ENTITY_ID = Config(
  key="entity_id",
  default="http://localhost:8888/saml2/metadata/",
  type=str,
  help=_t("Globally unique identifier of the entity."))

ATTRIBUTE_MAP_DIR = Config(
  key="attribute_map_dir",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'attribute-maps') ),
  type=str,
  private=True,
  help=_t("Attribute map directory contains files that map SAML attributes to pysaml2 attributes."))

ASSERTION_CONSUMER_SERVICE_URI = Config(
  key="assertion_consumer_service_uri",
  default="http://localhost:8888/saml2/acs/",
  type=str,
  help=_t("Consumes assertions sent back from IdP."))

SINGLE_LOGOUT_SERVICE = Config(
  key="single_logout_service",
  default="http://localhost:8888/saml2/ls/",
  type=str,
  help=_t("Logout using the IdP."))

ALLOW_UNSOLICITED = Config(
  key="allow_unsolicited",
  default=True,
  type=coerce_bool,
  private=True,
  help=_t("Allow imperfect responses."))

REQUIRED_ATTRIBUTES = Config(
  key="required_attributes",
  default=[],
  type=csv,
  help=_t("Required attributes to ask for from IdP."))

OPTIONAL_ATTRIBUTES = Config(
  key="optional_attributes",
  default=[],
  type=csv,
  help=_t("Optional attributes to ask for from IdP."))

METADATA_FILE = Config(
  key="metadata_file",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'examples', 'idp.xml') ),
  type=str,
  help=_t("IdP metadata in the form of a file. This is generally an XML file containing metadata that the Identity Provider generates."))

KEY_FILE = Config(
  key="key_file",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'examples', 'key.pem') ),
  type=str,
  help=_t("key_file is the name of a PEM formatted file that contains the private key of the Hue service. This is presently used both to encrypt/sign assertions and as client key in a HTTPS session."))

CERT_FILE = Config(
  key="cert_file",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'examples', 'cert.pem') ),
  type=str,
  help=_t("This is the public part of the service private/public key pair. cert_file must be a PEM formatted certificate chain file."))

USER_ATTRIBUTE_MAPPING = Config(
  key="user_attribute_mapping",
  default={'uid': ('username', )},
  type=dict_list_map,
  help=_t("A mapping from attributes in the response from the IdP to django user attributes."))
