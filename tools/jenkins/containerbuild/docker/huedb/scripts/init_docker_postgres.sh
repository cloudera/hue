#!/bin/bash

# this script is run when the docker container is built
# it imports the base database structure and create the database for the tests

DB_DUMP_LOCATION="/tmp/psql_data/huedb.dump"
DB_USER="hueuser"
DB_PASSWORD="huepasswd"
DB_NAME="huedb"


echo "*** CREATING DATABASE ***"

{ psql --user postgres <<-EOSQL
    CREATE ROLE "$DB_USER" superuser;
    CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
    ALTER ROLE "$DB_USER" WITH LOGIN;
    CREATE DATABASE "$DB_NAME" WITH OWNER="$DB_USER" TEMPLATE=template0 ENCODING='$DB_ENCODING';
    GRANT ALL PRIVILEGES ON TABLE "$DB_NAME" TO "$DB_USER";
EOSQL
}

psql "$DB_NAME" < "$DB_DUMP_LOCATION";
echo "*** DATABASE CREATED! ***"
