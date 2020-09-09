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

from themattrix/tox-base

RUN apt-get update && apt-get install -y krb5-user libkrb5-dev

ENV PHOENIXDB_TEST_DB_URL=http://host.docker.internal:8765
ENV PHOENIXDB_TEST_DB_TRUSTSTORE=
ENV PHOENIXDB_TEST_DB_AUTHENTICATION=
ENV PHOENIXDB_TEST_DB_AVATICA_USER=
ENV PHOENIXDB_TEST_DB_AVATICA_PASSWORD=
