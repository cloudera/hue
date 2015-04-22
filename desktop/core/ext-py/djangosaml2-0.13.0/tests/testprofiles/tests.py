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

import django

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from django.test import TestCase

from djangosaml2.backends import Saml2Backend

if django.VERSION < (1,7):
    from testprofiles.models import TestProfile


class Saml2BackendTests(TestCase):
    def test_update_user(self):
        # we need a user
        user = User.objects.create(username='john')

        backend = Saml2Backend()

        attribute_mapping = {
            'uid': ('username', ),
            'mail': ('email', ),
            'cn': ('first_name', ),
            'sn': ('last_name', ),
            }
        attributes = {
            'uid': ('john', ),
            'mail': ('john@example.com', ),
            'cn': ('John', ),
            'sn': ('Doe', ),
            }
        backend.update_user(user, attributes, attribute_mapping)
        self.assertEquals(user.email, 'john@example.com')
        self.assertEquals(user.first_name, 'John')
        self.assertEquals(user.last_name, 'Doe')

        # now we create a user profile and link it to the user
        if django.VERSION < (1, 7):
            profile = TestProfile.objects.create(user=user)
            self.assertNotEquals(profile, None)

        attribute_mapping['saml_age'] = ('age', )
        attributes['saml_age'] = ('22', )
        backend.update_user(user, attributes, attribute_mapping)

        if django.VERSION < (1, 7):
            self.assertEquals(user.get_profile().age, '22')
        else:
            self.assertEquals(user.age, '22')
