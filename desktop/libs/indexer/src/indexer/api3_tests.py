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
import json
from django.http import HttpRequest
from indexer.api3 import upload_local_file
from nose.tools import assert_equal
from django.utils.datastructures import MultiValueDict
from django.core.files.uploadhandler import InMemoryUploadedFile
from urllib.parse import urlparse, unquote as urllib_unquote

def test_xlsx_local_file_upload():

    class User:
        def __init__(self, username='test'):
            self.username = username
    correct = '''test 1,test.2,test_3,test_4
2010-10-10 00:00:00,2012-10-11 01:00:00,30,
2021-10-10 00:00:00,2012-10-11 03:00:00,0.12,
2010-10-10 00:00:00,2012-10-11 09:00:00,0.99,
2010-10-10 00:00:00,2012-10-11 04:00:00,500,
2010-10-10 00:00:00,2012-10-11 09:00:00,29830,
2010-10-10 00:00:00,2012-10-11 08:00:00,50,
2010-10-10 00:00:00,2012-10-11 07:00:00,,
2010-10-10 00:00:00,2012-10-11 03:00:00,,
2010-10-10 00:00:00,2012-10-11 09:00:00,,
2010-10-10 00:00:00,2022-10-10 14:00:00,,
2010-10-10 00:00:00,2021-10-10 15:00:00,,
2010-10-10 00:00:00,,,
2010-10-10 00:00:00,,,
2010-10-10 00:00:00,scattered,,
2010-10-10 00:00:00,,scattered,
2010-10-10 00:00:00,,,
,,,
,,,
scattered,,,
,,scattered,
,,,
,,,
,scattered,,
,,,
,,,
,,,
scattered,,,scattered
,,,
,,,
,,,
,,,
,scattered,,
'''
    with open('apps/beeswax/data/tables/testbook1.xlsx','rb') as file:
        #must keep indentation like this or file will leave scope and not get read by xlsxreader
        f = InMemoryUploadedFile(file=file,field_name='test',name='testbook1.xlsx', content_type='xlsx',size=100,charset='utf-8')
        request = HttpRequest()
        request.user = User()
        request.FILES = MultiValueDict({'file': [f]})
        response = upload_local_file(request)
    path = urllib_unquote(json.loads(response.content.decode('utf-8'))['local_file_url'])
    with open(path, 'r') as test_file:
        test = test_file.read()
        assert_equal(correct, test)