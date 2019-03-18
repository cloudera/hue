---
title: "Administration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

## Reference Architecture

A recommended setup consists in:

* 2 Hues and 1 Load Balancer
* Databases: MySQL InnoDB, PostgreSQL, Oracle
* Authentication: [LDAP or Username/Passord](#user-management)

### Monitoring

Performing a `GET /desktop/debug/is_alive` will return a 200 response if running.


### Load Balancers

Hue is often run with:

* Cherrypy with Httpd
* [Apache mod Python](http://gethue.com/how-to-run-hue-with-the-apache-server/)
* [NGINX](http://gethue.com/using-nginx-to-speed-up-hue-3-8-0/)

### Task Server

The task server is currently a work in progress to outsource all the blocking or resource intensive operations
outside of the API server. Follow (HUE-8738)[https://issues.cloudera.org/browse/HUE-8738) for more information
on when first usable task will be released.

Until then, here is how to try the task server service.

Make sure you have Rabbit MQ installed and running.

    sudo apt-get install rabbitmq-server -y


In hue.ini, telling the API server that the Task Server is available:

    [desktop]
    [[task_server]]
    enabled=true

Starting the  Task server:

    ./build/env/bin/celery worker -l info -A desktop

Running a test tasks:

    ./build/env/bin/hue shell

    from desktop.celery import debug_task

    debug_task.delay()
    debug_task.delay().get() # Works if result backend is setup and task_server is true in the hue.ini

Starting the Task Scheduler server:

    ./build/env/bin/celery -A core beat -l info

or when Django Celery Beat is enabled:

    ./build/env/bin/celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

### Proxy

A Web proxy lets you centralize all the access to a certain URL and prettify the address (e.g. ec2-54-247-321-151.compute-1.amazonaws.com --> demo.gethue.com).

Here is one way to do it with [Apache](http://gethue.com/i-put-a-proxy-on-hue/).

## Quick Start Wizard

The Quick Start wizard allows you to perform the following Hue setup
operations by clicking the tab of each step or sequentially by clicking
Next in each screen:

1.  **Check Configuration** validates your Hue configuration. It will
    note any potential misconfiguration and provide hints as to how to
    fix them. You can edit the configuration file described in the next
    section or use Cloudera Manager, if installed, to manage your
    changes.
2.  **Examples** contains links to install examples into the Hive,
    Impala, MapReduce, Spark, Oozie, Solr Dashboard and Pig Editor applications.
3.  **Users** contains a link to the User Admin application to create or
    import users and a checkbox to enable and disable collection of
    usage information.

## Configuration

Displays a list of the installed Hue applications and their
configuration. The location of the folder containing the Hue
configuration files is shown at the top of the page. Hue configuration
settings are in the hue.ini configuration file.

Click the tabs under **Configuration Sections and Variables** to see the
settings configured for each application. For information on configuring
these settings, see Hue Configuration in the Hue installation manual.


Hue ships with a default configuration that will work for
pseudo-distributed clusters.  If you are running on a real cluster, you must
make a few changes to the `hue.ini` configuration file (`/etc/hue/hue.ini` when installed from the
package version) or `pseudo-distributed.ini` in `desktop/conf` when in development mode).
The following sections describe the key configuration options you must make to configure Hue.


<div class="note">
To list all available configuration options, run:

    $ /usr/share/hue/build/env/bin/hue config_help | less

This commands outlines the various sections and options in the configuration,
and provides help and information on the default values.
</div>


<div class="note">
To view the current configuration from within Hue, open:

    http://<hue>/hue/dump_config
</div>

<div class="note">
Hue loads and merges all of the files with extension `.ini`
located in the `/etc/hue` directory.  Files that are alphabetically later
take precedence.
</div>

# Administration

Now that you've installed and started Hue, you can feel free to skip ahead
to the <<usage,Using Hue>> section. Administrators may want to refer to this
section for more details about managing and operating a Hue installation.


## Configuration Validation

Hue can detect certain invalid configuration.

To view the configuration of a running Hue instance, navigate to
`http://myserver:8888/hue/dump_config`, also accessible through the About
application.


## Server Logs

Displays the Hue Server log and allows you to download the log to your
local system in a zip file.

## Threads

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Threads page can be very helpful in debugging purposes. It includes a daemonic thread and the thread objects serving concurrent requests. The host name, thread name identifier and current stack frame of each are displayed. Those are useful when Hue “hangs”, sometimes in case of a request too CPU intensive. There is also a REST API to get the dump of Threads using 'desktop/debug/threads'

## Metrics

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Hue uses the **PyFormance** Python library to collect the metrics. These metrics are represented as gauge, counters, meter, rate of events over time, histogram, statistical distribution of values. A REST API endpoint '/desktop/metrics/' to get all the metrics dump as json is also exposed

The below metrics of most concern to us are displayed on the page:

- requests.active
- requests.exceptions
- requests.response-time
- threads.daemon
- threads.total
- users
- users.active

One of the most useful ones are the percentiles of response time of requests and the count of active users.
Admins can either filter a particular property in all the metrics or select a particular metric for all properties


## User management

The User Admin application lets a superuser add, delete, and manage Hue
users and groups, and configure group permissions. Superusers can add
users and groups individually, or import them from an LDAP directory.
Group permissions define the Hue applications visible to group members
when they log into Hue and the application features available to them.

Click the **User Admin** icon in the top right navigation bar under your username.

### LDAP

[LDAP or PAM pass-through authentication with Hive or Impala and Impersonation
](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/).


### Users

The User Admin application provides two levels of user privileges:
superusers and users.

-   Superusers — The first user who logs into Hue after its initial
    installation becomes the first superuser. Superusers have
    permissions to perform administrative functions:
    -   Add and delete users
    -   Add and delete groups
    -   Assign permissions to groups
    -   Change a user into a superuser
    -   Import users and groups from an LDAP server

-   Users can change their name, e-mail address, and password and log
    in to Hue and run Hue applications, subject to the permissions
    provided by the Hue groups to which they belong.

#### Adding a User

1.  In the **User Admin** page, click **Add User**.
2.  In the **Credentials** screen, add required information about the
    user. Once you provide the required information you can click the
    wizard step tabs to set other information.

 <table>
<tr><td>Username</td><td>  A user name that contains only letters, numbers, and underscores;
    blank spaces are not allowed and the name cannot begin with a
    number. The user name is used to log into Hue and in file
    permissions and job submissions. This is a required field.
</td></tr>
<tr><td>Password and Password confirmation</td><td>    A password for the user. This is a required field.</td></tr>
<tr><td>Create home directory</td><td>   Indicate whether to create a directory named /user/username in HDFS.
    For non-superusers, the user and group of the directory are
    username. For superusers, the user and group are username and
    supergroup.</td></tr></table>



3.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
4.  In the **Names and Groups** screen, add optional information.

<table>
<tr><td>First name and Last name</td><td> The user's first and last name.
</td></tr>
<tr><td>E-mail address</td><td>The user's e-mail address. The e-mail address is used by the Job
    Designer and Beeswax applications to send users an e-mail message
    after certain actions have occurred. The Job Designer sends an
    e-mail message after a job has completed. Beeswax sends a message
    after a query has completed. If an e-mail address is not specified,
    the application will not attempt to email the user.</td></tr>
<tr><td>Groups</td><td> The groups to which the user belongs. By default, a user is assigned
    to the **default** group, which allows access to all applications.
    See [Permissions](#permissions).</td></tr></table>


5.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
6.  In the **Advanced** screen, add status information.

<table>
<tr><td>Active</td><td> Indicate that the user is enabled and allowed to log in. Default: checked.</td></tr>
<tr><td>Superuser status</td><td> Assign superuser privileges to the user.</td></tr></table>

7.  Click **Add User** to save the information you specified and close
    the **Add User** wizard.

#### Deleting a User

1.  Check the checkbox next to the user name and click **Delete**.
2.  Click **Yes** to confirm.

#### Editing a User

1.  Click the user you want to edit in the **Hue Users** list.
2.  Make the changes to the user and then click **Update user**.

#### Importing Users from an LDAP Directory

**Note**:

Importing users from an LDAP directory does not import any password
information. You must add passwords manually in order for a user to log
in.

To add a user from an external LDAP directory:

1.  Click **Add/sync LDAP user**.
2.  Specify the user properties:

<table>
<tr><td>Username</td><td>The user name.</td></tr>
<tr><td>Distinguished name</td><td>Indicate that Hue should use a full distinguished name for the user.
    This imports the user's first and last name, username, and email,
    but does not store the user password.</td></tr>
    <tr><td>Create home directory</td><td> Indicate that Hue should create a home directory for the user in
    HDFS.</td></tr></table>


3.  Click **Add/sync user**.

    If the user already exists in the User Admin, the user information
    in User Admin is synced with what is currently in the LDAP
    directory.

#### Syncing Users and Groups with an LDAP Directory

You can sync the Hue user database with the current state of the LDAP
directory using the **Sync LDAP users/groups** function. This updates
the user and group information for the already imported users and
groups. It does not import any new users or groups.

1.  Click **Sync LDAP users/groups**.
2.  The **Create Home Directories** checkbox creates home directories in
    HDFS for existing imported members that don't have home directories.
3.  In the **Sync LDAP users and groups** dialog, click **Sync** to
    perform the sync.

### Reset a password

**Programmatically**

When a Hue administrator loses their password, a more programmatic approach is required to secure the administrator again. Hue comes with a wrapper around the python interpreter called the “shell” command. It loads all the libraries required to work with Hue at a programmatic level. To start the Hue shell, type the following command from the Hue installation root.

Then:

    cd /usr/lib/hue (or /opt/cloudera/parcels/CDH-XXXXX/share/hue if using parcels and CM)
    build/env/bin/hue shell

The following is a small script, that can be executed within the Hue shell, to change the password for a user named “example”:

    from django.contrib.auth.models import User
    user = User.objects.get(username='example')
    user.set_password('some password')
    user.save()

The script can also be invoked in the shell by using input redirection (assuming the script is in a file named script.py):

    build/env/bin/hue shell < script.py

How to make a certain user a Hue admin

    build/env/bin/hue  shell

Then set these properties to true:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

** Via a command**

Go on the Hue machine, then in the Hue home directory and either type:

To change the password of the currently logged in Unix user:

    build/env/bin/hue changepassword

If you don't remember the admin username, create a new Hue admin (you will then also be able to login and could change the password of another user in Hue):

    build/env/bin/hue createsuperuser


[Read more about it here](http://gethue.com/password-management-in-hue/).

<div class="note">
Above works with the `AllowFirstUserBackend`, it might be different if another backend is used.
</div>


### Groups

Superusers can add and delete groups, configure group permissions, and
assign users to group memberships.

#### Adding a Group

You can add groups, and delete the groups you've added. You can also
import groups from an LDAP directory.

1.  In the **User Admin** window, click **Groups** and then click **Add
    Group**.
2.  Specify the group properties:

<table>
<tr><td>Name</td><td> The name of the group. Group names can only be letters, numbers, and
    underscores; blank spaces are not allowed.</td></tr>
<tr><td>Members</td><td>The users in the group. Check user names or check Select all.</td></tr>
    <tr><td>Permissions</td><td>The applications the users in the group can access. Check
    application names or check Select all.</td></tr></table>

3.  Click **Add group**.

#### Adding Users to a Group

1.  In the **User Admin** window, click **Groups**.
2.  Click the group.
3.  To add users to the group, check the names in the list provided or
    check **Select All**.
4.  Click **Update group**.

#### Deleting a Group

1.  Click **Groups**.
2.  Check the checkbox next to the group and click **Delete**.
3.  Click **Yes** to confirm.

#### Limit users can login only if they are belong to one of listed LDAP groups

    [desktop]
    [[ldap]]
    login_groups=ldap_grp1,ldap_grp2,ldap_grp3

#### Importing Groups from an LDAP Directory

1.  From the **Groups** tab, click **Add/sync LDAP group**.
2.  Specify the group properties:

<table>
<tr><td>Name</td><td> The name of the group.</td></tr>
<tr><td>Distinguished name</td><td> Indicate that Hue should use a full distinguished name for the
    group.</td></tr>
    <tr><td>Import new members</td><td>  Indicate that Hue should import the members of the group.</td></tr>
        <tr><td>Import new members from all subgroups</td><td>
    Indicate that Hue should import the members of the subgroups.</td></tr>
            <tr><td>Create home directories</td><td> Indicate that Hue should create home directories in HDFS for the
    imported members.</td></tr>
</table>

3.  Click **Add/sync group**.

<a id="permissions"></a>
Permissions
-----------

Permissions for Hue applications are granted to groups, with users
gaining permissions based on their group membership. Group permissions
define the Hue applications visible to group members when they log into
Hue and the application features available to them.

1.  Click **Permissions**.
2.  Click the application for which you want to assign permissions.
3.  Check the checkboxes next to the groups you want to have permission
    for the application. Check **Select all** to select all groups.
4.  Click **Update permission**. The new groups will appear in the
    Groups column in the **Hue Permissions** list.

[Read more about it here](http://gethue.com/how-to-manage-permissions-in-hue/).

## Process Hierarchy

A script called `supervisor` manages all Hue processes. The supervisor is a
watchdog process -- its only purpose is to spawn and monitor other processes.
A standard Hue installation starts and monitors the following processes:

* `runcpserver` - a web server based on CherryPy that provides the core web
functionality of Hue

If you have installed other applications into your Hue instance, you may see
other daemons running under the supervisor as well.

You can see the supervised processes running in the output of `ps -f -u hue`:

    UID        PID  PPID  C STIME TTY          TIME CMD
    hue       8685  8679  0 Aug05 ?        00:01:39 /usr/share/hue/build/env/bin/python /usr/share/hue/build/env/bin/desktop runcpserver

Note that the supervisor automatically restarts these processes if they fail for
any reason. If the processes fail repeatedly within a short time, the supervisor
itself shuts down.

## Logging

The Hue logs are found in `/var/log/hue`, or in a `logs` directory under your
Hue installation root. Inside the log directory you can find:

* An `access.log` file, which contains a log for all requests against the Hue
web server.
* A `supervisor.log` file, which contains log information for the supervisor
process.
* A `supervisor.out` file, which contains the stdout and stderr for the
supervisor process.
* A `.log` file for each supervised process described above, which contains
the logs for that process.
* A `.out` file for each supervised process described above, which contains
the stdout and stderr for that process.

If users on your cluster have problems running Hue, you can often find error
messages in these log files. If you are unable to start Hue from the init
script, the `supervisor.log` log file can often contain clues.

### Viewing Recent Log Messages

In addition to logging `INFO` level messages to the `logs` directory, the Hue
web server keeps a small buffer of log messages at all levels in memory. You can
view these logs by visiting `http://myserver:8888/hue/logs`. The `DEBUG` level
messages shown can sometimes be helpful in troubleshooting issues.

## Troubleshooting

To troubleshoot why Hue is slow or consuming high memory, admin can enable instrumentation by setting the `instrumentation` flag to True.
 <pre>
[desktop]
instrumentation=true
</pre>
 If `django_debug_mode` is enabled, instrumentation is automatically enabled. This flag appends the response time and the total peak memory used since Hue started for every logged request.

### Instrumentation enabled

<pre>
[17/Apr/2018 15:18:43 -0700] access       INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" `returned in 97ms (mem: 135mb)`
</pre>

### Instrumentation not enabled

<pre>
[23/Apr/2018 10:59:01 -0700] INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" returned in 88ms
</pre>

## Database

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