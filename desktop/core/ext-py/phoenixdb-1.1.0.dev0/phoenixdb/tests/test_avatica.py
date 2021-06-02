# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import phoenixdb
from phoenixdb.avatica.client import parse_url, urlparse

from requests.auth import HTTPBasicAuth


class ParseUrlTest(unittest.TestCase):

    def test_parse_url(self):
        self.assertEqual(urlparse.urlparse('http://localhost:8765/'), parse_url('localhost'))
        # Python 3.9 will interpret "localhost:" as a scheme. Argueably,it is right
        # self.assertEqual(urlparse.urlparse('http://localhost:2222/'), parse_url('localhost:2222'))
        self.assertEqual(urlparse.urlparse('http://localhost:2222/'), parse_url('http://localhost:2222/'))

    def test_url_params(self):
        (url, auth, verify) = phoenixdb._process_args((
            "https://localhost:8765?authentication=BASIC&"
            "avatica_user=user&avatica_password=password&truststore=truststore"))
        self.assertEqual("https://localhost:8765", url)
        self.assertEqual("truststore", verify)
        self.assertEqual(auth, HTTPBasicAuth("user", "password"))

        (url, auth, verify) = phoenixdb._process_args(
            "http://localhost:8765", authentication='BASIC', user='user', password='password',
            truststore='truststore')
        self.assertEqual("http://localhost:8765", url)
        self.assertEqual("truststore", verify)
        self.assertEqual(auth, HTTPBasicAuth("user", "password"))

        (url, auth, verify) = phoenixdb._process_args(
            "https://localhost:8765", authentication='SPNEGO', user='user', truststore='truststore')
        self.assertEqual("https://localhost:8765?doAs=user", url)
        self.assertEqual("truststore", verify)
        # SPNEGO auth objects seem to have no working __eq__
        # self.assertEqual(auth, HTTPSPNEGOAuth(opportunistic_auth=True))
