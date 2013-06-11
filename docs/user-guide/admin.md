
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

User Admin
==========

The User Admin application lets a superuser add, delete, and manage Hue
users and groups, and configure group permissions. Superusers can add
users and groups individually, or import them from an LDAP directory.
Group permissions define the Hue applications visible to group members
when they log into Hue and the application features available to them.

Starting User Admin
-------------------

Click the **User Admin** icon (![image](images/icon_useradmin_24.png))
in the navigation bar at the top of the Hue browser page. The Hue Users
page opens.

Users
-----

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

-   Users — can change their name, e-mail address, and password and log
    in to Hue and run Hue applications, subject to the permissions
    provided by the Hue groups to which they belong.

### Adding a User

1.  In the **User Admin** page, click **Add User**.
2.  In the **Credentials** screen, add required information about the
    user. Once you provide the required information you can click the
    wizard step tabs to set other information.

    **Username**

    A user name that contains only letters, numbers, and underscores;
    blank spaces are not allowed and the name cannot begin with a
    number. The user name is used to log into Hue and in file
    permissions and job submissions. This is a required field.

    **Password** and **Password confirmation**

    A password for the user. This is a required field.

    **Create home directory**

    Indicate whether to create a directory named /user/username in HDFS.
    For non-superusers, the user and group of the directory are
    username. For superusers, the user and group are username and
    supergroup.

3.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
4.  In the **Names and Groups** screen, add optional information.

    **First name** and **Last name**

    The user's first and last name.

    **E-mail address**

    The user's e-mail address. The e-mail address is used by the Job
    Designer and Beeswax applications to send users an e-mail message
    after certain actions have occurred. The Job Designer sends an
    e-mail message after a job has completed. Beeswax sends a message
    after a query has completed. If an e-mail address is not specified,
    the application will not attempt to email the user.

    **Groups**

    The groups to which the user belongs. By default, a user is assigned
    to the **default** group, which allows access to all applications.
    See [Managing Application Permissions](#topic_11_4).

5.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
6.  In the **Advanced** screen, add status information.

    **Active**

    Indicate that the user is enabled and allowed to log in.

    Default: checked.

    **Superuser status**

    Assign superuser privileges to the user.

7.  Click **Add User** to save the information you specified and close
    the **Add User** wizard.

### Deleting a User

1.  Check the checkbox next to the user name and click **Delete**.
2.  Click **Yes** to confirm.

### Editing a User

1.  Click the user you want to edit in the **Hue Users** list.
2.  Make the changes to the user and then click **Update user**.

### Importing Users from an LDAP Directory

Hue must be configured to use an external LDAP directory (OpenLDAP or
Active Directory). See Hue Installation in [CDH4
Installation](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/CDH4-Installation-Guide.html).

![image](images/note.jpg) **Note**:

Importing users from an LDAP directory does not import any password
information. You must add passwords manually in order for a user to log
in.

To add a user from an external LDAP directory:

1.  Click **Add/sync LDAP user**.
2.  Specify the user properties:

    **Username**

    The user name.

    **Distinguished name**

    Indicate that Hue should use a full distinguished name for the user.
    This imports the user's first and last name, username, and email,
    but does not store the user password.

    **Create home directory**

    Indicate that Hue should create a home directory for the user in
    HDFS.

3.  Click **Add/sync user**.

    If the user already exists in the User Admin, the user information
    in User Admin is synced with what is currently in the LDAP
    directory.

### Syncing Users and Groups with an LDAP Directory

You can sync the Hue user database with the current state of the LDAP
directory using the **Sync LDAP users/groups** function. This updates
the user and group information for the already imported users and
groups. It does not import any new users or groups.

1.  Click **Sync LDAP users/groups**.
2.  The **Create Home Directories** checkbox creates home directories in
    HDFS for existing imported members that don't have home directories.
3.  In the **Sync LDAP users and groups** dialog, click **Sync** to
    perform the sync.

Groups
------

Superusers can add and delete groups, configure group permissions, and
assign users to group memberships.

### Adding a Group

You can add groups, and delete the groups you've added. You can also
import groups from an LDAP directory.

1.  In the **User Admin** window, click **Groups** and then click **Add
    Group**.
2.  Specify the group properties:

    **Name**

    The name of the group. Group names can only be letters, numbers, and
    underscores; blank spaces are not allowed.

    **Members**

    The users in the group. Check user names or check **Select all**.

    **Permissions**

    The applications the users in the group can access. Check
    application names or check **Select all**.

3.  Click **Add group**.

### Adding Users to a Group

1.  In the **User Admin** window, click **Groups**.
2.  Click the group.
3.  To add users to the group, check the names in the list provided or
    check **Select All**.
4.  Click **Update group**.

### Deleting a Group

1.  Click **Groups**.
2.  Check the checkbox next to the group and click **Delete**.
3.  Click **Yes** to confirm.

### Importing Groups from an LDAP Directory

1.  From the **Groups** tab, click **Add/sync LDAP group**.
2.  Specify the group properties:

    **Name**

    The group name.

    **Distinguished name**

    Indicate that Hue should use a full distinguished name for the
    group.

    **Import new members**

    Indicate that Hue should import the members of the group.

    **Import new members from all subgroups**

    Indicate that Hue should import the members of the subgroups.

    **Create home directories**

    Indicate that Hue should create home directories in HDFS for the
    imported members.

3.  Click **Add/sync group**.

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
