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

FROM openjdk:8

ARG HBASE_VERSION
ARG HBASE_DIR
ARG PHOENIX_VERSION
ARG PHOENIX_NAME=apache-phoenix

ENV HBASE_URL https://archive.apache.org/dist/hbase/$HBASE_DIR/hbase-$HBASE_VERSION-bin.tar.gz

RUN wget --no-verbose -O hbase.tar.gz "$HBASE_URL" && \
    mkdir /opt/hbase && \
    tar xf hbase.tar.gz --strip-components=1 -C /opt/hbase && \
    rm hbase.tar.gz

ENV PHOENIX_URL https://archive.apache.org/dist/phoenix/apache-phoenix-$PHOENIX_VERSION/bin/apache-phoenix-$PHOENIX_VERSION-bin.tar.gz

RUN wget --no-verbose -O phoenix.tar.gz "$PHOENIX_URL" && \
    mkdir /opt/phoenix && \
    tar xf phoenix.tar.gz --strip-components=1 -C /opt/phoenix && \
    rm phoenix.tar.gz

RUN ln -sv /opt/phoenix/phoenix-*-server.jar /opt/hbase/lib/

ADD hbase-site.xml /opt/hbase/conf/hbase-site.xml

ENV HBASE_CONF_DIR /opt/hbase/conf
ENV HBASE_CP /opt/hbase/lib
ENV HBASE_HOME /opt/hbase

EXPOSE 8765

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
