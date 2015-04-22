# Copyright (C) 2012 Sam Bull (lsb@pocketuniverse.ca)
# Copyright (C) 2011-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import base64
import re
import urlparse
import sys

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test import TestCase
from django.test.client import RequestFactory

from saml2.config import SPConfig
from saml2.s_utils import decode_base64_and_inflate, deflate_and_base64_encode

from djangosaml2 import views
from djangosaml2.cache import OutstandingQueriesCache
from djangosaml2.conf import get_config
from djangosaml2.tests import conf
from djangosaml2.tests.auth_response import auth_response
from djangosaml2.signals import post_authenticated


PY_VERSION = sys.version_info[:2]


class SAML2Tests(TestCase):

    urls = 'djangosaml2.tests.urls'

    def setUp(self):
        if hasattr(settings, 'SAML_ATTRIBUTE_MAPPING'):
            self.actual_attribute_mapping = settings.SAML_ATTRIBUTE_MAPPING
            del settings.SAML_ATTRIBUTE_MAPPING
        if hasattr(settings, 'SAML_CONFIG_LOADER'):
            self.actual_conf_loader = settings.SAML_CONFIG_LOADER
            del settings.SAML_CONFIG_LOADER

    def tearDown(self):
        if hasattr(self, 'actual_attribute_mapping'):
            settings.SAML_ATTRIBUTE_MAPPING = self.actual_attribute_mapping
        if hasattr(self, 'actual_conf_loader'):
            settings.SAML_CONFIG_LOADER = self.actual_conf_loader

    def assertSAMLRequestsEquals(self, real_xml, expected_xmls):

        def remove_variable_attributes(xml_string):
            xml_string = re.sub(r' ID=".*?" ', ' ', xml_string)
            xml_string = re.sub(r' IssueInstant=".*?" ', ' ', xml_string)
            if PY_VERSION > (2, 6):
                xml_string = re.sub(
                    r'<saml:NameID(.*)>.*</saml:NameID>',
                    r'<saml:NameID\1></saml:NameID>',
                    xml_string)
            else:
                xml_string = re.sub(
                    r'<saml:NameID(.*)>.*</saml:NameID>',
                    r'<saml:NameID\1></saml:NameID>',
                    xml_string)

            return xml_string

        if isinstance(expected_xmls, basestring):
            self.assertEquals(remove_variable_attributes(real_xml),
                              remove_variable_attributes(expected_xmls))
        else:
            py_version_as_str = '%s.%s' % PY_VERSION
            xml = expected_xmls.get(py_version_as_str, None)
            if xml is None:
                xml = expected_xmls.values()[0]
            self.assertEquals(remove_variable_attributes(real_xml),
                              remove_variable_attributes(xml))

    def init_cookies(self):
        self.client.cookies[settings.SESSION_COOKIE_NAME] = 'testing'

    def add_outstanding_query(self, session_id, came_from):
        session = self.client.session
        oq_cache = OutstandingQueriesCache(session)
        oq_cache.set(session_id, came_from)
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    def render_template(self, text):
        return Template(text).render(Context())

    def test_login_one_idp(self):
        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )

        response = self.client.get('/login/')
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path, '/simplesaml/saml2/idp/SSOService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLRequest' in params)
        self.assert_('RelayState' in params)

        saml_request = params['SAMLRequest'][0]
        expected_request26 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:AuthnRequest AssertionConsumerServiceURL="http://sp.example.com/saml2/acs/" Destination="https://idp.example.com/simplesaml/saml2/idp/SSOService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" /></samlp:AuthnRequest>"""
        expected_request27 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:AuthnRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://sp.example.com/saml2/acs/" Destination="https://idp.example.com/simplesaml/saml2/idp/SSOService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" /></samlp:AuthnRequest>"""

        self.assertSAMLRequestsEquals(decode_base64_and_inflate(saml_request),
                                      {'2.6': expected_request26,
                                       '2.7': expected_request27})

        # if we set a next arg in the login view, it is preserverd
        # in the RelayState argument
        next = '/another-view/'
        response = self.client.get('/login/', {'next': next})
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path, '/simplesaml/saml2/idp/SSOService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLRequest' in params)
        self.assert_('RelayState' in params)
        self.assertEquals(params['RelayState'][0], next)

    def test_login_several_idps(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp1.example.com',
                       'idp2.example.com',
                       'idp3.example.com'],
            metadata_file='remote_metadata_three_idps.xml',
        )

        response = self.client.get('/login/')
        # a WAYF page should be displayed
        self.assertContains(response, 'Where are you from?', status_code=200)
        for i in range(1, 4):
            link = '/login/?idp=https://idp%d.example.com/simplesaml/saml2/idp/metadata.php&next=/'
            self.assertContains(response, link % i)

        # click on the second idp
        response = self.client.get('/login/', {
                'idp': 'https://idp2.example.com/simplesaml/saml2/idp/metadata.php',
                'next': '/',
                })
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp2.example.com')
        self.assertEquals(url.path, '/simplesaml/saml2/idp/SSOService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLRequest' in params)
        self.assert_('RelayState' in params)

        saml_request = params['SAMLRequest'][0]
        expected_request26 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:AuthnRequest AssertionConsumerServiceURL="http://sp.example.com/saml2/acs/" Destination="https://idp2.example.com/simplesaml/saml2/idp/SSOService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" /></samlp:AuthnRequest>"""
        expected_request27 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:AuthnRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://sp.example.com/saml2/acs/" Destination="https://idp2.example.com/simplesaml/saml2/idp/SSOService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:NameIDPolicy AllowCreate="false" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" /></samlp:AuthnRequest>"""

        self.assertSAMLRequestsEquals(decode_base64_and_inflate(saml_request),
                                      {'2.6': expected_request26,
                                       '2.7': expected_request27})

    def test_assertion_consumer_service(self):
        # Get initial number of users
        initial_user_count = User.objects.count()
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )

        self.init_cookies()

        # session_id should start with a letter since it is a NCName
        session_id = "a0123456789abcdef0123456789abcdef"
        came_from = '/another-view/'
        self.add_outstanding_query(session_id, came_from)

        # this will create a user
        saml_response = auth_response(session_id, 'student')
        response = self.client.post('/acs/', {
                'SAMLResponse': base64.b64encode(saml_response),
                'RelayState': came_from,
                })
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'testserver')
        self.assertEquals(url.path, came_from)

        self.assertEquals(User.objects.count(), initial_user_count + 1)
        user_id = self.client.session[SESSION_KEY]
        user = User.objects.get(id=user_id)
        self.assertEquals(user.username, 'student')

        # let's create another user and log in with that one
        new_user = User.objects.create(username='teacher', password='not-used')

        session_id = "a1111111111111111111111111111111"
        came_from = ''  # bad, let's see if we can deal with this
        saml_response = auth_response(session_id, 'teacher')
        self.add_outstanding_query(session_id, '/')
        response = self.client.post('/acs/', {
                'SAMLResponse': base64.b64encode(saml_response),
                'RelayState': came_from,
                })
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'testserver')
        # as the RelayState is empty we have redirect to LOGIN_REDIRECT_URL
        self.assertEquals(url.path, '/accounts/profile/')
        self.assertEquals(new_user.id, self.client.session[SESSION_KEY])

    def test_missing_param_to_assertion_consumer_service_request(self):
        # Send request without SAML2Response parameter
        response = self.client.post(reverse('saml2_acs'))
        # Assert that view responded with "Bad Request" error
        self.assertEqual(response.status_code, 400)

    def test_bad_request_method_to_assertion_consumer_service(self):
        # Send request with non-POST method.
        response = self.client.get(reverse('saml2_acs'))
        # Assert that view responded with method not allowed status
        self.assertEqual(response.status_code, 405)

    def do_login(self):
        """Auxiliary method used in several tests (mainly logout tests)"""
        self.init_cookies()

        session_id = "a0123456789abcdef0123456789abcdef"
        came_from = '/another-view/'
        self.add_outstanding_query(session_id, came_from)

        saml_response = auth_response(session_id, 'student')

        # this will create a user
        response = self.client.post('/acs/', {
                'SAMLResponse': base64.b64encode(saml_response),
                'RelayState': came_from,
                })
        self.assertEquals(response.status_code, 302)

    def test_logout(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )
        self.do_login()

        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path,
                          '/simplesaml/saml2/idp/SingleLogoutService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLRequest' in params)

        saml_request = params['SAMLRequest'][0]
        expected_request26 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" Reason="" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" SPNameQualifier="http://sp.example.com/saml2/metadata/" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">58bcc81ea14700f66aeb707a0eff1360</saml:NameID></samlp:LogoutRequest>"""
        expected_request27 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" Reason="" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" SPNameQualifier="http://sp.example.com/saml2/metadata/">58bcc81ea14700f66aeb707a0eff1360</saml:NameID></samlp:LogoutRequest>"""
        self.assertSAMLRequestsEquals(decode_base64_and_inflate(saml_request),
                                      {'2.6': expected_request26,
                                       '2.7': expected_request27})

    def test_logout_service_local(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )

        self.do_login()

        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path,
                          '/simplesaml/saml2/idp/SingleLogoutService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLRequest' in params)

        saml_request = params['SAMLRequest'][0]
        expected_request26 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" Reason="" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" SPNameQualifier="http://sp.example.com/saml2/metadata/" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">58bcc81ea14700f66aeb707a0eff1360</saml:NameID></samlp:LogoutRequest>"""
        expected_request27 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="XXXXXXXXXXXXXXXXXXXXXX" IssueInstant="2010-01-01T00:00:00Z" Reason="" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" SPNameQualifier="http://sp.example.com/saml2/metadata/">58bcc81ea14700f66aeb707a0eff1360</saml:NameID></samlp:LogoutRequest>"""
        xml = decode_base64_and_inflate(saml_request)
        self.assertSAMLRequestsEquals(xml,
                                      {'2.6': expected_request26,
                                       '2.7': expected_request27})

        # now simulate a logout response sent by the idp
        request_id = re.findall(r' ID="(.*?)" ', xml)[0]
        instant = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        saml_response = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutResponse xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="http://sp.example.com/saml2/ls/" ID="a140848e7ce2bce834d7264ecdde0151" InResponseTo="%s" IssueInstant="%s" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></samlp:Status></samlp:LogoutResponse>""" % (
            request_id, instant)

        response = self.client.get('/ls/', {
                'SAMLResponse': deflate_and_base64_encode(saml_response),
                })
        self.assertContains(response, "Logged out", status_code=200)
        self.assertEquals(self.client.session.keys(), [])

    def test_logout_service_global(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )

        self.do_login()

        # now simulate a global logout process initiated by another SP
        subject_id = views._get_subject_id(self.client.session)
        instant = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        saml_request = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_9961abbaae6d06d251226cb25e38bf8f468036e57e" Version="2.0" IssueInstant="%s" Destination="http://sp.example.com/saml2/ls/"><saml:Issuer>https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">%s</saml:NameID><samlp:SessionIndex>_1837687b7bc9faad85839dbeb319627889f3021757</samlp:SessionIndex></samlp:LogoutRequest>""" % (instant, subject_id.text)

        response = self.client.get('/ls/', {
                'SAMLRequest': deflate_and_base64_encode(saml_request),
                })
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path,
                          '/simplesaml/saml2/idp/SingleLogoutService.php')

        params = urlparse.parse_qs(url.query)
        self.assert_('SAMLResponse' in params)

        saml_response = params['SAMLResponse'][0]
        expected_response26 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutResponse Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="a140848e7ce2bce834d7264ecdde0151" InResponseTo="_9961abbaae6d06d251226cb25e38bf8f468036e57e" IssueInstant="2010-09-05T09:10:12Z" Version="2.0" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></samlp:Status></samlp:LogoutResponse>"""
        expected_response27 = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutResponse xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" ID="a140848e7ce2bce834d7264ecdde0151" InResponseTo="_9961abbaae6d06d251226cb25e38bf8f468036e57e" IssueInstant="2010-09-05T09:10:12Z" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></samlp:Status></samlp:LogoutResponse>"""
        self.assertSAMLRequestsEquals(decode_base64_and_inflate(saml_response),
                                      {'2.6': expected_response26,
                                       '2.7': expected_response27})

    def test_incomplete_logout(self):
        settings.SAML_CONFIG = conf.create_conf(sp_host='sp.example.com',
                                                idp_hosts=['idp.example.com'])

        # don't do a login

        # now simulate a global logout process initiated by another SP
        instant = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        saml_request = '<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_9961abbaae6d06d251226cb25e38bf8f468036e57e" Version="2.0" IssueInstant="%s" Destination="http://sp.example.com/saml2/ls/"><saml:Issuer>https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">%s</saml:NameID><samlp:SessionIndex>_1837687b7bc9faad85839dbeb319627889f3021757</samlp:SessionIndex></samlp:LogoutRequest>' % (
            instant, 'invalid-subject-id')

        response = self.client.get('/ls/', {
                'SAMLRequest': deflate_and_base64_encode(saml_request),
                })
        self.assertContains(response, 'Logout error', status_code=200)

    def _test_metadata(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp.example.com'],
            metadata_file='remote_metadata_one_idp.xml',
        )
        valid_until = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        valid_until = valid_until.strftime("%Y-%m-%dT%H:%M:%SZ")
        expected_metadata26 = """<?xml version='1.0' encoding='UTF-8'?>
<md:EntityDescriptor entityID="http://sp.example.com/saml2/metadata/" validUntil="%s" xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"><md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"><md:KeyDescriptor><ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:X509Data><ds:X509Certificate>MIIDPjCCAiYCCQCkHjPQlll+mzANBgkqhkiG9w0BAQUFADBhMQswCQYDVQQGEwJF
UzEQMA4GA1UECBMHU2V2aWxsYTEbMBkGA1UEChMSWWFjbyBTaXN0ZW1hcyBTLkwu
MRAwDgYDVQQHEwdTZXZpbGxhMREwDwYDVQQDEwh0aWNvdGljbzAeFw0wOTEyMDQx
OTQzNTJaFw0xMDEyMDQxOTQzNTJaMGExCzAJBgNVBAYTAkVTMRAwDgYDVQQIEwdT
ZXZpbGxhMRswGQYDVQQKExJZYWNvIFNpc3RlbWFzIFMuTC4xEDAOBgNVBAcTB1Nl
dmlsbGExETAPBgNVBAMTCHRpY290aWNvMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEA7rMOMOaIZ/YYD5hYS6Hpjpovcu4k8gaIY+om9zCxLV5F8BLEfkxo
Pk9IA3cRQNRxf7AXCFxEOH3nKy56AIi1gU7X6fCT30JBT8NQlYdgOVMLlR+tjy1b
YV07tDa9U8gzjTyKQHgVwH0436+rmSPnacGj3fMwfySTMhtmrJmax0bIa8EB+gY1
77DBtvf8dIZIXLlGMQFloZeUspvHOrgNoEA9xU4E9AanGnV9HeV37zv3mLDUOQLx
4tk9sMQmylCpij7WZmcOV07DyJ/cEmnvHSalBTcyIgkcwlhmjtSgfCy6o5zuWxYd
T9ia80SZbWzn8N6B0q+nq23+Oee9H0lvcwIDAQABMA0GCSqGSIb3DQEBBQUAA4IB
AQCQBhKOqucJZAqGHx4ybDXNzpPethszonLNVg5deISSpWagy55KlGCi5laio/xq
hHRx18eTzeCeLHQYvTQxw0IjZOezJ1X30DD9lEqPr6C+IrmZc6bn/pF76xsvdaRS
gduNQPT1B25SV2HrEmbf8wafSlRARmBsyUHh860TqX7yFVjhYIAUF/El9rLca51j
ljCIqqvT+klPdjQoZwODWPFHgute2oNRmoIcMjSnoy1+mxOC2Q/j7kcD8/etulg2
XDxB3zD81gfdtT8VBFP+G4UrBa+5zFk6fT6U8a7ZqVsyH+rCXAdCyVlEC4Y5fZri
ID4zT0FcZASGuthM56rRJJSx
</ds:X509Certificate></ds:X509Data></ds:KeyInfo></md:KeyDescriptor><md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="http://sp.example.com/saml2/ls/" /><md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="http://sp.example.com/saml2/acs/" index="1" /><md:AttributeConsumingService index="1"><md:ServiceName xml:lang="en">Test SP</md:ServiceName><md:RequestedAttribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" isRequired="true" /><md:RequestedAttribute FriendlyName="eduPersonAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" isRequired="false" /></md:AttributeConsumingService></md:SPSSODescriptor><md:Organization><md:OrganizationName xml:lang="es">Ejemplo S.A.</md:OrganizationName><md:OrganizationName xml:lang="en">Example Inc.</md:OrganizationName><md:OrganizationDisplayName xml:lang="es">Ejemplo</md:OrganizationDisplayName><md:OrganizationDisplayName xml:lang="en">Example</md:OrganizationDisplayName><md:OrganizationURL xml:lang="es">http://www.example.es</md:OrganizationURL><md:OrganizationURL xml:lang="en">http://www.example.com</md:OrganizationURL></md:Organization><md:ContactPerson contactType="technical"><md:Company>Example Inc.</md:Company><md:GivenName>Technical givenname</md:GivenName><md:SurName>Technical surname</md:SurName><md:EmailAddress>technical@sp.example.com</md:EmailAddress></md:ContactPerson><md:ContactPerson contactType="administrative"><md:Company>Example Inc.</md:Company><md:GivenName>Administrative givenname</md:GivenName><md:SurName>Administrative surname</md:SurName><md:EmailAddress>administrative@sp.example.ccom</md:EmailAddress></md:ContactPerson></md:EntityDescriptor>"""

        expected_metadata27 = """<?xml version='1.0' encoding='UTF-8'?>
<md:EntityDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="http://sp.example.com/saml2/metadata/" validUntil="%s"><md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"><md:KeyDescriptor use="encryption"><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIDPjCCAiYCCQCkHjPQlll+mzANBgkqhkiG9w0BAQUFADBhMQswCQYDVQQGEwJF
UzEQMA4GA1UECBMHU2V2aWxsYTEbMBkGA1UEChMSWWFjbyBTaXN0ZW1hcyBTLkwu
MRAwDgYDVQQHEwdTZXZpbGxhMREwDwYDVQQDEwh0aWNvdGljbzAeFw0wOTEyMDQx
OTQzNTJaFw0xMDEyMDQxOTQzNTJaMGExCzAJBgNVBAYTAkVTMRAwDgYDVQQIEwdT
ZXZpbGxhMRswGQYDVQQKExJZYWNvIFNpc3RlbWFzIFMuTC4xEDAOBgNVBAcTB1Nl
dmlsbGExETAPBgNVBAMTCHRpY290aWNvMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEA7rMOMOaIZ/YYD5hYS6Hpjpovcu4k8gaIY+om9zCxLV5F8BLEfkxo
Pk9IA3cRQNRxf7AXCFxEOH3nKy56AIi1gU7X6fCT30JBT8NQlYdgOVMLlR+tjy1b
YV07tDa9U8gzjTyKQHgVwH0436+rmSPnacGj3fMwfySTMhtmrJmax0bIa8EB+gY1
77DBtvf8dIZIXLlGMQFloZeUspvHOrgNoEA9xU4E9AanGnV9HeV37zv3mLDUOQLx
4tk9sMQmylCpij7WZmcOV07DyJ/cEmnvHSalBTcyIgkcwlhmjtSgfCy6o5zuWxYd
T9ia80SZbWzn8N6B0q+nq23+Oee9H0lvcwIDAQABMA0GCSqGSIb3DQEBBQUAA4IB
AQCQBhKOqucJZAqGHx4ybDXNzpPethszonLNVg5deISSpWagy55KlGCi5laio/xq
hHRx18eTzeCeLHQYvTQxw0IjZOezJ1X30DD9lEqPr6C+IrmZc6bn/pF76xsvdaRS
gduNQPT1B25SV2HrEmbf8wafSlRARmBsyUHh860TqX7yFVjhYIAUF/El9rLca51j
ljCIqqvT+klPdjQoZwODWPFHgute2oNRmoIcMjSnoy1+mxOC2Q/j7kcD8/etulg2
XDxB3zD81gfdtT8VBFP+G4UrBa+5zFk6fT6U8a7ZqVsyH+rCXAdCyVlEC4Y5fZri
ID4zT0FcZASGuthM56rRJJSx
</ds:X509Certificate></ds:X509Data></ds:KeyInfo></md:KeyDescriptor><md:KeyDescriptor use="sign"><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIDPjCCAiYCCQCkHjPQlll+mzANBgkqhkiG9w0BAQUFADBhMQswCQYDVQQGEwJF
UzEQMA4GA1UECBMHU2V2aWxsYTEbMBkGA1UEChMSWWFjbyBTaXN0ZW1hcyBTLkwu
MRAwDgYDVQQHEwdTZXZpbGxhMREwDwYDVQQDEwh0aWNvdGljbzAeFw0wOTEyMDQx
OTQzNTJaFw0xMDEyMDQxOTQzNTJaMGExCzAJBgNVBAYTAkVTMRAwDgYDVQQIEwdT
ZXZpbGxhMRswGQYDVQQKExJZYWNvIFNpc3RlbWFzIFMuTC4xEDAOBgNVBAcTB1Nl
dmlsbGExETAPBgNVBAMTCHRpY290aWNvMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEA7rMOMOaIZ/YYD5hYS6Hpjpovcu4k8gaIY+om9zCxLV5F8BLEfkxo
Pk9IA3cRQNRxf7AXCFxEOH3nKy56AIi1gU7X6fCT30JBT8NQlYdgOVMLlR+tjy1b
YV07tDa9U8gzjTyKQHgVwH0436+rmSPnacGj3fMwfySTMhtmrJmax0bIa8EB+gY1
77DBtvf8dIZIXLlGMQFloZeUspvHOrgNoEA9xU4E9AanGnV9HeV37zv3mLDUOQLx
4tk9sMQmylCpij7WZmcOV07DyJ/cEmnvHSalBTcyIgkcwlhmjtSgfCy6o5zuWxYd
T9ia80SZbWzn8N6B0q+nq23+Oee9H0lvcwIDAQABMA0GCSqGSIb3DQEBBQUAA4IB
AQCQBhKOqucJZAqGHx4ybDXNzpPethszonLNVg5deISSpWagy55KlGCi5laio/xq
hHRx18eTzeCeLHQYvTQxw0IjZOezJ1X30DD9lEqPr6C+IrmZc6bn/pF76xsvdaRS
gduNQPT1B25SV2HrEmbf8wafSlRARmBsyUHh860TqX7yFVjhYIAUF/El9rLca51j
ljCIqqvT+klPdjQoZwODWPFHgute2oNRmoIcMjSnoy1+mxOC2Q/j7kcD8/etulg2
XDxB3zD81gfdtT8VBFP+G4UrBa+5zFk6fT6U8a7ZqVsyH+rCXAdCyVlEC4Y5fZri
ID4zT0FcZASGuthM56rRJJSx
</ds:X509Certificate></ds:X509Data></ds:KeyInfo></md:KeyDescriptor><md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="http://sp.example.com/saml2/ls/" /><md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="http://sp.example.com/saml2/acs/" index="1" /></md:SPSSODescriptor><md:Organization><md:OrganizationName xml:lang="es">Ejemplo S.A.</md:OrganizationName><md:OrganizationName xml:lang="en">Example Inc.</md:OrganizationName><md:OrganizationDisplayName xml:lang="es">Ejemplo</md:OrganizationDisplayName><md:OrganizationDisplayName xml:lang="en">Example</md:OrganizationDisplayName><md:OrganizationURL xml:lang="es">http://www.example.es</md:OrganizationURL><md:OrganizationURL xml:lang="en">http://www.example.com</md:OrganizationURL></md:Organization><md:ContactPerson contactType="technical"><md:Company>Example Inc.</md:Company><md:GivenName>Technical givenname</md:GivenName><md:SurName>Technical surname</md:SurName><md:EmailAddress>technical@sp.example.com</md:EmailAddress></md:ContactPerson><md:ContactPerson contactType="administrative"><md:Company>Example Inc.</md:Company><md:GivenName>Administrative givenname</md:GivenName><md:SurName>Administrative surname</md:SurName><md:EmailAddress>administrative@sp.example.ccom</md:EmailAddress></md:ContactPerson></md:EntityDescriptor>"""

#<md:AttributeConsumingService index="1"><md:ServiceName xml:lang="en">Test SP</md:ServiceName><md:RequestedAttribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" isRequired="true" /><md:RequestedAttribute FriendlyName="eduPersonAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" isRequired="false" /></md:AttributeConsumingService>

        if PY_VERSION > (2, 6):
            expected_metadata = expected_metadata27 % valid_until
        else:
            expected_metadata = expected_metadata26 % valid_until

        response = self.client.get('/metadata/')
        self.assertEquals(response['Content-type'], 'text/xml; charset=utf8')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, expected_metadata)

    def test_post_authenticated_signal(self):

        def signal_handler(signal, user, session_info):
            self.assertEquals(isinstance(user, User), True)

        post_authenticated.connect(signal_handler, dispatch_uid='test_signal')

        self.do_login()

        post_authenticated.disconnect(dispatch_uid='test_signal')

    def test_idplist_templatetag(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host='sp.example.com',
            idp_hosts=['idp1.example.com',
                       'idp2.example.com',
                       'idp3.example.com'],
            metadata_file='remote_metadata_three_idps.xml',
        )
        rendered = self.render_template(
            '{% load idplist %}'
            '{% idplist as idps %}'
            '{% for url, name in idps.items %}'
            '{{ url }} - {{ name }}; '
            '{% endfor %}'
            )

        # the idplist is unordered, so convert the result into a set.
        rendered = set(rendered.split('; '))
        expected = set([
            u'https://idp1.example.com/simplesaml/saml2/idp/metadata.php - idp1.example.com IdP',
            u'https://idp2.example.com/simplesaml/saml2/idp/metadata.php - idp2.example.com IdP',
            u'https://idp3.example.com/simplesaml/saml2/idp/metadata.php - idp3.example.com IdP',
            u'',
        ])

        self.assertEqual(rendered, expected)


def test_config_loader(request):
    config = SPConfig()
    config.load({'entityid': 'testentity'})
    return config


def test_config_loader_with_real_conf(request):
    config = SPConfig()
    config.load(conf.create_conf(sp_host='sp.example.com',
                                 idp_hosts=['idp.example.com'],
                                 metadata_file='remote_metadata_one_idp.xml'))
    return config


class ConfTests(TestCase):

    def test_custom_conf_loader(self):
        config_loader_path = 'djangosaml2.tests.test_config_loader'
        request = RequestFactory().get('/bar/foo')
        conf = get_config(config_loader_path, request)

        self.assertEquals(conf.entityid, 'testentity')

    def test_custom_conf_loader_from_view(self):
        config_loader_path = 'djangosaml2.tests.test_config_loader_with_real_conf'
        request = RequestFactory().get('/login/')
        request.user = AnonymousUser()
        request.session = {}
        response = views.login(request, config_loader_path)
        self.assertEquals(response.status_code, 302)
        location = response['Location']

        url = urlparse.urlparse(location)
        self.assertEquals(url.hostname, 'idp.example.com')
        self.assertEquals(url.path, '/simplesaml/saml2/idp/SSOService.php')
