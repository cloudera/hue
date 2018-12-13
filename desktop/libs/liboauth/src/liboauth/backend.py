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
"""
See desktop/auth/backend.py
"""

import httplib2
import json
import urllib
import cgi
import logging

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from desktop.auth.backend import force_username_case, DesktopBackendBase
from desktop.conf import AUTH
from useradmin.models import get_profile, get_default_user_group, UserProfile

import liboauth.conf
import liboauth.metrics

try:
  import oauth2 as oauth
except:
  oauth = None


LOG = logging.getLogger(__name__)

class OAuthBackend(DesktopBackendBase):

  @liboauth.metrics.oauth_authentication_time
  def authenticate(self, access_token):
    username = access_token['screen_name']
    password = access_token['oauth_token_secret']

    username = force_username_case(username)

    try:
      if AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist:

      if not UserProfile.objects.filter(creation_method=UserProfile.CreationMethod.EXTERNAL.name).exists():
        is_super = True
      else:
        is_super = False
    
      # Could save oauth_token detail in the user profile here
      user = find_or_create_user(username, password)

      profile = get_profile(user)
      profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
      profile.save()

      user.is_superuser = is_super
      user.save()

      default_group = get_default_user_group()
      if default_group is not None:
        user.groups.add(default_group)

    return user

    
  @classmethod
  def manages_passwords_externally(cls):
    return True 

  @classmethod
  def is_first_login_ever(cls):
    """ Return true if no external user has ever logged in to Desktop yet. """
    return not UserProfile.objects.filter(creation_method=UserProfile.CreationMethod.EXTERNAL.name).exists()
  

  @classmethod
  def handleAuthenticationRequest(cls, request):
    assert oauth is not None
 
    if 'oauth_verifier' in request.GET:
        social = 'twitter'
        consumer_key=liboauth.conf.CONSUMER_KEY_TWITTER.get()
        consumer_secret=liboauth.conf.CONSUMER_SECRET_TWITTER.get()
        access_token_uri=liboauth.conf.ACCESS_TOKEN_URL_TWITTER.get()

        consumer = oauth.Consumer(consumer_key, consumer_secret)
        token = oauth.Token(request.session['request_token']['oauth_token'], request.session['request_token']['oauth_token_secret'])
        client = oauth.Client(consumer, token)
        oauth_verifier=request.GET['oauth_verifier']
        resp, content = client.request(access_token_uri + oauth_verifier, "GET")
        if resp['status'] != '200':
            raise Exception(_("Invalid response from OAuth provider: %s") % resp)
        access_token = dict(cgi.parse_qsl(content))
        access_token['screen_name'] = ''.join([x for x in access_token['screen_name'] if x.isalnum()])

    else:
        parser = httplib2.Http()
        login_failed_url = '/'
        if 'error' in request.GET or 'code' not in request.GET:
            return ""

        redirect_uri = get_redirect_uri(request)
        code = request.GET['code']
        grant_type = 'authorization_code'

        state_split = request.GET['state'].split(',')
        nexturl = state_split[1] if len(state_split) > 1 else '/'
        social = state_split[0]

        if social == 'google':
            consumer_key=liboauth.conf.CONSUMER_KEY_GOOGLE.get()
            consumer_secret=liboauth.conf.CONSUMER_SECRET_GOOGLE.get()
            access_token_uri=liboauth.conf.ACCESS_TOKEN_URL_GOOGLE.get()
            authentication_token_uri=liboauth.conf.AUTHORIZE_URL_GOOGLE.get()        

        elif social == 'facebook':
            consumer_key=liboauth.conf.CONSUMER_KEY_FACEBOOK.get()
            consumer_secret=liboauth.conf.CONSUMER_SECRET_FACEBOOK.get()
            access_token_uri=liboauth.conf.ACCESS_TOKEN_URL_FACEBOOK.get()
            authentication_token_uri=liboauth.conf.AUTHORIZE_URL_FACEBOOK.get()
        
        elif social == 'linkedin':
            consumer_key=liboauth.conf.CONSUMER_KEY_LINKEDIN.get()
            consumer_secret=liboauth.conf.CONSUMER_SECRET_LINKEDIN.get()
            access_token_uri=liboauth.conf.ACCESS_TOKEN_URL_LINKEDIN.get()
            authentication_token_uri=liboauth.conf.AUTHORIZE_URL_LINKEDIN.get()
        
        params = urllib.urlencode({
           'code':code,
           'redirect_uri':redirect_uri,
           'client_id': consumer_key,
           'client_secret': consumer_secret,
           'grant_type':grant_type
        })
        headers={'content-type':'application/x-www-form-urlencoded'}
        resp, cont = parser.request(access_token_uri, method = 'POST', body = params, headers = headers)
        if resp['status'] != '200':
            raise Exception(_("Invalid response from OAuth provider: %s") % resp)

        #google
        if social == 'google':
            access_tok = (json.loads(cont))['access_token']
            auth_token_uri = authentication_token_uri + access_tok
            resp, content = parser.request(auth_token_uri, "GET")
            if resp['status'] != '200':
                raise Exception(_("Invalid response from OAuth provider: %s") % resp)
            username=(json.loads(content))["email"]
            access_token = dict(screen_name=map_username(username), oauth_token_secret=access_tok)
            whitelisted_domains = liboauth.conf.WHITELISTED_DOMAINS_GOOGLE.get()
            if whitelisted_domains:
                if username.split('@')[1] not in whitelisted_domains:
                    access_token = ""
        #facebook
        elif social == 'facebook':
            access_tok = (dict(cgi.parse_qsl(cont)))['access_token']
            auth_token_uri = authentication_token_uri + access_tok
            resp, content = parser.request(auth_token_uri, "GET")
            if resp['status'] != '200':
                raise Exception(_("Invalid response from OAuth provider: %s") % resp)
            username = (json.loads(content))["email"]
            access_token = dict(screen_name=map_username(username), oauth_token_secret=access_tok)
        #linkedin
        elif social == 'linkedin':
            access_tok = (json.loads(cont))['access_token']
            auth_token_uri = authentication_token_uri + access_tok
            resp, content = parser.request(auth_token_uri, "GET")
            if resp['status'] != '200':
                raise Exception(_("Invalid response from OAuth provider: %s") % resp)
            username = (json.loads(content))['emailAddress']
            access_token = dict(screen_name=map_username(username), oauth_token_secret=access_tok)
  

    return access_token, nexturl


  @classmethod
  def handleLoginRequest(cls, request):
    assert oauth is not None

    redirect_uri = get_redirect_uri(request)
    response_type = "code"
 
    social = request.GET['social']
    state = social + "," + request.GET.get('next', '/')

    if social == 'google':
      consumer_key=liboauth.conf.CONSUMER_KEY_GOOGLE.get()
      token_request_uri = liboauth.conf.REQUEST_TOKEN_URL_GOOGLE.get()
      scope = "https://www.googleapis.com/auth/userinfo.email"
      access_type="offline"
      approval_prompt="force"

      url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}&access_type={access_type}&approval_prompt={approval_prompt}".format(
         token_request_uri = token_request_uri,
         response_type = response_type,
         client_id = consumer_key,
         redirect_uri = redirect_uri,
         scope = scope,
         state = state,
         access_type = access_type,
         approval_prompt = approval_prompt)

    #facebook
    elif social == 'facebook':
       consumer_key=liboauth.conf.CONSUMER_KEY_FACEBOOK.get()
       token_request_uri = liboauth.conf.REQUEST_TOKEN_URL_FACEBOOK.get()
       scope = "email"
       grant_type = "client_credentials"

       url = "{token_request_uri}?client_id={client_id}&redirect_uri={redirect_uri}&grant_type={grant_type}&scope={scope}&state={state}".format(
           token_request_uri=token_request_uri,
           client_id=consumer_key,
           redirect_uri=redirect_uri,
           grant_type=grant_type,
           scope=scope,
           state=state)

    #linkedin
    elif social == 'linkedin':
       consumer_key=liboauth.conf.CONSUMER_KEY_LINKEDIN.get()
       token_request_uri = liboauth.conf.REQUEST_TOKEN_URL_LINKEDIN.get()
       scope= "r_emailaddress"

       url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&scope={scope}&state={state}&redirect_uri={redirect_uri}".format(
             token_request_uri=token_request_uri,
             response_type=response_type,
             client_id=consumer_key,
             scope=scope,
             state=state,
             redirect_uri=redirect_uri)
    #twitter
    else:
       consumer_key=liboauth.conf.CONSUMER_KEY_TWITTER.get()
       consumer_secret=liboauth.conf.CONSUMER_SECRET_TWITTER.get()
       token_request_uri = liboauth.conf.REQUEST_TOKEN_URL_TWITTER.get()
       token_authentication_uri = liboauth.conf.AUTHORIZE_URL_TWITTER.get()

       consumer = oauth.Consumer(consumer_key, consumer_secret)
       client = oauth.Client(consumer)
       resp, content = client.request(token_request_uri, "POST", body=urllib.urlencode({'oauth_callback': redirect_uri}))
       if resp['status'] != '200':
           raise Exception(_("Invalid response from OAuth provider: %s") % resp)
       request.session['request_token'] = dict(cgi.parse_qsl(content))
       url = "{token_authentication_uri}?oauth_token={oauth_token}".format(
            token_authentication_uri=token_authentication_uri,
            oauth_token=request.session['request_token']['oauth_token']
       )
    return url

def map_username(username):
    username_map = liboauth.conf.USERNAME_MAP.get()
    if username_map:
        for key, value in username_map.iteritems():
            username = username.replace(key, value)
    return ''.join([x for x in username if x.isalnum()])

def find_or_create_user(username, password=None):
  try:
    user = User.objects.get(username=username)
    LOG.debug("Found user %s in the db" % username)
  except User.DoesNotExist:
    LOG.info("Materializing user %s in the database" % username)
    user = User(username=username)
    if password is None:
      user.set_unusable_password()
    else:
      user.set_password(password)
    user.is_superuser = True
    user.save()
  return user

def get_redirect_uri(request):
  # Either use the proxy-specified protocol or the one from the request itself.
  # This is useful if the server is behind some kind of proxy
  protocol = request.META.get("HTTP_X_FORWARDED_PROTO",
                              request.META.get('wsgi.url_scheme', 'http'))
  host = request.get_host()
  path = '/oauth/social_login/oauth_authenticated'

  return protocol + "://" + host + path
