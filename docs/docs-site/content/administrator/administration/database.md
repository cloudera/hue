---
title: "Database"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Hue stores a small amount of data in a SQL database: user accounts, query history, saved documents, and sharing permissions.

By default, Hue uses an embedded SQLite database so that it starts without setup. SQLite does not support concurrent writes well, so you can get `database is locked` errors. Use another database for anything beyond a test.

This page describes how to configure Hue with another database and how to operate it.

## Prerequisites

* A running MySQL, MariaDB, PostgreSQL, or Oracle server.
* The Python client library of your database installed in the Hue virtual environment. See [Database dependencies](/administrator/installation/dependencies/#database).
* The path to your `hue.ini`. Hue loads all the `.ini` files of the `desktop/conf` directory (or of the `HUE_CONF_DIR` directory), and later files in alphabetical order take precedence.

> **Note:** If you use an external database, upgrades can require more manual steps.

The settings of the `[[database]]` section of the `hue.ini` are:

| Setting | Description |
|---|---|
| `engine` | `mysql` (also for MariaDB), `postgresql_psycopg2`, `oracle`, or `sqlite3` (default) |
| `host` | Database server host |
| `port` | Database server port |
| `user` | Database user |
| `password` | Database password. Alternatively, set `password_script` to a script that prints it. |
| `name` | Database name. For `sqlite3`, the path of the file. |
| `options` | Extra connection options |
| `conn_max_age` | Seconds to keep connections open (default `0`) |

Run `build/env/bin/hue config_help | less` to list all the options.

## Configure another database

The steps below use `/usr/share/hue` as the Hue installation directory. Replace it with yours.

### MySQL

1. Create a database and a user in MySQL:

   ```sql
   CREATE DATABASE hue;
   CREATE USER 'hue'@'localhost' IDENTIFIED BY 'secretpassword';
   GRANT ALL ON hue.* TO 'hue'@'localhost';
   ```

2. Stop Hue if it is running.

3. To keep your existing data, dump it to a file. The `.json` extension is required:

   ```bash
   /usr/share/hue/build/env/bin/hue dumpdata > /tmp/hue_database_dump.json
   ```

4. Open the `hue.ini` file in a text editor. Under `[desktop]`, add the options below directly after the `[[database]]` line, and modify them for your setup:

   ```ini
   [desktop]
   [[database]]
   host=localhost
   port=3306
   engine=mysql
   user=hue
   password=secretpassword
   name=hue
   ```

5. As the Hue user, create the database tables:

   ```bash
   /usr/share/hue/build/env/bin/hue migrate
   ```

6. If you dumped your data, remove the content types created by the migration, then load the dump:

   ```bash
   mysql -uhue -p -e "DELETE FROM hue.django_content_type;"
   /usr/share/hue/build/env/bin/hue loaddata /tmp/hue_database_dump.json
   ```

You can now start the Hue server as usual.

### PostgreSQL

1. Create a database and a user:

   ```sql
   CREATE USER hue WITH PASSWORD 'secretpassword';
   CREATE DATABASE hue OWNER hue;
   ```

2. Set the `[[database]]` section of the `hue.ini`:

   ```ini
   [desktop]
   [[database]]
   host=localhost
   port=5432
   engine=postgresql_psycopg2
   user=hue
   password=secretpassword
   name=hue
   ```

3. Stop Hue, dump your data as in the MySQL steps, then create the tables:

   ```bash
   /usr/share/hue/build/env/bin/hue migrate
   ```

4. To load a dump, log on to PostgreSQL and drop the foreign key constraint from `auth_permission`:

   ```bash
   psql -h localhost -U hue -d hue
   ```

   ```sql
   \d auth_permission;
   ALTER TABLE auth_permission DROP CONSTRAINT content_type_id_refs_id_<id value>;
   ```

5. Delete the contents of `django_content_type`:

   ```sql
   TRUNCATE django_content_type CASCADE;
   ```

6. Load the data, then add the foreign key back:

   ```bash
   /usr/share/hue/build/env/bin/hue loaddata /tmp/hue_database_dump.json
   ```

   ```sql
   ALTER TABLE auth_permission ADD FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
   ```

### Oracle

To migrate data to Oracle, delete all content from the Oracle tables after running `migrate` and before loading the data:

Log on to Oracle:

```bash
su - oracle
sqlplus / as sysdba
```

Grant a quota to the tablespace where tables are created (the default is SYSTEM). For example:

```sql
ALTER USER hue quota 100m on system;
```

Log on as the hue:

```bash
sqlplus hue/<hue password>
```

Create a spool script that creates a delete script to clean the content of all tables.

```bash
vi spool_statements.ddl
```

Save in spool_statements.ddl (which generates delete_from_tables.ddl)

```sql
spool delete_from_tables.ddl
set pagesize 100;
SELECT 'DELETE FROM ' || table_name || ';' FROM user_tables;
commit;
spool off
quit
```

Run both scripts:

```text
-- Create delete_from_tables.ddl
sqlplus hue/<your hue password> < spool_statements.ddl

-- Run delete_from_tables.ddl
sqlplus hue/<your hue password> < delete_from_tables.ddl
```

#### RAC

Set the database in the `[[database]]` section of the `hue.ini`:

```ini
[desktop]
[[database]]
engine=oracle
host=<oracle host>
port=<port>
user=<username>
password=<password>
name=<service name or SID of one of the instances>
```

You can also use the Oracle service name with `host` and `port` set and `name=<host>:<port>/<service_name>`.

If this does not work for your RAC cluster, set `port=0` and use a full connect descriptor as the name:

```ini
[desktop]
[[database]]
engine=oracle
port=0
user=<username>
password=<password>
name=(DESCRIPTION=(LOAD_BALANCE=off)(FAILOVER=on)(CONNECT_TIMEOUT=5)(TRANSPORT_CONNECT_TIMEOUT=3)(RETRY_COUNT=3)(ADDRESS=(PROTOCOL=TCP)(HOST=<scan ip>)(PORT=<port>))(CONNECT_DATA=(SERVICE_NAME=<service name>)))
```

Hue sets `options={"threaded": True}` by default for Oracle, which is required in a multithreaded environment.

## Operation

### Inspect the database

Use the standard shell of your database, the Hue [SQL Editor](/administrator/configuration/connectors/#databases), or the Django database shell:

```bash
/usr/share/hue/build/env/bin/hue dbshell
```

> **Warning:** Avoid modifying the database directly. Use direct access only for management or troubleshooting.

### Back up the database

Back up the database on a regular schedule, and before any upgrade or data change. Use the standard backup tools of your database, or dump the records as described in [Migrate to another database](#migrate-to-another-database).

### Clean up the database

Too many entries in some tables, such as documents, cause performance issues. The Hue configuration check warns superusers about this. Log in as a superuser and open **Hue Administration** to see it.

![Config check for too many documents](https://cdn.gethue.com/uploads/2019/03/Doc2CountCheck.png)

To clean up old entries, go to the Hue installation directory and run:

```bash
./build/env/bin/hue desktop_document_cleanup
```

### Migrate to another database

You can migrate the existing data when you change databases, for example from SQLite to MySQL or PostgreSQL.

1. Stop Hue and dump the data with `dumpdata`, as in the [MySQL](#mysql) steps.
2. Edit the dump file and remove all the objects whose `model` is `useradmin.userprofile`. For example:

   ```bash
   grep -c useradmin.userprofile /tmp/hue_database_dump.json
   ```

   ```json
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
   ```

3. Configure the new database in the `hue.ini` as described above, and run `migrate`.
4. Load the data as described for your database.
5. Start Hue and check on the Hue home page that all the documents were migrated.

#### MySQL foreign key

If loading the data fails on MySQL, drop the foreign key constraint from `hue.auth_permission` before the load and add it back after.

1. Find the constraint name:

   ```sql
   SHOW CREATE TABLE hue.auth_permission;
   ```

   In the output, find the name in the `CONSTRAINT` clause, for example `content_type_id_refs_id_d043b34a`.

2. Drop the constraint, using your constraint name:

   ```sql
   ALTER TABLE hue.auth_permission DROP FOREIGN KEY content_type_id_refs_id_d043b34a;
   ```

3. Delete the contents of `django_content_type`:

   ```sql
   DELETE FROM hue.django_content_type;
   ```

4. Load the data, then add the foreign key back:

   ```sql
   ALTER TABLE hue.auth_permission ADD FOREIGN KEY (content_type_id) REFERENCES django_content_type (id);
   ```
