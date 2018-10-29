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
import logging
import os
import platform

from altuscli.auth import RSAv1Auth
from altuscli.credentials import Credentials
from altuscli.signers import RequestSigner

from navoptapi.serialize import Serializer

from requests import put, Request, Session

import six

LOG = logging.getLogger('altuscli.navopt')
ROOT_LOGGER = logging.getLogger('')
LOG_FORMAT = ('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

DEFAULT_PROFILE_NAME = 'default'
VERSION = "0.1.0"


class ApiLib(object):

    def __init__(self, service_name, host_name, access_key, private_key):
        # get Credentials
        self._access_key = access_key
        self._private_key = private_key
        self._endpoint_url = "https://" + host_name + "/" + service_name + "/"
        self._service_name = service_name
        self._cred = Credentials(access_key, private_key,
                                 method='shared-credentials-file')
        self._signer = RequestSigner(RSAv1Auth.AUTH_METHOD_NAME, self._cred)

    def _build_user_agent_header(self):
        return 'ALTUSCLI/%s Python/%s %s/%s' % (VERSION,
                                                platform.python_version(),
                                                platform.system(),
                                                platform.release())

    def _encode_headers(self, headers):
        # In place encoding of headers to utf-8 if they are unicode.
        for key, value in headers.items():
            if isinstance(value, six.text_type):
                # We have to do this because request.headers is not
                # normal dictionary.  It has the (unintuitive) behavior
                # of aggregating repeated setattr calls for the same
                # key value.  For example:
                # headers['foo'] = 'a'; headers['foo'] = 'b'
                # list(headers) will print ['foo', 'foo'].
                del headers[key]
                headers[key] = value.encode('utf-8')

    def _upload_file(self, params, prepped, api_session):
        # header for upload
        s3_session = Session()
        api_url = self._endpoint_url + "getS3url"
        req = Request('POST', api_url)
        upload_prepped = req.prepare()
        self._encode_headers(upload_prepped.headers)
        upload_prepped.headers['Content-Type'] = 'application/json'
        upload_prepped.headers['User-Agent'] = self._build_user_agent_header()
        self._signer.sign(upload_prepped)
        # prepare params for s3 url
        url_parameters = {'fileName': '', 'tenant': ''}
        if 'fileName' in params and params['fileName']:
            url_parameters['fileName'] = params['file_name']
        elif 'fileLocation' in params and params['fileLocation']:
            if os.path.isfile(params['fileLocation']):
                fileName = os.path.basename(params['fileLocation'])
                url_parameters['fileName'] = fileName

        if 'tenant' in params and params['tenant']:
            url_parameters['tenant'] = params['tenant']
        # prepare the body
        serializer = Serializer()
        serial_obj = serializer.serialize_to_request(url_parameters, None)
        upload_prepped.prepare_body(serial_obj['body'], None)
        resp = s3_session.send(upload_prepped)
        resp = json.loads(json.dumps(resp.json()))

        # upload file to S3 bucket
        if 'url' in resp and 'fileLocation' in params and params['fileLocation']:
            put(resp['url'], data=open(params['fileLocation']).read())
            # build upload parameters
            upload_params = {'rowDelim': '', 'colDelim': '', 'headerFields': [],
                             'tenant': '', 'fileType': 0}
            # now do actual upload
            if 'tenant' in params and params['tenant']:
                upload_params['tenant'] = params['tenant']
            upload_params['fileLocation'] = params['fileLocation']
            if os.path.isfile(params['fileLocation']):
                fileName = os.path.basename(params['fileLocation'])
                upload_params['fileName'] = fileName
            if 'fileName' in params and params['fileName']:
                upload_params['fileName'] = params['fileName']
            if 'sourcePlatform' in params and params['sourcePlatform']:
                upload_params['sourcePlatform'] = params['sourcePlatform']
            if 'colDelim' in params and params['colDelim']:
                upload_params['colDelim'] = params['colDelim']
            if 'rowDelim' in params and params['rowDelim']:
                upload_params['rowDelim'] = params['rowDelim']
            if 'headerFields' in params and params['headerFields']:
                upload_params['headerFields'] = params['headerFields']
            if 'fileType' in params and params['fileType']:
                upload_params['fileType'] = params['fileType']
            # prepare the body
            serializer = Serializer()
            serial_obj = serializer.serialize_to_request(upload_params, None)
            prepped.prepare_body(serial_obj['body'], None)
            resp = api_session.send(prepped)
            resp = json.dumps(resp.json())
        return resp

    def call_api(self, operation_name, params=None):
        if not operation_name:
            return
        if params is None:
          params = {}

        api_session = Session()
        api_url = self._endpoint_url + operation_name
        req = Request('POST', api_url)
        prepped = req.prepare()
        self._encode_headers(prepped.headers)
        prepped.headers['Content-Type'] = 'application/json'
        prepped.headers['User-Agent'] = self._build_user_agent_header()
        self._signer.sign(prepped)

        # check if operation is for 'upload'
        if operation_name == 'upload':
            # get s3url for the upload and then do a upload
            resp = self._upload_file(params, prepped, api_session)
            return resp
        # prepare the body
        serializer = Serializer()
        serial_obj = serializer.serialize_to_request(params, None)
        prepped.prepare_body(serial_obj['body'], None)
        resp = api_session.send(prepped)
        return resp
