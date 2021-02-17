#!/bin/bash
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
set -x

TMP_DIR=/tmp/$(basename "$0" | awk -F\. '{print $1}')

HUE_VERSION=$1

if [[ -d /opt/cloudera/parcels/CDH/lib/hue-${HUE_VERSION} ]]
then
  echo "This version already downloaded"
  exit 1
fi

HUE_MAJOR=$(echo ${HUE_VERSION} | cut -f1 -d.)
OS_CDH_VERSION=$(basename $(hadoop version | grep "\.jar" | awk '{print $6}') | awk -Fcdh '{print $2}' | awk -F\. '{print $1}')
OS_EL_VERSION="el$(lsb_release -rs | cut -f1 -d.)"

HUE_VERSION_TEST=
if [[ ${HUE_MAJOR} -eq 5 ]]
then
  HUE_VERSION_TEST=$(echo ${HUE_VERSION} | grep "^[0-9]\.[0-9][0-9]\.[0-9]$")
  ARCHIVE_BASE_URL=https://archive.cloudera.com/cdh${HUE_MAJOR}/parcels/${HUE_VERSION}/
elif [[ ${HUE_MAJOR} -eq 6 ]]
then
  HUE_VERSION_TEST=$(echo ${HUE_VERSION} | grep "^[0-9]\.[0-9]\.[0-9]$")
  ARCHIVE_BASE_URL=https://archive.cloudera.com/cdh${HUE_MAJOR}/${HUE_VERSION}/parcels/
elif [[ ${HUE_MAJOR} -eq 7 ]]
then
  HUE_VERSION_TEST=$(echo ${HUE_VERSION} | grep "^[0-9]\.[0-9]\.[0-9]$")
  ARCHIVE_BASE_URL=https://archive.cloudera.com/cdh${HUE_MAJOR}/${HUE_VERSION}/parcels/
else
  echo "Major version was ${HUE_MAJOR} this script only works on major version 5, 6, 7"
  exit 1
fi

if [[ -z ${HUE_VERSION_TEST} ]]
then
  echo "Invalid Hue version, example of good 5.16.0 or 6.3.2"
  exit 1
fi

if [[ ! -f /etc/redhat-release ]]
then
  echo "This is not RedHat, Oracle Linux or CentOS, this script only works on those OS's"
  exit 1
fi

PARCEL_NAME=$(curl -s ${ARCHIVE_BASE_URL} | grep "${OS_EL_VERSION}.parcel<" | sed "s/.*href=\"//g" | sed "s/\">.*//g")
if [[ ! -z ${PARCEL_NAME} ]]
then
  PARCEL_DIR_NAME=$(echo ${PARCEL_NAME} | sed "s/\-${OS_EL_VERSION}.*//g")

  mkdir -p ${TMP_DIR}
  cd ${TMP_DIR} && wget ${ARCHIVE_BASE_URL}/${PARCEL_NAME}
  cd ${TMP_DIR} && tar xvf ${PARCEL_NAME}
  if [[ ! -d /opt/cloudera/parcels/CDH/lib/hue-${HUE_VERSION} ]]
  then
    cd ${TMP_DIR} && mv ${PARCEL_DIR_NAME}/lib/hue /opt/cloudera/parcels/CDH/lib/hue-${HUE_VERSION}
  fi
else
  echo "${HUE_VERSION} does not exist"
fi
cd && rm -Rf ${TMP_DIR}
