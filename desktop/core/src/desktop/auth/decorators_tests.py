#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import sys
import unittest
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from desktop.auth.decorators import admin_required, hue_admin_required
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.exceptions_renderable import PopupException
from useradmin.models import Group, Organization, User


class TestDecorator(TestCase):

  @classmethod
  def setup_class(cls):
    cls.client1 = make_logged_in_client(username='admin', recreate=True, is_superuser=True)
    cls.client2 = make_logged_in_client(username='joe', recreate=True, is_superuser=False)

  def test_admin_required(self):
    request = Mock(user=User.objects.get(username='admin'))
    hello_admin(request)

    request = Mock(user=User.objects.get(username='joe'))
    with pytest.raises(PopupException):
      hello_admin(request)

  def test_hue_admin_required(self):
    request = Mock(user=User.objects.get(username='admin'))
    hello_hue_admin(request)

    request = Mock(user=User.objects.get(username='joe'))
    with pytest.raises(PopupException):
      hello_hue_admin(request)


@admin_required
def hello_admin(request, *args, **kwargs):
  return 'Hello'


@admin_required
def hello_hue_admin(request, *args, **kwargs):
  return 'Hello'
