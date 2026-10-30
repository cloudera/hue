---
title: "Users"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

The User Admin application lets a superuser add, delete, and manage Hue
users and groups, and configure group permissions. Superusers can add
users and groups individually, or import them from an LDAP directory.
Group permissions define the Hue applications visible to group members
when they log into Hue and the application features available to them.

To open the User Admin application, click your username in the top right navigation bar, then click **Manage Users**.

## LDAP

Read how to use [LDAP or PAM pass-through authentication with Hive or Impala and impersonation](https://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/).

To restrict which LDAP groups can log in, see [Limit who can log in](#limit-who-can-log-in).


## Users

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

### Adding a User

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
<tr><td>E-mail address</td><td>The user's e-mail address. The e-mail address is used by the Editor to send users an e-mail message after a query has completed. If an e-mail address is not specified,
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


### Importing Users

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

### Syncing Users and Groups

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

**With a command**

Go to the Hue installation directory and run:

```bash
build/env/bin/hue changepassword [username]
```

When you omit the username, the command uses the currently logged in Unix user.

**With the Hue shell**

If a Hue administrator loses their password, use the Hue `shell` command. It is a wrapper around the Python interpreter that loads the libraries required to work with Hue. From the Hue installation directory, run:

```bash
build/env/bin/hue shell
```

The following script changes the password of a user named `example`. Run it in the Hue shell:

```python
from django.contrib.auth.models import User
user = User.objects.get(username='example')
user.set_password('some password')
user.save()
```

You can also run a script file (here `script.py`) with input redirection:

```bash
build/env/bin/hue shell < script.py
```

### Reset an admin

**With the Hue shell**

To make a user a Hue admin, start the shell:

```bash
build/env/bin/hue shell
```

Then set these properties:

```python
from django.contrib.auth.models import User

a = User.objects.get(username='hdfs')
a.is_staff = True
a.is_superuser = True
a.set_password('my_secret')
a.save()
```

**With a command**

If you do not remember the admin username, create a new Hue admin. You can then log in and change the password of another user in Hue:

```bash
build/env/bin/hue createsuperuser
```

> **Note:** This works with the `AllowFirstUserDjangoBackend` authentication backend. It can differ with another backend.

## Groups

Superusers can add and delete groups, configure group permissions, and assign users to group memberships.

### Adding a Group

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


### Limit who can log in

To allow only the users of some LDAP groups to log in, set `login_groups` in the `hue.ini`:

```ini
[desktop]
[[ldap]]
login_groups=ldap_grp1,ldap_grp2,ldap_grp3
```

### Importing Groups

1.  From the **Groups** tab, click **Add/sync LDAP group**.
2.  Click **Add/sync group**.


## Permissions

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

### Example

A company would like to use the following LDAP users and groups in Hue:

* John Smith belongs to team A.
* Helen Taylor belongs to team B.

Assuming the following access requirements:

* Team A can use Beeswax, but nothing else.
* Team B can only see the Oozie dashboard, with read-only permissions.

To implement these requirements, import the users from LDAP by clicking **Add/Sync LDAP user** in **Users**.

Similarly, import the groups from LDAP by clicking **Add/Sync LDAP group** in **Groups**.

If the information of a previously imported user changed in LDAP, resynchronize it with the LDAP sync feature.

For team A, explicitly allow access to Beeswax in the **Groups** tab of the User Admin application.

Click the name of the team A group to edit its permissions. Select the `beeswax.access` permission and unselect the others.


For team B, follow the same steps. Unselect every permission except `oozie.dashboard_jobs_access`.

With explicit application-level permissions, the users see different applications. For example, Helen, who belongs to team B, only sees the Oozie dashboard.

### Programmatically

To set the permissions of a group with a Bash script:

```bash
#!/usr/bin/env bash

set -eu

host="localhost"
port="8888"
credentials="/home/hadoop/hue-config/hue_access_admin.txt" # password file
user="admin"
protocol="http"
group_name="spark02-user"
permissions_id1="10" # jobbrowser.access
permissions_id2="18" # spark.access
list_of_users="members=10&members=9&members=4" # number here is an order number for a user in the list of users

password=$(sed -n 's/admin:\(.*\)/\1/p' "${credentials}")

curl ${protocol}://${host}:${port}/hue/accounts/login/?fromModal=true -o /dev/null -D - -c cookies.txt -s
x_csrftoken=$(grep csrftoken cookies.txt | cut -f 7)

curl -i -X POST ${protocol}://${host}:${port}/hue/accounts/login/?fromModal=true -d "username=${user}&password=${password}" -o /dev/null -D - -c cookies.txt -b cookies.txt -H "X-CSRFToken: ${x_csrftoken}" -s
x_csrftoken=$(grep csrftoken cookies.txt | cut -f 7)

curl -X POST ${protocol}://${host}:${port}/useradmin/groups/edit/${group_name} \
  -d "csrfmiddlewaretoken=${x_csrftoken}&name=${group_name}&permissions=${permissions_id1}&permissions=${permissions_id2}&${list_of_users}&is_embeddable=true" \
  -b cookies.txt -H "X-CSRFToken: ${x_csrftoken}"
```
