---
title: "User Management"
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


## Groups

Superusers can add and delete groups, configure group permissions, and
assign users to group memberships.

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

[Read more about it here](http://gethue.com/how-to-manage-permissions-in-hue/).
