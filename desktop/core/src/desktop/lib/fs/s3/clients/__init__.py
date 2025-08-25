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

from desktop.lib.fs.s3.clients.auth.iam import IAMAuthProvider
from desktop.lib.fs.s3.clients.auth.idbroker import IDBrokerAuthProvider
from desktop.lib.fs.s3.clients.auth.key import KeyAuthProvider
from desktop.lib.fs.s3.clients.auth.raz import RazAuthProvider
from desktop.lib.fs.s3.clients.aws import AWSS3Client
from desktop.lib.fs.s3.clients.factory import S3ClientFactory
from desktop.lib.fs.s3.clients.generic import GenericS3Client

# Register provider implementations
S3ClientFactory.register_provider("aws", AWSS3Client)
S3ClientFactory.register_provider("netapp", GenericS3Client)
S3ClientFactory.register_provider("dell", GenericS3Client)
S3ClientFactory.register_provider("generic", GenericS3Client)

# Register auth providers
S3ClientFactory.register_auth_provider("key", KeyAuthProvider)
S3ClientFactory.register_auth_provider("iam", IAMAuthProvider)
S3ClientFactory.register_auth_provider("raz", RazAuthProvider)
S3ClientFactory.register_auth_provider("idbroker", IDBrokerAuthProvider)
