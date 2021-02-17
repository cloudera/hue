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
PARCEL_DIR=/opt/cloudera/parcels/CDH
LOG_FILE=/var/log/hue/`basename "$0" | awk -F\. '{print $1}'`.log
DATABASE=$1
PASSWORD=$2
TYPE=$3

if [[ -z ${DBUSER} ]]
then
   DBUSER="cloudera"
fi

if [[ -z ${DBPASSWORD} ]]
then
   DBPASSWORD="cloudera"
fi

if [[ -z ${TYPE} ]]
then
   TYPE="mysql"
fi

if [[ -z ${DATABASE} ]]
then
   echo "Usage: hue_create_db.sh <database_name> <password> <dbtype-mysql-postgres>"
   exit 1
fi


export HUE_DATABASE_PASSWORD=${PASSWORD}
export HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1

HUE_CONF_DIR=/tmp/hue_create_db/${DATABASE}
mkdir -p ${HUE_CONF_DIR}

if [ ! -d "/usr/lib/hadoop" ]
then
   CDH_HOME=$PARCEL_DIR
else
   CDH_HOME=/usr
fi

if [ -d "${CDH_HOME}/lib/hue/build/env/bin" ]
then
   COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue"
else
   COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue"
fi

DATABASE_DUMP=${HUE_CONF_DIR}/hue_database_dump.json
ORACLE_HOME=/opt/cloudera/parcels/ORACLE_INSTANT_CLIENT/instantclient_11_2/
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_HOME}
export CDH_HOME HUE_CONF_DIR ORACLE_HOME LD_LIBRARY_PATH COMMAND PASSWORD DATABASE

${COMMAND} dumpdata --indent 2 > ${HUE_CONF_DIR}/hue_database_dump.json

if [[ ${TYPE} =~ .*mysql.* ]]
then
cat > ${HUE_CONF_DIR}/hue.ini << EOF
[desktop]
[[database]]
#engine=sqlite3
#name=/var/lib/hue/desktop.db
engine=mysql
host=`hostname`
port=3306
user=${DATABASE}
password=${PASSWORD}
name=${DATABASE}
EOF

cat > ${HUE_CONF_DIR}/create.sql << EOF
drop database if exists ${DATABASE};
create database ${DATABASE};
grant all on *.* to '${DATABASE}'@'%' identified by '${PASSWORD}';
EOF

mysql -uroot -p${PASSWORD} < ${HUE_CONF_DIR}/create.sql
elif [[ ${TYPE} =~ .*postgres.* ]]
then
   yum -y install postgresql-server
   chkconfig postgresql on
   if [[ ! -f /var/lib/pgsql/data/postgresql.conf ]]
   then
      service postgresql initdb
   fi
   CHECK_HBA=$(grep ${DATABASE} /var/lib/pgsql/data/pg_hba.conf)
   if [[ -z ${CHECK_HBA} ]]
   then
      echo "host        ${DATABASE}     ${DATABASE}     0.0.0.0/0       md5" >> /var/lib/pgsql/data/pg_hba.conf
   fi
   sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '0.0.0.0'/g" /var/lib/pgsql/data/postgresql.conf
   service postgresql restart
   sudo -u postgres /bin/bash -c psql -U postgres << EOF
create database ${DATABASE};
\c ${DATABASE};
create user ${DATABASE} with password '${PASSWORD}';
grant all privileges on database ${DATABASE} to ${DATABASE};
\q
EOF
cat > ${HUE_CONF_DIR}/hue.ini << EOF
[desktop]
[[database]]
#engine=sqlite3
#name=/var/lib/hue/desktop.db
engine=postgresql_psycopg2
host=`hostname`
port=5432
user=${DATABASE}
password=${PASSWORD}
name=${DATABASE}
EOF
fi

${COMMAND} syncdb --noinput
${COMMAND} migrate --merge

if [[ ${TYPE} =~ .*mysql.* ]]
then
   CONSTRAINT_ID=$(mysql -uroot -p${PASSWORD} ${DATABASE} -e "show create table auth_permission" | grep content_type_id_refs_id | awk -Fid_ '{print $3}' | awk -F\` '{print $1}')

cat > ${HUE_CONF_DIR}/prepare.sql << EOF
ALTER TABLE auth_permission DROP FOREIGN KEY content_type_id_refs_id_${CONSTRAINT_ID};
delete from django_content_type;
EOF

mysql -uroot -p${PASSWORD} ${DATABASE} < ${HUE_CONF_DIR}/prepare.sql

elif [[ ${TYPE} =~ .*postgres.* ]]
then
  CONSTRAINT_ID=$(PGPASSWORD=${PASSWORD} psql -h `hostname` -U ${DATABASE} -d ${DATABASE} -c '\d auth_permission;' | grep content_type_id_refs_id | awk -Fid_ '{print $3}' | awk -F\" '{print $1}')
#PGPASSWORD=${PASSWORD} psql -h `hostname` -U ${DATABASE} -d ${DATABASE} << EOF
#ALTER TABLE auth_permission DROP CONSTRAINT content_type_id_refs_id_${CONSTRAINT_ID};
#TRUNCATE django_content_type CASCADE;
#EOF
fi



