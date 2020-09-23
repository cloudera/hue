---
title: "Database"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Hue requires a SQL database to store small amounts of data, including user account information as well as history of queries and sharing permissions.

By default, Hue is configured to use an embedded SQLite database so that it starts but many errors will come up due to the lack of transactions.

This section contains instructions for configuring Hue with another database.

## Configuring with another Database

Although SQLite is the default database type, some advanced users may prefer
to have Hue access an alternate database type. Note that if you elect to
configure Hue to use an external database, upgrades may require more manual
steps in the future.

The following instructions are for MySQL, though you can also configure Hue to work with other common databases such as PostgreSQL and Oracle.


### MySQL

To configure Hue to store data in MySQL:

1. Create a new database in MySQL and grant privileges to a Hue user to manage
   this database.

    mysql> create database hue;
    Query OK, 1 row affected (0.01 sec)
    mysql> grant all on hue.* to 'hue'@'localhost' identified by 'secretpassword';
    Query OK, 0 rows affected (0.00 sec)

2. Shut down Hue if it is running.

3. To migrate your existing data to MySQL, use the following command to dump the
   existing database data to a text file. Note that using the ".json" extension
   is required.

    /usr/share/hue/build/env/bin/hue dumpdata > $some-temporary-file.json

4. Open the `hue.ini` file in a text editor. Directly below the
   `[[database]]` line, add the following options (and modify accordingly for
   your MySQL setup):

    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue

5. As the Hue user, configure Hue to load the existing data and create the database tables:

    /usr/share/hue/build/env/bin/hue migrate
    mysql -uhue -psecretpassword -e "DELETE FROM hue.django_content_type;"
    /usr/share/hue/build/env/bin/hue loaddata $temporary-file-containing-dumped-data.json

Your system is now configured and you can start the Hue server as normal.

### PostgreSQL

Log on to PostgreSQL:
    psql -h localhost -U hue -d hue

Password for user hue:

Drop the foreign key constraint from auth_permission:

    \d auth_permission;
    ALTER TABLE auth_permission DROP CONSTRAINT content_type_id_refs_id_<id value>;

Delete the contents of django_content_type:

    TRUNCATE django_content_type CASCADE;

Load Database.

    Add the foreign key, content_type_id, to auth_permission:
    ALTER TABLE auth_permission ADD FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

### Oracle

Oracle users should delete all content from the Oracle tables after synchronizing and before loading:

Log on to Oracle:

    su - oracle
    sqlplus / as sysdba

Grant a quota to the tablespace where tables are created (the default is SYSTEM). For example:

    ALTER USER hue quota 100m on system;

Log on as the hue:

    sqlplus hue/<hue password>

Create a spool script that creates a delete script to clean the content of all tables.

    vi spool_statements.ddl

Save in spool_statements.ddl (which generates delete_from_tables.ddl)

    spool delete_from_tables.ddl
    set pagesize 100;
    SELECT 'DELETE FROM ' || table_name || ';' FROM user_tables;
    commit;
    spool off
    quit

Run both scripts:

    -- Create delete_from_tables.ddl
    sqlplus hue/<your hue password> < spool_statements.ddl

    -- Run delete_from_tables.ddl
    sqlplus hue/<your hue password> < delete_from_tables.ddl

#### RAC

The current setup of Oracle is this way:

    Hostname : ORACLE IP
    Database Type: Oracle
    Database Name: <Service Name/SID of one of the instance>
    Username: <username>
    Password: <password>

This would be an alternate way to address the Oracle RAC issue:

1. Go to Hue > Configuration > Database > Hue Database Name
2. Enter the database name in the following format
Hue Database Name=(DESCRIPTION=(LOAD_BALANCE=off)(FAILOVER=on)(CONNECT_TIMEOUT=5)(TRANSPORT_CONNECT_TIMEOUT=3)(RETRY_COUNT=3)(ADDRESS=(PROTOCOL=TCP)(HOST=<scan ip>)(PORT=<port>))(CONNECT_DATA=(SERVICE_NAME=<service name>)))

If the above does not work, then use the below config info `hue_safety_valve_server` for database:

    engine=oracle
    port=0
    user=<username>
    password=<password>
    name=(DESCRIPTION=(LOAD_BALANCE=off)(FAILOVER=on)(CONNECT_TIMEOUT=5)(TRANSPORT_CONNECT_TIMEOUT=3)(RETRY_COUNT=3)(ADDRESS=(PROTOCOL=TCP)(HOST=<scan ip>)(PORT=<port>))(CONNECT_DATA=(SERVICE_NAME=<service name>)))

## Operation

### Inspecting

You can inspect your database via its standard own Shell, Hue [SQL Editor](/administrator/configuration/connectors/#databases) itself, or from the command line using the db shell:

    /usr/share/hue/build/env/bin/hue dbshell

It is strongly recommended that you avoid making any modifications to the database directly, though this trick can be useful for management or troubleshooting.

### Backing up

It is recommended that you back it up on a regular schedule, and also that you back it up before any upgrade to a new version or doing a data change in the database.

Backing up can be done the standard way of the chosen database or via dumping the records similarly to doing a [migration](#migrating).

### Clean up

When the database has too many entries in certain tables, it will cause performance issue. Now Hue config check will help superuser to find this issue. Login as superuser and go to "Administration, this sample screenshot will be displayed in the quick start wizard when the tables have too many entries:

[<img class="size-full wp-image-5802 aligncenter" src="https://cdn.gethue.com/uploads/2019/03/Doc2CountCheck.png"/>][1]

Run following clean up command:

    cd /opt/cloudera/parcels/CDH/lib/hue  # Hue home directory
    ./build/env/bin/hue desktop_document_cleanup

### Migrating

Hue Custom Databases includes database-specific pages on how to migrate from an old to a new database (e.g. sqlite to Oracle or MySQL). This page summarizes across supported database types.

When you change Hue databases, you can migrate the existing data to your new database.

#### Dump Database

Ensure that the Hue service is stopped and dump the database content like explained in the top section and the `dumpdata` command.

Edit `/tmp/hue_database_dump.json` by removing all objects with useradmin.userprofile in the model field.

For example:

    grep -c useradmin.userprofile /tmp/hue_database_dump.json

    vi /tmp/hue_database_dump.json
    {
      "pk": 1,
      "model": "useradmin.userprofile",
      "fields": {
        "last_activity": "2016-10-03T10:06:13",
        "creation_method": "HUE",
        "first_login": false,
        "user": 1,
        "home_directory": "/user/admin"
      }
    },

#### Connect to the new Database

Set the appropriate database parameters :

    Hue Database Type: MySQL or PostgreSQL or Oracle
    Hue Database Hostname: <fqdn of host with database server>
    Hue Database Port: 3306 or 5432 or 1521
    Hue Database Username: <hue database username>
    Hue Database Password: <hue database password>
    Hue Database Name: <hue database name or SID>

Oracle users only should add support for a multithreaded environment:

Add support for a multithreaded environment by setting in the hue.ini:

    [desktop]
    [[database]]
    options={"threaded":True}

In the Hue Web UI, click the home icon Hue Home icon to ensure that all documents were migrated.

    MariaDB / MySQL
    Synchronize Database in Cloudera Manager.
    Log on to MySQL:
    mysql -u root -p
    Enter password: <root password>

Drop the foreign key constraint from the hue.auth_permission table:

Execute the following statement to find the `content_type_id_refs_id_<value>` in the CONSTRAINT clause of the CREATE TABLE statement for the `hue.auth_permission` table:

    SHOW CREATE TABLE hue.auth_permission;

This SHOW CREATE TABLE statement produces output similar to the following:

    |  auth_permission | CREATE TABLE 'auth_permission' (
      'id' int(11) NOT NULL AUTO-INCREMENT,
      'name' varchar(50) NOT NULL,
      'content_type_id' int(11) NOT NULL,
      'CODENAME' VARCHAR(100) NOT NULL,
      PRIMARY KEY ('id'),
      UNIQUE KEY 'content_type_id' ('content_type_id', 'codename'),
      KEY 'auth_permission_37ef4eb4' ('content_type_id'),
      CONSTRAINT 'content_type_id_refs_id_d043b34a' FOREIGN KEY ('content_type_id')
    REFERENCES 'django_content_type' ('id')
    ) ENGINE=InnoDB AUTO_INCREMENT=229 DEFAULT CHARSET=utf8 |

Then execute the following statement to drop the foreign key constraint:

    ALTER TABLE hue.auth_permission DROP FOREIGN KEY
    content_type_id_refs_id_<value>;

For example, if you used the above output from the SHOW CREATE TABLE statement, you would use the following ALTER TABLE statement:

    ALTER TABLE hue.auth_permission DROP FOREIGN KEY
    content_type_id_refs_id_d043b34a;

Delete the contents of django_content_type:

    DELETE FROM hue.django_content_type;

Load Database.

    Add the foreign key, content_type_id, to auth_permission:

    ALTER TABLE hue.auth_permission ADD FOREIGN KEY (content_type_id) REFERENCES django_content_type (id);
