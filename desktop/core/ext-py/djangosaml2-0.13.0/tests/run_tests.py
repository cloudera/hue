#!/usr/bin/env python

# Copyright (C) 2012 Sam Bull (lsb@pocketuniverse.ca)
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


import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management
import django

if hasattr(django, 'setup'):
    django.setup()

management.call_command('test', 'djangosaml2', 'testprofiles')

