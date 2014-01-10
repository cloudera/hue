# -*- coding: utf-8 -*-
# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2009-2013 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import cgi
import unittest
from urllib import quote_plus

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from openid.consumer.consumer import Consumer, SuccessResponse
from openid.consumer.discover import OpenIDServiceEndpoint
from openid.extensions import ax, sreg, pape
from openid.fetchers import (
    HTTPFetcher, HTTPFetchingError, HTTPResponse, setDefaultFetcher)
from openid.oidutil import importElementTree
from openid.server.server import BROWSER_REQUEST_MODES, ENCODE_URL, Server
from openid.store.memstore import MemoryStore
from openid.message import IDENTIFIER_SELECT

from django_openid_auth import teams
from django_openid_auth.models import UserOpenID
from django_openid_auth.views import (
    sanitise_redirect_url, 
    make_consumer,
)
from django_openid_auth.signals import openid_login_complete
from django_openid_auth.store import DjangoOpenIDStore
from django_openid_auth.exceptions import (
    MissingUsernameViolation,
    DuplicateUsernameViolation,
    MissingPhysicalMultiFactor,
    RequiredAttributeNotReturned,
)

ET = importElementTree()

class StubOpenIDProvider(HTTPFetcher):

    def __init__(self, base_url):
        self.store = MemoryStore()
        self.identity_url = base_url + 'identity'
        self.localid_url = base_url + 'localid'
        self.endpoint_url = base_url + 'endpoint'
        self.server = Server(self.store, self.endpoint_url)
        self.last_request = None
        self.type_uris = ['http://specs.openid.net/auth/2.0/signon']

    def fetch(self, url, body=None, headers=None):
        if url == self.identity_url:
            # Serve an XRDS document directly, pointing at our endpoint.
            type_uris = ['<Type>%s</Type>' % uri for uri in self.type_uris]
            return HTTPResponse(
                url, 200, {'content-type': 'application/xrds+xml'}, """\
<?xml version="1.0"?>
<xrds:XRDS
    xmlns="xri://$xrd*($v*2.0)"
    xmlns:xrds="xri://$xrds">
  <XRD>
    <Service priority="0">
      %s
      <URI>%s</URI>
      <LocalID>%s</LocalID>
    </Service>
  </XRD>
</xrds:XRDS>
""" % ('\n'.join(type_uris), self.endpoint_url, self.localid_url))
        elif url.startswith(self.endpoint_url):
            # Gather query parameters
            query = {}
            if '?' in url:
                query.update(cgi.parse_qsl(url.split('?', 1)[1]))
            if body is not None:
                query.update(cgi.parse_qsl(body))
            self.last_request = self.server.decodeRequest(query)

            # The browser based requests should not be handled through
            # the fetcher interface.
            assert self.last_request.mode not in BROWSER_REQUEST_MODES

            response = self.server.handleRequest(self.last_request)
            webresponse = self.server.encodeResponse(response)
            return HTTPResponse(url,  webresponse.code, webresponse.headers,
                                webresponse.body)
        else:
            raise HTTPFetchingError('unknown URL %s' % url)

    def parseFormPost(self, content):
        """Parse an HTML form post to create an OpenID request."""
        # Hack to make the javascript XML compliant ...
        content = content.replace('i < elements.length',
                                  'i &lt; elements.length')
        tree = ET.XML(content)
        form = tree.find('.//form')
        assert form is not None, 'No form in document'
        assert form.get('action') == self.endpoint_url, (
            'Form posts to %s instead of %s' % (form.get('action'),
                                                self.endpoint_url))
        query = {}
        for input in form.findall('input'):
            if input.get('type') != 'hidden':
                continue
            query[input.get('name').encode('UTF-8')] = \
                input.get('value').encode('UTF-8')
        self.last_request = self.server.decodeRequest(query)
        return self.last_request


class DummyDjangoRequest(object):
    def __init__(self, request_path):
        self.request_path = request_path
        self.META = {
            'HTTP_HOST': "localhost",
            'SCRIPT_NAME': "http://localhost",
            'SERVER_PROTOCOL': "http",
        }
        self.POST = {
            'openid_identifier': "http://example.com/identity",
        }
        self.GET = {}
        self.session = {}

    def get_full_path(self):
        return self.META['SCRIPT_NAME'] + self.request_path

    def build_absolute_uri(self):
        return self.META['SCRIPT_NAME'] + self.request_path
        
    def _combined_request(self):
        request = {}
        request.update(self.POST)
        request.update(self.GET)
        return request
    REQUEST = property(_combined_request)

class RelyingPartyTests(TestCase):
    urls = 'django_openid_auth.tests.urls'

    def setUp(self):
        super(RelyingPartyTests, self).setUp()
        self.provider = StubOpenIDProvider('http://example.com/')
        self.req = DummyDjangoRequest('http://localhost/')
        self.endpoint = OpenIDServiceEndpoint()
        self.endpoint.claimed_id = 'http://example.com/identity'
        server_url = 'http://example.com/'
        self.endpoint.server_url = server_url
        self.consumer = make_consumer(self.req)
        self.server = Server(DjangoOpenIDStore(), op_endpoint=server_url)
        setDefaultFetcher(self.provider, wrap_exceptions=False)

        self.old_login_redirect_url = getattr(settings, 'LOGIN_REDIRECT_URL', '/accounts/profile/')
        self.old_create_users = getattr(settings, 'OPENID_CREATE_USERS', False)
        self.old_strict_usernames = getattr(settings, 'OPENID_STRICT_USERNAMES', False)
        self.old_update_details = getattr(settings, 'OPENID_UPDATE_DETAILS_FROM_SREG', False)
        self.old_sso_server_url = getattr(settings, 'OPENID_SSO_SERVER_URL', None)
        self.old_teams_map = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
        self.old_use_as_admin_login = getattr(settings, 'OPENID_USE_AS_ADMIN_LOGIN', False)
        self.old_follow_renames = getattr(settings, 'OPENID_FOLLOW_RENAMES', False)
        self.old_physical_multifactor = getattr(settings, 'OPENID_PHYSICAL_MULTIFACTOR_REQUIRED', False)
        self.old_login_render_failure = getattr(settings, 'OPENID_RENDER_FAILURE', None)
        self.old_consumer_complete = Consumer.complete
        self.old_openid_use_email_for_username = getattr(settings,
            'OPENID_USE_EMAIL_FOR_USERNAME', False)

        self.old_required_fields = getattr(
            settings, 'OPENID_SREG_REQUIRED_FIELDS', [])

        settings.OPENID_CREATE_USERS = False
        settings.OPENID_STRICT_USERNAMES = False
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = False
        settings.OPENID_SSO_SERVER_URL = None
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING = {}
        settings.OPENID_USE_AS_ADMIN_LOGIN = False
        settings.OPENID_FOLLOW_RENAMES = False
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = False
        settings.OPENID_SREG_REQUIRED_FIELDS = []
        settings.OPENID_USE_EMAIL_FOR_USERNAME = False

    def tearDown(self):
        settings.LOGIN_REDIRECT_URL = self.old_login_redirect_url
        settings.OPENID_CREATE_USERS = self.old_create_users
        settings.OPENID_STRICT_USERNAMES = self.old_strict_usernames
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = self.old_update_details
        settings.OPENID_SSO_SERVER_URL = self.old_sso_server_url
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING = self.old_teams_map
        settings.OPENID_USE_AS_ADMIN_LOGIN = self.old_use_as_admin_login
        settings.OPENID_FOLLOW_RENAMES = self.old_follow_renames
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = self.old_physical_multifactor
        settings.OPENID_RENDER_FAILURE = self.old_login_render_failure
        Consumer.complete = self.old_consumer_complete
        settings.OPENID_SREG_REQUIRED_FIELDS = self.old_required_fields
        settings.OPENID_USE_EMAIL_FOR_USERNAME = self.old_openid_use_email_for_username

        setDefaultFetcher(None)
        super(RelyingPartyTests, self).tearDown()

    def complete(self, openid_response):
        """Complete an OpenID authentication request."""
        # The server can generate either a redirect or a form post
        # here.  For simplicity, force generation of a redirect.
        openid_response.whichEncoding = lambda: ENCODE_URL
        webresponse = self.provider.server.encodeResponse(openid_response)
        self.assertEquals(webresponse.code, 302)
        redirect_to = webresponse.headers['location']
        self.assertTrue(redirect_to.startswith(
                'http://testserver/openid/complete/'))
        return self.client.get('/openid/complete/',
            dict(cgi.parse_qsl(redirect_to.split('?', 1)[1])))

    def test_login(self):
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # The login form is displayed:
        response = self.client.get('/openid/login/')
        self.assertTemplateUsed(response, 'openid/login.html')

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        openid_request = self.provider.parseFormPost(response.content)
        self.assertEquals(openid_request.mode, 'checkid_setup')
        self.assertTrue(openid_request.return_to.startswith(
                'http://testserver/openid/complete/'))

        # Complete the request.  The user is redirected to the next URL.
        openid_response = openid_request.answer(True)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')

        # And they are now logged in:
        response = self.client.get('/getuser/')
        self.assertEquals(response.content, 'someuser')

    def test_login_with_nonascii_return_to(self):
        """Ensure non-ascii characters can be used for the 'next' arg."""
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': u'/files/ñandú.jpg'.encode('utf-8')})
        self.assertContains(response, 'OpenID transaction in progress')

    def test_login_no_next(self):
        """Logins with no next parameter redirect to LOGIN_REDIRECT_URL."""
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        settings.LOGIN_REDIRECT_URL = '/getuser/'
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity'})
        self.assertContains(response, 'OpenID transaction in progress')

        openid_request = self.provider.parseFormPost(response.content)
        self.assertEquals(openid_request.mode, 'checkid_setup')
        self.assertTrue(openid_request.return_to.startswith(
                'http://testserver/openid/complete/'))

        # Complete the request.  The user is redirected to the next URL.
        openid_response = openid_request.answer(True)
        response = self.complete(openid_response)
        self.assertRedirects(
            response, 'http://testserver' + settings.LOGIN_REDIRECT_URL)

    def test_login_sso(self):
        settings.OPENID_SSO_SERVER_URL = 'http://example.com/identity'
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Requesting the login form immediately begins an
        # authentication request.
        response = self.client.get('/openid/login/', {'next': '/getuser/'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'OpenID transaction in progress')

        openid_request = self.provider.parseFormPost(response.content)
        self.assertEquals(openid_request.mode, 'checkid_setup')
        self.assertTrue(openid_request.return_to.startswith(
                'http://testserver/openid/complete/'))

        # Complete the request.  The user is redirected to the next URL.
        openid_response = openid_request.answer(True)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')

        # And they are now logged in:
        response = self.client.get('/getuser/')
        self.assertEquals(response.content, 'someuser')

    def test_login_create_users(self):
        settings.OPENID_CREATE_USERS = True
        # Create a user with the same name as we'll pass back via sreg.
        User.objects.create_user('someuser', 'someone@example.com')

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': 'someuser', 'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')

        # And they are now logged in as a new user (they haven't taken
        # over the existing "someuser" user).
        response = self.client.get('/getuser/')
        self.assertEquals(response.content, 'someuser2')

        # Check the details of the new user.
        user = User.objects.get(username='someuser2')
        self.assertEquals(user.first_name, 'Some')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'foo@example.com')

    def _do_user_login(self, req_data, resp_data, use_sreg=True, use_pape=None):
        openid_request = self._get_login_request(req_data)
        openid_response = self._get_login_response(openid_request, resp_data, use_sreg, use_pape)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')
        return response

    def _get_login_request(self, req_data):
        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/', req_data)
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        return openid_request

    def _get_login_response(self, openid_request, resp_data, use_sreg, use_pape):
        openid_response = openid_request.answer(True)

        if use_sreg:
            sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
            sreg_response = sreg.SRegResponse.extractResponse(
                sreg_request, resp_data)
            openid_response.addExtension(sreg_response)
        if use_pape is not None:
            policies = [
                use_pape
            ]
            pape_response = pape.Response(auth_policies=policies)
            openid_response.addExtension(pape_response)
        return openid_response

    def parse_query_string(self, query_str):
        query_items = map(tuple,
            [item.split('=') for item in query_str.split('&')])
        query = dict(query_items)
        return query

    def test_login_physical_multifactor_request(self):
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = True
        preferred_auth = pape.AUTH_MULTI_FACTOR_PHYSICAL
        self.provider.type_uris.append(pape.ns_uri)
        
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        response = self.client.post('/openid/login/', openid_req)
        openid_request = self.provider.parseFormPost(response.content)

        request_auth = openid_request.message.getArg(
            'http://specs.openid.net/extensions/pape/1.0',
            'preferred_auth_policies',
        )
        self.assertEqual(request_auth, preferred_auth)

    def test_login_physical_multifactor_response(self):
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = True
        preferred_auth = pape.AUTH_MULTI_FACTOR_PHYSICAL
        self.provider.type_uris.append(pape.ns_uri)

        def mock_complete(this, request_args, return_to):
            request = {'openid.mode': 'checkid_setup',
                       'openid.trust_root': 'http://localhost/',
                       'openid.return_to': 'http://localhost/',
                       'openid.identity': IDENTIFIER_SELECT,
                       'openid.ns.pape' : pape.ns_uri,
                       'openid.pape.auth_policies': request_args.get('openid.pape.auth_policies', pape.AUTH_NONE),
            }
            openid_server = self.provider.server
            orequest = openid_server.decodeRequest(request)
            response = SuccessResponse(
                self.endpoint, orequest.message,
                signed_fields=['openid.pape.auth_policies',])
            return response
        Consumer.complete = mock_complete

        user = User.objects.create_user('testuser', 'test@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Openid User',
                 'email': 'test@example.com'}

        response = self._do_user_login(openid_req, openid_resp, use_pape=pape.AUTH_MULTI_FACTOR_PHYSICAL)

        query = self.parse_query_string(response.request['QUERY_STRING'])
        self.assertTrue('openid.pape.auth_policies' in query)
        self.assertEqual(query['openid.pape.auth_policies'], 
                quote_plus(preferred_auth))

        response = self.client.get('/getuser/')
        self.assertEqual(response.content, 'testuser')


    def test_login_physical_multifactor_not_provided(self):
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = True
        preferred_auth = pape.AUTH_MULTI_FACTOR_PHYSICAL
        self.provider.type_uris.append(pape.ns_uri)

        def mock_complete(this, request_args, return_to):
            request = {'openid.mode': 'checkid_setup',
                       'openid.trust_root': 'http://localhost/',
                       'openid.return_to': 'http://localhost/',
                       'openid.identity': IDENTIFIER_SELECT,
                       'openid.ns.pape' : pape.ns_uri,
                       'openid.pape.auth_policies': request_args.get('openid.pape.auth_policies', pape.AUTH_NONE),
            }
            openid_server = self.provider.server
            orequest = openid_server.decodeRequest(request)
            response = SuccessResponse(
                self.endpoint, orequest.message,
                signed_fields=['openid.pape.auth_policies',])
            return response
        Consumer.complete = mock_complete

        user = User.objects.create_user('testuser', 'test@example.com')
        useropenid = UserOpenID(    
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Openid User',
                 'email': 'test@example.com'}

        openid_request = self._get_login_request(openid_req)
        openid_response = self._get_login_response(openid_request, openid_req, openid_resp, use_pape=pape.AUTH_NONE)

        response_auth = openid_request.message.getArg(
            'http://specs.openid.net/extensions/pape/1.0',
            'auth_policies',
        )
        self.assertNotEqual(response_auth, preferred_auth)

        response = self.complete(openid_response)
        self.assertEquals(403, response.status_code)
        self.assertContains(response, '<h1>OpenID failed</h1>', status_code=403)
        self.assertContains(response, '<p>Login requires physical multi-factor authentication.</p>', status_code=403)

    def test_login_physical_multifactor_not_provided_override(self):
        settings.OPENID_PHYSICAL_MULTIFACTOR_REQUIRED = True
        preferred_auth = pape.AUTH_MULTI_FACTOR_PHYSICAL
        self.provider.type_uris.append(pape.ns_uri)

        # Override the login_failure handler
        def mock_login_failure_handler(request, message, status=403,
                                       template_name=None,
                                       exception=None):
           self.assertTrue(isinstance(exception, MissingPhysicalMultiFactor))
           return HttpResponse('Test Failure Override', status=200)
        settings.OPENID_RENDER_FAILURE = mock_login_failure_handler

        def mock_complete(this, request_args, return_to):
            request = {'openid.mode': 'checkid_setup',
                       'openid.trust_root': 'http://localhost/',
                       'openid.return_to': 'http://localhost/',
                       'openid.identity': IDENTIFIER_SELECT,
                       'openid.ns.pape' : pape.ns_uri,
                       'openid.pape.auth_policies': request_args.get('openid.pape.auth_policies', pape.AUTH_NONE),
            }
            openid_server = self.provider.server
            orequest = openid_server.decodeRequest(request)
            response = SuccessResponse(
                self.endpoint, orequest.message,
                signed_fields=['openid.pape.auth_policies',])
            return response
        Consumer.complete = mock_complete

        user = User.objects.create_user('testuser', 'test@example.com')
        useropenid = UserOpenID(    
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Openid User',
                 'email': 'test@example.com'}

        openid_request = self._get_login_request(openid_req)
        openid_response = self._get_login_response(openid_request, openid_req, openid_resp, use_pape=pape.AUTH_NONE)

        response_auth = openid_request.message.getArg(
            'http://specs.openid.net/extensions/pape/1.0',
            'auth_policies',
        )
        self.assertNotEqual(response_auth, preferred_auth)

        # Status code should be 200, since we over-rode the login_failure handler
        response = self.complete(openid_response)
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Test Failure Override')

    def test_login_without_nickname(self):
        settings.OPENID_CREATE_USERS = True

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': '', 'fullname': 'Openid User',
                 'email': 'foo@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # username defaults to 'openiduser'
        self.assertEquals(response.content, 'openiduser')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Openid')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'foo@example.com')

    def test_login_without_nickname_with_email_suggestion(self):
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_USE_EMAIL_FOR_USERNAME = True

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': '', 'fullname': 'Openid User',
                 'email': 'foo@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # username defaults to a munged version of the email
        self.assertEquals(response.content, 'fooexamplecom')

    def test_login_duplicate_username_numbering(self):
        settings.OPENID_FOLLOW_RENAMES = False
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to conflict with
        user = User.objects.create_user('testuser', 'someone@example.com')

        # identity url is for 'renameuser'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Test User',
                 'email': 'test@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it, and get testuser2.
        self.assertEquals(response.content, 'testuser2')

    def test_login_duplicate_username_numbering_with_conflicts(self):
        settings.OPENID_FOLLOW_RENAMES = False
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to conflict with
        user = User.objects.create_user('testuser', 'someone@example.com')
        user = User.objects.create_user('testuser3', 'someone@example.com')

        # identity url is for 'renameuser'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Test User',
                 'email': 'test@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 2.  i should
        # start at 3, which already exists, so it should skip to 4.
        self.assertEquals(response.content, 'testuser4')

    def test_login_duplicate_username_numbering_with_holes(self):
        settings.OPENID_FOLLOW_RENAMES = False
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to conflict with
        user = User.objects.create_user('testuser', 'someone@example.com')
        user = User.objects.create_user('testuser1', 'someone@example.com')
        user = User.objects.create_user('testuser6', 'someone@example.com')
        user = User.objects.create_user('testuser7', 'someone@example.com')
        user = User.objects.create_user('testuser8', 'someone@example.com')

        # identity url is for 'renameuser'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Test User',
                 'email': 'test@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 5.  i should
        # start at 6, and increment until it reaches 9.
        self.assertEquals(response.content, 'testuser9')

    def test_login_duplicate_username_numbering_with_nonsequential_matches(self):
        settings.OPENID_FOLLOW_RENAMES = False
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to conflict with
        user = User.objects.create_user('testuser', 'someone@example.com')
        user = User.objects.create_user('testuserfoo', 'someone@example.com')

        # identity url is for 'renameuser'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Test User',
                 'email': 'test@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # Since this username is already taken by someone else, we go through
        # the process of adding +i to it starting with the count of users with
        # username starting with 'testuser', of which there are 2.  i should
        # start at 3, which will be available.
        self.assertEquals(response.content, 'testuser3')

    def test_login_follow_rename(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'someuser', 'fullname': 'Some User',
                 'email': 'foo@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # If OPENID_FOLLOW_RENAMES, they are logged in as
        # someuser (the passed in nickname has changed the username)
        self.assertEquals(response.content, 'someuser')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Some')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'foo@example.com')

    def test_login_follow_rename_without_nickname_change(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        settings.OPENID_STRICT_USERNAMES = True
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Some User',
                 'email': 'foo@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # Username should not have changed
        self.assertEquals(response.content, 'testuser')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Some')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'foo@example.com')

    def test_login_follow_rename_conflict(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to switch to
        user = User.objects.create_user('testuser', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')

        # Setup user who is going to try to change username to 'testuser'
        renamed_user = User.objects.create_user('renameuser', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=renamed_user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')

        # identity url is for 'renameuser'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Rename User',
                 'email': 'rename@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # If OPENID_FOLLOW_RENAMES, attempt to change username to 'testuser'
        # but since that username is already taken by someone else, we go through
        # the process of adding +i to it, and get testuser2.
        self.assertEquals(response.content, 'testuser2')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Rename')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'rename@example.com')

    def test_login_follow_rename_false_onlyonce(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to switch to
        user = User.objects.create_user('testuser', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')

        # Setup user who is going to try to change username to 'testuser'
        renamed_user = User.objects.create_user('testuser2000eight', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=renamed_user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')

        # identity url is for 'testuser2000eight'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser2', 'fullname': 'Rename User',
                 'email': 'rename@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # If OPENID_FOLLOW_RENAMES, attempt to change username to 'testuser'
        # but since that username is already taken by someone else, we go through
        # the process of adding +i to it.  Even though it looks like the username
        # follows the nickname+i scheme, it has non-numbers in the suffix, so
        # it's not an auto-generated one.  The regular process of renaming to
        # 'testuser' has a conflict, so we get +2 at the end.
        self.assertEquals(response.content, 'testuser2')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Rename')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'rename@example.com')

    def test_login_follow_rename_conflict_onlyonce(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's name we're going to switch to
        user = User.objects.create_user('testuser', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/existing_identity',
            display_id='http://example.com/existing_identity')

        # Setup user who is going to try to change username to 'testuser'
        renamed_user = User.objects.create_user('testuser2000', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=renamed_user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')

        # identity url is for 'testuser2000'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which already exists for another identity
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Rename User',
                 'email': 'rename@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # If OPENID_FOLLOW_RENAMES, attempt to change username to 'testuser'
        # but since that username is already taken by someone else, we go through
        # the process of adding +i to it.  Since the user for this identity url
        # already has a name matching that pattern, check if first.
        self.assertEquals(response.content, 'testuser2000')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Rename')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'rename@example.com')

    def test_login_follow_rename_false_conflict(self):
        settings.OPENID_FOLLOW_RENAMES = True
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        # Setup existing user who's username matches the name+i pattern
        user = User.objects.create_user('testuser2', 'someone@example.com')
        UserOpenID.objects.get_or_create(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')

        # identity url is for 'testuser2'
        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        # but returned username is for 'testuser', which looks like we've done
        # a username+1 for them already, but 'testuser' isn't actually taken
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Same User',
                 'email': 'same@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        # If OPENID_FOLLOW_RENAMES, username should be changed to 'testuser'
        # because it wasn't currently taken
        self.assertEquals(response.content, 'testuser')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Same')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'same@example.com')

    def test_strict_username_no_nickname(self):
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_STRICT_USERNAMES = True
        settings.OPENID_SREG_REQUIRED_FIELDS = []

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': '', # No nickname
                           'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)

        # Status code should be 403: Forbidden
        self.assertEquals(403, response.status_code)
        self.assertContains(response, '<h1>OpenID failed</h1>', status_code=403)
        self.assertContains(response, "An attribute required for logging in was not returned "
            "(nickname)", status_code=403)

    def test_strict_username_no_nickname_override(self):
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_STRICT_USERNAMES = True
        settings.OPENID_SREG_REQUIRED_FIELDS = []

        # Override the login_failure handler
        def mock_login_failure_handler(request, message, status=403,
                                       template_name=None,
                                       exception=None):
           self.assertTrue(isinstance(exception, (RequiredAttributeNotReturned, MissingUsernameViolation)))
           return HttpResponse('Test Failure Override', status=200)
        settings.OPENID_RENDER_FAILURE = mock_login_failure_handler
        
        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': '', # No nickname
                           'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)
            
        # Status code should be 200, since we over-rode the login_failure handler
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Test Failure Override')

    def test_strict_username_duplicate_user(self):
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_STRICT_USERNAMES = True
        # Create a user with the same name as we'll pass back via sreg.
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/different_identity',
            display_id='http://example.com/different_identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': 'someuser', 'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)

        # Status code should be 403: Forbidden
        self.assertEquals(403, response.status_code)
        self.assertContains(response, '<h1>OpenID failed</h1>', status_code=403)
        self.assertContains(response,
            "The username (someuser) with which you tried to log in is "
            "already in use for a different account.",
            status_code=403)

    def test_strict_username_duplicate_user_override(self):
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_STRICT_USERNAMES = True

        # Override the login_failure handler
        def mock_login_failure_handler(request, message, status=403,
                                       template_name=None,
                                       exception=None):
           self.assertTrue(isinstance(exception, DuplicateUsernameViolation))
           return HttpResponse('Test Failure Override', status=200)
        settings.OPENID_RENDER_FAILURE = mock_login_failure_handler

        # Create a user with the same name as we'll pass back via sreg.
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/different_identity',
            display_id='http://example.com/different_identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': 'someuser', 'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)
        
        # Status code should be 200, since we over-rode the login_failure handler
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Test Failure Override')

    def test_login_requires_sreg_required_fields(self):
        # If any required attributes are not included in the response,
        # we fail with a forbidden.
        settings.OPENID_CREATE_USERS = True
        settings.OPENID_SREG_REQUIRED_FIELDS = ('email', 'language')
        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request, passing back some simple registration
        # data.  The user is redirected to the next URL.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        openid_response = openid_request.answer(True)
        sreg_response = sreg.SRegResponse.extractResponse(
            sreg_request, {'nickname': 'foo',
                           'fullname': 'Some User',
                           'email': 'foo@example.com'})
        openid_response.addExtension(sreg_response)
        response = self.complete(openid_response)

        # Status code should be 403: Forbidden as we didn't include
        # a required field - language.
        self.assertContains(response,
            "An attribute required for logging in was not returned "
            "(language)", status_code=403)

    def test_login_update_details(self):
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        openid_req = {'openid_identifier': 'http://example.com/identity',
               'next': '/getuser/'}
        openid_resp =  {'nickname': 'testuser', 'fullname': 'Some User',
                 'email': 'foo@example.com'}
        self._do_user_login(openid_req, openid_resp)
        response = self.client.get('/getuser/')

        self.assertEquals(response.content, 'testuser')

        # The user's full name and email have been updated.
        user = User.objects.get(username=response.content)
        self.assertEquals(user.first_name, 'Some')
        self.assertEquals(user.last_name, 'User')
        self.assertEquals(user.email, 'foo@example.com')

    def test_login_uses_sreg_extra_fields(self):
        # The configurable sreg attributes are used in the request.
        settings.OPENID_SREG_EXTRA_FIELDS = ('language',)
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})

        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        for field in ('email', 'fullname', 'nickname', 'language'):
            self.assertTrue(field in sreg_request)

    def test_login_uses_sreg_required_fields(self):
        # The configurable sreg attributes are used in the request.
        settings.OPENID_SREG_REQUIRED_FIELDS = ('email', 'language')
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})

        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)

        self.assertEqual(['email', 'language'], sreg_request.required)
        self.assertEqual(['fullname', 'nickname'], sreg_request.optional)

    def test_login_attribute_exchange(self):
        settings.OPENID_UPDATE_DETAILS_FROM_SREG = True
        user = User.objects.create_user('testuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Configure the provider to advertise attribute exchange
        # protocol and start the authentication process:
        self.provider.type_uris.append('http://openid.net/srv/ax/1.0')
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # The resulting OpenID request uses the Attribute Exchange
        # extension rather than the Simple Registration extension.
        openid_request = self.provider.parseFormPost(response.content)
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)
        self.assertEqual(sreg_request.required, [])
        self.assertEqual(sreg_request.optional, [])

        fetch_request = ax.FetchRequest.fromOpenIDRequest(openid_request)
        self.assertTrue(fetch_request.has_key(
                'http://axschema.org/contact/email'))
        self.assertTrue(fetch_request.has_key(
                'http://axschema.org/namePerson'))
        self.assertTrue(fetch_request.has_key(
                'http://axschema.org/namePerson/first'))
        self.assertTrue(fetch_request.has_key(
                'http://axschema.org/namePerson/last'))
        self.assertTrue(fetch_request.has_key(
                'http://axschema.org/namePerson/friendly'))
        # myOpenID compatibilty attributes:
        self.assertTrue(fetch_request.has_key(
                'http://schema.openid.net/contact/email'))
        self.assertTrue(fetch_request.has_key(
                'http://schema.openid.net/namePerson'))
        self.assertTrue(fetch_request.has_key(
                'http://schema.openid.net/namePerson/friendly'))

        # Build up a response including AX data.
        openid_response = openid_request.answer(True)
        fetch_response = ax.FetchResponse(fetch_request)
        fetch_response.addValue(
            'http://axschema.org/contact/email', 'foo@example.com')
        fetch_response.addValue(
            'http://axschema.org/namePerson/first', 'Firstname')
        fetch_response.addValue(
            'http://axschema.org/namePerson/last', 'Lastname')
        fetch_response.addValue(
            'http://axschema.org/namePerson/friendly', 'someuser')
        openid_response.addExtension(fetch_response)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')

        # And they are now logged in as testuser (the passed in
        # nickname has not caused the username to change).
        response = self.client.get('/getuser/')
        self.assertEquals(response.content, 'testuser')

        # The user's full name and email have been updated.
        user = User.objects.get(username='testuser')
        self.assertEquals(user.first_name, 'Firstname')
        self.assertEquals(user.last_name, 'Lastname')
        self.assertEquals(user.email, 'foo@example.com')

    def test_login_teams(self):
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO = False
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING = {'teamname': 'groupname',
                                                   'otherteam': 'othergroup'}
        user = User.objects.create_user('testuser', 'someone@example.com')
        group = Group(name='groupname')
        group.save()
        ogroup = Group(name='othergroup')
        ogroup.save()
        user.groups.add(ogroup)
        user.save()
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request
        openid_request = self.provider.parseFormPost(response.content)
        openid_response = openid_request.answer(True)
        teams_request = teams.TeamsRequest.fromOpenIDRequest(openid_request)
        teams_response = teams.TeamsResponse.extractResponse(
            teams_request, 'teamname,some-other-team')
        openid_response.addExtension(teams_response)
        response = self.complete(openid_response)
        self.assertRedirects(response, 'http://testserver/getuser/')

        # And they are now logged in as testuser
        response = self.client.get('/getuser/')
        self.assertEquals(response.content, 'testuser')

        # The user's groups have been updated.
        user = User.objects.get(username='testuser')
        self.assertTrue(group in user.groups.all())
        self.assertTrue(ogroup not in user.groups.all())

    def test_login_teams_automapping(self):
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING = {'teamname': 'groupname',
                                                   'otherteam': 'othergroup'}
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO = True
        settings.OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST = ['django-group1', 'django-group2']
        user = User.objects.create_user('testuser', 'someone@example.com')
        group1 = Group(name='django-group1')
        group1.save()
        group2 = Group(name='django-group2')
        group2.save()
        group3 = Group(name='django-group3')
        group3.save()
        user.save()
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity',
             'next': '/getuser/'})
        self.assertContains(response, 'OpenID transaction in progress')

        # Complete the request
        openid_request = self.provider.parseFormPost(response.content)
        openid_response = openid_request.answer(True)
        teams_request = teams.TeamsRequest.fromOpenIDRequest(openid_request)

        self.assertEqual(group1 in user.groups.all(), False)
        self.assertEqual(group2 in user.groups.all(), False)
        self.assertTrue(group3 not in user.groups.all())

    def test_login_teams_staff_not_defined(self):
        delattr(settings, 'OPENID_LAUNCHPAD_STAFF_TEAMS')
        user = User.objects.create_user('testuser', 'someone@example.com')
        user.is_staff = True
        user.save()
        self.assertTrue(user.is_staff)

        user = self.get_openid_authed_user_with_teams(user, 'teamname,some-other-team')
        self.assertTrue(user.is_staff)

    def test_login_teams_staff_assignment(self):
        settings.OPENID_LAUNCHPAD_STAFF_TEAMS = ('teamname',)
        user = User.objects.create_user('testuser', 'someone@example.com')
        user.is_staff = False
        user.save()
        self.assertFalse(user.is_staff)

        user = self.get_openid_authed_user_with_teams(user, 'teamname,some-other-team')
        self.assertTrue(user.is_staff)

    def test_login_teams_staff_unassignment(self):
        settings.OPENID_LAUNCHPAD_STAFF_TEAMS = ('different-teamname',)
        user = User.objects.create_user('testuser', 'someone@example.com')
        user.is_staff = True
        user.save()
        self.assertTrue(user.is_staff)

        user = self.get_openid_authed_user_with_teams(user, 'teamname,some-other-team')
        self.assertFalse(user.is_staff)

    def get_openid_authed_user_with_teams(self, user, teams_str):
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()

        # Posting in an identity URL begins the authentication request:
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity'})

        # Complete the request
        openid_request = self.provider.parseFormPost(response.content)
        openid_response = openid_request.answer(True)
        teams_request = teams.TeamsRequest.fromOpenIDRequest(openid_request)
        teams_response = teams.TeamsResponse.extractResponse(
            teams_request, teams_str)
        openid_response.addExtension(teams_response)
        response = self.complete(openid_response)
        return User.objects.get(username=user.username)

    def test_login_complete_signals_login(self):
        # An oauth_login_complete signal is emitted including the
        # request and sreg_response.
        user = User.objects.create_user('someuser', 'someone@example.com')
        useropenid = UserOpenID(
            user=user,
            claimed_id='http://example.com/identity',
            display_id='http://example.com/identity')
        useropenid.save()
        response = self.client.post('/openid/login/',
            {'openid_identifier': 'http://example.com/identity'})
        openid_request = self.provider.parseFormPost(response.content)
        openid_response = openid_request.answer(True)
        # Use a closure to test whether the signal handler was called.
        self.signal_handler_called = False
        def login_callback(sender, **kwargs):
            self.assertTrue(isinstance(
                kwargs.get('request', None), HttpRequest))
            self.assertTrue(isinstance(
                kwargs.get('openid_response', None), SuccessResponse))
            self.signal_handler_called = True
        openid_login_complete.connect(login_callback)

        response = self.complete(openid_response)

        self.assertTrue(self.signal_handler_called)
        openid_login_complete.disconnect(login_callback)

    
class HelperFunctionsTest(TestCase):
    def test_sanitise_redirect_url(self):
        settings.ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = [
            "example.com", "example.org"]
        # list of URLs and whether they should be passed or not
        urls = [
            ("http://example.com", True),
            ("http://example.org/", True),
            ("http://example.org/foo/bar", True),
            ("http://example.org/foo/bar?baz=quux", True),
            ("http://example.org:9999/foo/bar?baz=quux", True),
            ("http://www.example.org/", False),
            ("http://example.net/foo/bar?baz=quux", False),
            ("/somewhere/local", True),
            ("/somewhere/local?url=http://fail.com/bar", True),
            # An empty path, as seen when no "next" parameter is passed.
            ("", False),
            ("/path with spaces", False),
        ]
        for url, returns_self in urls:
            sanitised = sanitise_redirect_url(url)
            if returns_self:
                self.assertEqual(url, sanitised)
            else:
                self.assertEqual(settings.LOGIN_REDIRECT_URL, sanitised)

def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)
