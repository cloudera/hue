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

Click the **Hue Administration** icon in the top right navigation bar under your username.

## LDAP

[LDAP or PAM pass-through authentication with Hive or Impala and Impersonation
](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/).


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

**Programmatically**

When a Hue administrator loses their password, a more programmatic approach is required to secure the administrator again. Hue comes with a wrapper around the python interpreter called the “shell” command. It loads all the libraries required to work with Hue at a programmatic level. To start the Hue shell, type the following command from the Hue installation root.

If using CM:

    export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'`"

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

**Via a command**

Go on the Hue machine, then in the Hue home directory and either type:

To change the password of the currently logged in Unix user:

    build/env/bin/hue changepassword

### Reset an Admin

**Programmatically**

How to make a certain user a Hue admin

    build/env/bin/hue  shell

Then set these properties to true:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

**Via a command**

If you don't remember the admin username, create a new Hue admin (you will then also be able to login and could change the password of another user in Hue):

    build/env/bin/hue createsuperuser

<div class="note">
Above works with the `AllowFirstUserBackend`, it might be different if another backend is used.
</div>


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


### Limit users can login

    [desktop]
    [[ldap]]
    login_groups=ldap_grp1,ldap_grp2,ldap_grp3

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

  John Smith belonging to team A
  Helen Taylor belonging to team B

Assuming the following access requirements:

  Team A should be able to use Beeswax, but nothing else.
  Team B should only be able to see the Oozie dashboard with readonly permissions.

In Hue 2 the scenarios can be addressed more appropriately. Users can be imported from LDAP by clicking “Add/Sync LDAP user” in Useradmin > Users:

Similarly, groups can be imported from LDAP by clicking “Add/Sync LDAP group” in Useradmin > Groups.

If a previously imported user’s information was updated recently, the information in Hue will need to be resynchronized. This can be achieved through the LDAP sync feature:

Part A of the example can be addressed by explicitly allowing access Beeswax for Team A. This is managed in the “Groups” tab of the Useradmin app:

The Team A group can be edited by clicking on its name, where access privileges for the group are selectable. Here, the “beeswax.access” permission would be selected and the others would be unselected:


Part B of the example can be handled by explicitly defining access for Team B. This can be accomplished by following the same steps in part A, except for Team B. Every permission would be unselected except “oozie.dashboard_jobs_access”:

By explicitly setting the app level permissions, the apps that these users will be able to see will change. For instance, Helen, who is a member of Team B, will only see the Oozie app available:

### Programmatically

Set permissions to a group via a Bash shell:

    #!/bin/env bash

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

    password=$(cat /home/hadoop/hue-config/hue_access_admin.txt | sed -n 's/admin:(.*)/\1/p')

    curl ${protocol}://${host}:${port}/hue/accounts/login/?fromModal=true -o /dev/null -D - -c cookies.txt -s
    x_csrftoken=$(grep csrftoken cookies.txt | cut -f 7)

    curl -i -X POST ${protocol}://${host}:${port}/hue/accounts/login/?fromModal=true -d "username=${user}&password=${password}" -o /dev/null -D - -c cookies.txt -b cookies.txt -H "X-CSRFToken: ${x_csrftoken}" -s
    x_csrftoken=$(grep csrftoken cookies.txt | cut -f 7)

    curl -X POST ${protocol}://${host}:${port}/useradmin/groups/edit/${group_name}
    -d "csrfmiddlewaretoken=${x_csrftoken}&name=${group_name}&permissions=${permissions_id1}&permissions=${permissions_id2}&${list_of_users}&is_embeddable=true",
    -b cookies.txt -H "X-CSRFToken: ${x_csrftoken}"
