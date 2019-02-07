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

import json
import os
import subprocess

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import Config, coerce_bool, coerce_csv, coerce_password_from_script


BASEDIR = os.path.dirname(os.path.abspath(__file__))

USERNAME_SOURCES = ('attributes', 'nameid')


def xmlsec():
  """
  xmlsec path
  """
  try:
    proc = subprocess.Popen(['which', 'xmlsec1'], stdout=subprocess.PIPE)
    return proc.stdout.read().strip()
  except subprocess.CalledProcessError:
    return '/usr/local/bin/xmlsec1'


def dict_list_map(value):
  if isinstance(value, str):
    d = {}
    for k, v in json.loads(value).iteritems():
      d[k] = (v,)
    return d
  elif isinstance(value, dict):
    return value
  return None


XMLSEC_BINARY = Config(
  key="xmlsec_binary",
  dynamic_default=xmlsec,
  type=str,
  help=_t("Xmlsec1 binary path. This program should be executable by the user running Hue."))

BASE_URL = Config(
  key="base_url",
  default=None,
  type=str,
  help=_t("Optional base url the SAML IdP should use for responses."))

ENTITY_ID = Config(
  key="entity_id",
  default="<base_url>/saml2/metadata/",
  type=str,
  help=_t("Entity ID for Hue acting as service provider. Can also accept a pattern where '<base_url>' will be replaced with server URL base."))

CREATE_USERS_ON_LOGIN = Config(
  key="create_users_on_login",
  default=True,
  type=coerce_bool,
  help=_t("Create users from IdP on login."))

ATTRIBUTE_MAP_DIR = Config(
  key="attribute_map_dir",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'attribute-maps') ),
  type=str,
  private=True,
  help=_t("Attribute map directory contains files that map SAML attributes to pysaml2 attributes."))

ALLOW_UNSOLICITED = Config(
  key="allow_unsolicited",
  default=True,
  type=coerce_bool,
  private=True,
  help=_t("Allow responses that are initiated by the IdP."))

REQUIRED_ATTRIBUTES = Config(
  key="required_attributes",
  default=['uid'],
  type=coerce_csv,
  help=_t("Required attributes to ask for from IdP."))

OPTIONAL_ATTRIBUTES = Config(
  key="optional_attributes",
  default=[],
  type=coerce_csv,
  help=_t("Optional attributes to ask for from IdP."))

METADATA_FILE = Config(
  key="metadata_file",
  default=os.path.abspath( os.path.join(BASEDIR, '..', '..', 'examples', 'idp.xml') ),
  type=str,
  help=_t("IdP metadata in the form of a file. This is generally an XML file containing metadata that the Identity Provider generates."))

KEY_FILE = Config(
  key="key_file",
  default="",
  type=str,
  help=_t("key_file is the name of a PEM formatted file that contains the private key of the Hue service. This is presently used both to encrypt/sign assertions and as client key in a HTTPS session."))

KEY_FILE_PASSWORD = Config(
  key="key_file_password",
  help=_t("key_file_password password of the private key"),
  default=None)

KEY_FILE_PASSWORD_SCRIPT = Config(
  key="key_file_password_script",
  help=_t("Execute this script to produce the private key password. This will be used when `key_file_password` is not set."),
  type=coerce_password_from_script,
  default=None)

CERT_FILE = Config(
  key="cert_file",
  default="",
  type=str,
  help=_t("This is the public part of the service private/public key pair. cert_file must be a PEM formatted certificate chain file."))

USER_ATTRIBUTE_MAPPING = Config(
  key="user_attribute_mapping",
  default={'uid': ('username', )},
  type=dict_list_map,
  help=_t("A mapping from attributes in the response from the IdP to django user attributes."))

AUTHN_REQUESTS_SIGNED = Config(
  key="authn_requests_signed",
  default=False,
  type=coerce_bool,
  help=_t("Have Hue initiated authn requests be signed and provide a certificate."))

WANT_RESPONSE_SIGNED = Config(
  key="want_response_signed",
  default=True,
  type=coerce_bool,
  help=_t("Have Hue initiated authn response be signed."))

WANT_ASSERTIONS_SIGNED = Config(
  key="want_assertions_signed",
  default=True,
  type=coerce_bool,
  help=_t("Have Hue initiated authn assertions response be signed."))

LOGOUT_REQUESTS_SIGNED = Config(
  key="logout_requests_signed",
  default=False,
  type=coerce_bool,
  help=_t("Have Hue initiated logout requests be signed and provide a certificate."))

USERNAME_SOURCE = Config(
  key="username_source",
  default="attributes",
  type=str,
  help=_t("Username can be sourced from 'attributes' or 'nameid'"))

LOGOUT_ENABLED = Config(
  key="logout_enabled",
  default=True,
  type=coerce_bool,
  help=_t("Performs the logout or not."))

NAME_ID_FORMAT = Config(
  key="name_id_format",
  default="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
  type=str,
  help=_t("Request this NameID format from the server"))

def get_key_file_password():
  password = os.environ.get('HUE_SAML_KEY_FILE_PASSWORD')
  if password is not None:
    return password

  password = KEY_FILE_PASSWORD.get()
  if not password:
    password = KEY_FILE_PASSWORD_SCRIPT.get()

  return password

def config_validator(user):
  res = []
  if USERNAME_SOURCE.get() not in USERNAME_SOURCES:
    res.append(("libsaml.username_source", _("username_source not configured properly. SAML integration may not work.")))
  return res
