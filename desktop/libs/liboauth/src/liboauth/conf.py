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

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import Config, coerce_bool, coerce_csv, coerce_json_dict


CONSUMER_KEY_TWITTER = Config(
      key="consumer_key_twitter",
      help=_t("The Consumer key of the twitter application."),
      type=str,
      default=""
    )
CONSUMER_KEY_GOOGLE = Config(
      key="consumer_key_google",
      help=_t("The Consumer key of the google application."),
      type=str,
      default=""
    )
CONSUMER_KEY_FACEBOOK = Config(
      key="consumer_key_facebook",
      help=_t("The Consumer key of the facebook application."),
      type=str,
      default=""
    )
CONSUMER_KEY_LINKEDIN = Config(
      key="consumer_key_linkedin",
      help=_t("The Consumer key of the linkedin application."),
      type=str,
      default=""
    )

CONSUMER_SECRET_TWITTER = Config(
      key="consumer_secret_twitter",
      help=_t("The Consumer secret of the twitter application."),
      type=str,
      default=""
    )
CONSUMER_SECRET_GOOGLE = Config(
      key="consumer_secret_google",
      help=_t("The Consumer secret of the google application."),
      type=str,
      default=""
    )
CONSUMER_SECRET_FACEBOOK = Config(
      key="consumer_secret_facebook",
      help=_t("The Consumer secret of the facebook application."),
      type=str,
      default=""
    )
CONSUMER_SECRET_LINKEDIN = Config(
      key="consumer_secret_linkedin",
      help=_t("The Consumer secret of the linkedin application."),
      type=str,
      default=""
    )


REQUEST_TOKEN_URL_TWITTER = Config(
      key="request_token_url_twitter",
      help=_t("The Twitter Request token URL."),
      type=str,
      default="https://api.twitter.com/oauth/request_token"
    )
REQUEST_TOKEN_URL_GOOGLE = Config(
      key="request_token_url_google",
      help=_t("The Google Request token URL."),
      type=str,
      default="https://accounts.google.com/o/oauth2/auth"
    )
REQUEST_TOKEN_URL_FACEBOOK = Config(
      key="request_token_url_facebook",
      help=_t("The Facebook Request token URL."),
      type=str,
      default="https://graph.facebook.com/oauth/authorize"
    )
REQUEST_TOKEN_URL_LINKEDIN = Config(
      key="request_token_url_linkedin",
      help=_t("The Linkedin Request token URL."),
      type=str,
      default="https://www.linkedin.com/uas/oauth2/authorization"
    )

ACCESS_TOKEN_URL_TWITTER = Config(
      key="access_token_url_twitter",
      help=_t("The Twitter Access token URL."),
      type=str,
      default="https://api.twitter.com/oauth/access_token"
    )
ACCESS_TOKEN_URL_GOOGLE = Config(
      key="access_token_url_google",
      help=_t("The Google Access token URL."),
      type=str,
      default="https://accounts.google.com/o/oauth2/token"
    )
ACCESS_TOKEN_URL_FACEBOOK = Config(
      key="access_token_url_facebook",
      help=_t("The Facebook Access token URL."),
      type=str,
      default="https://graph.facebook.com/oauth/access_token"
    )
ACCESS_TOKEN_URL_LINKEDIN = Config(
      key="access_token_url_linkedin",
      help=_t("The Linkedin Access token URL."),
      type=str,
      default="https://api.linkedin.com/uas/oauth2/accessToken"
    )


AUTHORIZE_URL_TWITTER = Config(
      key="authenticate_url_twitter",
      help=_t("The Twitter Authorize URL."),
      type=str,
      default="https://api.twitter.com/oauth/authorize"
    )
AUTHORIZE_URL_GOOGLE = Config(
      key="authenticate_url_google",
      help=_t("The Google Authorize URL."),
      type=str,
      default="https://www.googleapis.com/oauth2/v1/userinfo"
    )
AUTHORIZE_URL_FACEBOOK = Config(
      key="authenticate_url_facebook",
      help=_t("The Facebook Authorize URL."),
      type=str,
      default="https://graph.facebook.com/me"
    )
AUTHORIZE_URL_LINKEDIN = Config(
      key="authenticate_url_linkedin",
      help=_t("The Linkedin Authorize URL."),
      type=str,
      default="https://api.linkedin.com/v1/people/~"
    )

WHITELISTED_DOMAINS_GOOGLE = Config(
    key="whitelisted_domains_google",
    help=_t("Comma-separated list of whitelisted domains."),
    type=coerce_csv,
    default=''
)

USERNAME_MAP = Config(
    key="username_map",
    help=_t('JSON formatted hash of username simplifications. '
        'Example: {"@sub1.domain.com":"_S1", "@sub2.domain.com":"_S2"} '
        'converts "email@sub1.domain.com" to "email_S1"'),
    type=coerce_json_dict,
    default='{}'
)

