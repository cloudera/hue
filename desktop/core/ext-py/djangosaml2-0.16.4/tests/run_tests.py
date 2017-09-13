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
import sys

from django.core.wsgi import get_wsgi_application
from django.core import management

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
sys.path.append(PROJECT_DIR)
# Load models
application = get_wsgi_application()

management.call_command('test', 'djangosaml2.tests', 'testprofiles')
