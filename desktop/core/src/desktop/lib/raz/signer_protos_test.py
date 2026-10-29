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

"""
Guards the generated RAZ protobuf module against the installed protobuf runtime.

signer_protos_pb2.py is generated code that refuses to import with a runtime older than the protoc that
produced it, so a protobuf downgrade or an incompatible regeneration shows up here first.
"""

import desktop.lib.raz.signer_protos_pb2 as raz_signer


class TestSignerProtos:
  def test_sign_request_round_trips_through_the_wire_format(self):
    request = raz_signer.SignRequestProto(
      endpoint_prefix="s3",
      service_name="cm_s3",
      endpoint="https://bucket.s3.amazonaws.com",
      http_method="GET",
      headers=[{"key": "Host", "value": "bucket.s3.amazonaws.com"}],
      parameters=[{"key": "prefix", "value": "a/b"}],
      resource_path="/key",
      content_to_sign=b"payload",
      time_offset=0,
    )

    parsed = raz_signer.SignRequestProto()
    parsed.ParseFromString(request.SerializeToString())

    assert parsed == request
    assert parsed.http_method == raz_signer.HttpMethodProto.GET
    assert parsed.headers[0].key == "Host"
    assert parsed.content_to_sign == b"payload"
