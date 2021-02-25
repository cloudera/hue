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

#Changes owner of Search Dashboard
PARCEL_DIR=/opt/cloudera/parcels/CDH

DASHBOARD=$1
NEWOWNER=$2
USAGE="usage: $0 <dashboardname> <new_owner_name>"

if [[ ! ${USER} =~ .*root* ]]
then
  echo "Script must be run as root: exiting"
  exit 1
fi

if [[ -z ${NEWOWNER} ]]
then
  echo "No new_owner_name specified:"
  echo ${USAGE}
  exit 1
fi

if [[ -z ${DASHBOARD} ]]
then
  echo "No dashboard_name specified:"
  echo ${USAGE}
  exit 1
fi

if [ ! -d "/usr/lib/hadoop" ]
then
   CDH_HOME=$PARCEL_DIR
else
   CDH_HOME=/usr
fi

if [ -d "/var/run/cloudera-scm-agent/process" ]
then
   HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE_SERVER | sort -n | tail -1 `"
else
   HUE_CONF_DIR="/etc/hue/conf"
fi

if [ -d "${CDH_HOME}/lib/hue/build/env/bin" ]
then
   COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue shell"
else
   COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue shell"
fi

ORACLE_HOME=/opt/cloudera/parcels/ORACLE_INSTANT_CLIENT/instantclient_11_2/
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_HOME}
export CDH_HOME HUE_CONF_DIR ORACLE_HOME LD_LIBRARY_PATH COMMAND

echo "HUE_CONF_DIR: ${HUE_CONF_DIR}"
echo "COMMAND: ${COMMAND}"

${COMMAND} <<EOF
dashboard = "${DASHBOARD}"
newowner = "${NEWOWNER}"
from django.contrib.auth.models import User
from search.models import Collection
user = User.objects.get(username=newowner)
#for collection in Collection.objects.filter(name=dashboard):
#collection = Collection.objects.get(name=dashboard)

for collection in Collection.objects.filter(name=dashboard):
  print "Changing owner of colection(%s) from user(%s) to user(%s)" % (collection.name, collection.owner, user.username)
  collection.owner = user
  collection.save()

#collection = Collection.objects.get(name=dashboard)
for collection in Collection.objects.filter(name=dashboard):
  print "Owner of colection(%s) is now user(%s)" % (collection.name, collection.owner)

#Useful other examples:
#from django.contrib.auth.models import User, Group
#user = User.objects.get(username="tuser4")
#user2 = User.objects.get(username="cconner")
#from search.models import Collection
#for collection in Collection.objects.filter(owner=user):
#  collection.name
#  collection.owner
#  print ""
#  collection.owner = user2
#  collection.save()

#from django.contrib.auth.models import User, Group
#dashboardname = "students"
#user = User.objects.get(username="tuser4")
#user2 = User.objects.get(username="cconner")
#from search.models import Collection
#for collection in Collection.objects.filter(name=dashboardname):
#  collection.name
#  collection.owner
#  print ""
#  collection.owner = user2
#  collection.save()

EOF
