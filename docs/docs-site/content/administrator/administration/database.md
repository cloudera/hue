---
title: "Database"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Hue requires a SQL database to store small amounts of data, including user
account information as well as history of job submissions and Hive queries.
By default, Hue is configured to use the embedded database SQLite for this
purpose, and should require no configuration or management by the administrator.
However, MySQL is the recommended database to use. This section contains
instructions for configuring Hue to access MySQL and other databases.

### Inspecting the Database

The default SQLite database used by Hue is located in: `/usr/share/hue/desktop/desktop.db`.
You can inspect this database from the command line using the `sqlite3`
program or typing `/usr/share/hue/build/env/bin/hue dbshell'. For example:

    sqlite3 /usr/share/hue/desktop/desktop.db
    SQLite version 3.6.22
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"
    sqlite> select username from auth_user;
    admin
    test
    sample
    sqlite>

It is strongly recommended that you avoid making any modifications to the
database directly using SQLite, though this trick can be useful for management
or troubleshooting.

### Backing up the Database

If you use the default SQLite database, then copy the `desktop.db` file to
another node for backup. It is recommended that you back it up on a regular
schedule, and also that you back it up before any upgrade to a new version of
Hue.

### Clean up the database

When the database has too many entries in certain tables, it will cause performance issue. Now Hue config check will help superuser to find this issue. Login as superuser and go to “Hue Administration”, this sample screenshot will be displayed in the quick start wizard when the tables have too many entries.

Run following clean up command:

  cd /opt/cloudera/parcels/CDH/lib/hue # Hue home directory
  ./build/env/bin/hue desktop_document_cleanup


### Configuring to Access Another Database

Although SQLite is the default database type, some advanced users may prefer
to have Hue access an alternate database type. Note that if you elect to
configure Hue to use an external database, upgrades may require more manual
steps in the future.

The following instructions are for MySQL, though you can also configure Hue to
work with other common databases such as PostgreSQL and Oracle.

<div class="note">
Note that Hue has only been tested with SQLite and MySQL database backends.
</div>


### Configuring to Store Data in MySQL

To configure Hue to store data in MySQL:

1. Create a new database in MySQL and grant privileges to a Hue user to manage
   this database.

    <pre>
    mysql> create database hue;
    Query OK, 1 row affected (0.01 sec)
    mysql> grant all on hue.* to 'hue'@'localhost' identified by 'secretpassword';
    Query OK, 0 rows affected (0.00 sec)
    </pre>

2. Shut down Hue if it is running.

3. To migrate your existing data to MySQL, use the following command to dump the
   existing database data to a text file. Note that using the ".json" extension
   is required.

    <pre>
    /usr/share/hue/build/env/bin/hue dumpdata > $some-temporary-file.json
    </pre>

4. Open the `hue.ini` file in a text editor. Directly below the
   `[[database]]` line, add the following options (and modify accordingly for
   your MySQL setup):

    <pre>
    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue
    </pre>

5. As the Hue user, configure Hue to load the existing data and create the
   necessary database tables:

    <pre>
    /usr/share/hue/build/env/bin/hue syncdb --noinput
    mysql -uhue -psecretpassword -e "DELETE FROM hue.django_content_type;"
    /usr/share/hue/build/env/bin/hue loaddata $temporary-file-containing-dumped-data.json
    </pre>

Your system is now configured and you can start the Hue server as normal.

### Migrate the Hue Database
Note: Hue Custom Databases includes database-specific pages on how to migrate from an old to a new database. This page summarizes across supported database types.
When you change Hue databases, you can migrate the existing data to your new database. If the data is dispensable, there is no need to migrate.

The Hue database stores things like user accounts, SQL queries, and Oozie workflows, and you may have accounts, queries, and workflows worth saving. See How to Populate the Hue Database.

Dump Database

Note: Refresh the page to ensure that the Hue service is stopped: Service Stopped icon.
Select Actions > Dump Database and click Dump Database. The file is written to /tmp/hue_database_dump.json on the host of the Hue server.

Log on to the host of the Hue server in a command-line terminal. You can find the hostname on the Dump Database window and at Hue > Hosts.
Edit /tmp/hue_database_dump.json by removing all objects with useradmin.userprofile in the model field. For example:

Count number of objects

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

Connect New Database

Set the appropriate database parameters :

    Hue Database Type: MySQL or PostgreSQL or Oracle
    Hue Database Hostname: <fqdn of host with database server>
    Hue Database Port: 3306 or 5432 or 1521
    Hue Database Username: <hue database username>
    Hue Database Password: <hue database password>
    Hue Database Name: <hue database name or SID>

Oracle users only should add support for a multithreaded environment:

Add support for a multithreaded environment by setting Hue Service Advanced Configuration Snippet (Safety Valve) for hue_safety_valve.ini:
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

Execute the following statement to find the content_type_id_refs_id_<value> in the CONSTRAINT clause of the CREATE TABLE statement for the hue.auth_permission table:

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

#### PostgreSQL

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

#### Oracle

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
