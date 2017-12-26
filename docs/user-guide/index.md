
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>
<link rel="stylesheet" href="bootplus.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>


# Hue User Guide


<div class="row-fluid">
  <div class="span3">

[TOC]

   </div>
   <div class="span9">

## Concept
Hue consists in 4 apps in a single page interface that allow the users to perform its data
analyzes without losing any context.

Each app of Hue can be extended to support your own languages or apps.

### Interface
#### Top search
#### Left assist
#### Right assist
#### Sample popup
#### Charting
The SDK will be clarified in the upcoming charting revamp.

### Admin
Quick Start Wizard
------------------

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
4.  **Go!** - displays the Hue home screen, which contains links to the
    different categories of applications supported by Hue: Query,
    Hadoop, and Workflow.

Configuration
-------------

Displays a list of the installed Hue applications and their
configuration. The location of the folder containing the Hue
configuration files is shown at the top of the page. Hue configuration
settings are in the hue.ini configuration file.

Click the tabs under **Configuration Sections and Variables** to see the
settings configured for each application. For information on configuring
these settings, see Hue Configuration in the Hue installation manual.

Server Logs
-----------

Displays the Hue Server log and allows you to download the log to your
local system in a zip file.


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

<table>
<tr><td>Name</td><td> The name of the group. Group names can only be letters, numbers, and
    underscores; blank spaces are not allowed.</td></tr>
<tr><td>Members</td><td>The users in the group. Check user names or check Select all.</td></tr>
    <tr><td>Permissions</td><td>The applications the users in the group can access. Check
    application names or check Select all.</td></tr></table>

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

<table>
<tr><td>Name</td><td> The name of the group.</td></tr>
<tr><td>Distinguished name</td><td> Indicate that Hue should use a full distinguished name for the
    group.</td></tr>
    <tr><td>Import new members</td><td>  Indicate that Hue should import the members of the group.</td></tr>
        <tr><td>Import new members from all subgroups</td><td>
    Indicate that Hue should import the members of the subgroups.</td></tr>
            <tr><td>Create home directories</td><td> Indicate that Hue should create home directories in HDFS for the
    imported members.</td></tr></table>

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


### Importer

### Documents
#### Sharing
#### Import / Export

## Editors
The goal of Hue’s Editor is to make data querying easy and productive.

It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.

#### Languages
#### Hive
Beeswax
=======

The Beeswax application enables you to perform queries on Apache Hive, a
data warehousing system designed to work with Hadoop. For information
about Hive, see [Hive
Documentation](http://archive.cloudera.com/cdh4/cdh/4/hive/). You can
create Hive databases, tables and partitions, load data, create, run,
and manage queries, and download the results in a Microsoft Office Excel
worksheet file or a comma-separated values file.

Beeswax and Hive Installation and Configuration
-----------------------------------------------

Beeswax is installed and configured as part of Hue. For information
about installing and configuring Hue, see the Hue Installation
manual.

Beeswax assumes an existing Hive installation. The Hue installation
instructions include the configuration necessary for Beeswax to access
Hive. You can view the current Hive configuration from the **Settings**
tab in the Beeswax application.

By default, a Beeswax user can see the saved queries for all users -
both his/her own queries and those of other Beeswax users. To restrict
viewing saved queries to the query owner and Hue administrators, set the
share\_saved\_queries property under the [beeswax] section in the Hue
configuration file to false.

### Running Queries

![image](images/note.jpg) **Note**: To run a query, you must be logged
in to Hue as a user that also has a Unix user account on the remote
server.

1.  To execute a portion of the query, highlight one or more query
    statements.
2.  Click **Execute**. The Query Results window appears with the results
    of your query.
    -   To view a log of the query execution, click **Log** at the top
        of the results display. You can use the information in this tab
        to debug your query.
    -   To view the query that generated these results, click **Query**
        at the top of the results display.
    -   To view the columns of the query, click **Columns**.
    -   To return to the query in the Query Editor, click **Unsaved
        Query**.

3.  If there are multiple statements in the query, click Next in the
    Multi-statement query pane to execute the remaining statements.

![image](images/note.jpg) **Note**: Under **MR JOBS**, you can view any
MapReduce jobs that the query generated.

### Downloading and Saving Query Results

![image](images/important.jpg) **Important**:

-   You can only save results to a file when the results were generated
    by a MapReduce job.
-   This is the preferred way to save when the result is large (for
    example \> 1M rows).

1.  Do any of the following to download or save the query results:
    -   Click **Download as CSV** to download the results in a
        comma-separated values file suitable for use in other
        applications.
    -   Click **Download as XLS** to download the results in a Microsoft
        Office Excel worksheet file.
    -   Click **Save** to save the results in a table or HDFS file.
        -   To save the results in a new table, select **In a new
            table**, enter a table name, and then click **Save**.
        -   To save the results in an HDFS file, select **In an HDFS
            directory**, enter a path and then click **Save**. You can
            then download the file with [File Browser](../filebrowser.html).

<a id="advancedQuerySettings"></a>
### Advanced Query Settings

The pane to the left of the Query Editor lets you specify the following
options:


<table>
<tr><td>DATABASE</td><td>The database containing the table definitions.</td></tr>
<tr><td>SETTINGS</td><td>Override the Hive and Hadoop default settings. To configure a new
setting:

<ol>
<li> Click Add.
<li> For Key, enter a Hive or Hadoop configuration variable name.
<li> For Value, enter the value you want to use for the variable.

For example, to override the directory where structured Hive query logs
are created, you would enter hive.querylog.location for Key, and a
path for Value.
</ol>

To view the default settings, click the Settings tab at the top of
the page. For information about Hive configuration variables, see:
[http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration](http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration).
For information about Hadoop configuration variables, see:
[http://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml](http://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml).</td></tr>
<tr><td>FILE RESOURCES</td><td>Make files locally accessible at query execution time available on the
Hadoop cluster. Hive uses the Hadoop Distributed Cache to distribute the
added files to all machines in the cluster at query execution time.

<ol>
<li>  Click Add to configure a new setting.
<li>   From the Type drop-down menu, choose one of the following:
<ul>
   <li>jar - Adds the specified resources to the Java classpath.
   <li>archive - Unarchives the specified resources when
        distributing them.
    <li>file - Adds the specified resources to the distributed
        cache. Typically, this might be a transform script (or similar)
        to be executed.

<li>   For Path, enter the path to the file or click
    ![image](images/browse.png) to browse and select the file.
</ol>

![image](images/note.jpg) Note: It is not necessary to specify files
used in a transform script if the files are available in the same path
on all machines in the Hadoop cluster.</td></tr>
<tr><td>USER-DEFINED FUNCTIONS</td><td>Specify user-defined functions. Click Add to configure a new
setting. Specify the function name in the Name field, and specify
the class name for Classname.

You *must* specify a JAR file for the user-defined functions in FILE RESOURCES.

To include a user-defined function in a query, add a $ (dollar sign)
before the function name in the query. For example, if MyTable is a
user-defined function name in the query, you would type: SELECT $MyTable
</td></tr>
<tr><td>PARAMETERIZATION</td><td>Indicate that a dialog box should display to enter parameter values when
a query containing the string $parametername is executed. Enabled by
default.</td></tr>
</table>

#### Autocomplete
#### Syntax checker
#### Query Assist
#### Risk Alerts
#### Presentation
#### SDK


## Dashboards
Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.

#### SDK


## Browsers
Hue’s Browsers powers your Data Catalog. They let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.

### File Browser

<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

File Browser
============

The File Browser application lets you browse and manipulate files and
directories in the Hadoop Distributed File System (HDFS), S3 or ADLS.
With File Browser, you can:

-   Create files and directories, upload and download files, upload zip
    archives, and rename, move, and delete files and directories. You
    can also change a file's or directory's owner, group, and
    permissions. See [Files and Directories](#filesAndDirectories).
-   Search for files, directories, owners, and groups. See [Searching
    for Files and Directories](#searching).
-   View and edit files as text or binary. See [Viewing and Editing
    Files](#viewAndEdit).

File Browser Installation and Configuration
-------------------------------------------

File Browser is one of the applications installed as part of Hue. For
information about installing and configuring Hue, see the Hue Installation
manual.

Starting File Browser
---------------------

<a id="fileAndDirectories"></a>
Files and Directories
---------------------

You can use File Browser to view the input and output files of your
MapReduce jobs. Typically, you can save your output files in /tmp or in
your home directory if your system administrator set one up for you. You
must have the proper permissions to manipulate other user's files.

### Creating Directories

1.  In the File Browser window, select **New > Directory**.
2.  In the **Create Directory** dialog box, enter a directory name and
    then click **Submit**.

### Changing Directories

-   Click the directory name or parent directory dots in the **File
    Browser** window.
-   Click the ![image](images/edit.png) icon, type a directory name, and
    press **Enter**.

To change to your home directory, click **Home** in the path field at
the top of the **File Browser** window.

![image](images/note.jpg) **Note**:

The **Home** button is disabled if you do not have a home directory. Ask
a Hue administrator to create a home directory for you.

### Creating Files

1.  In the File Browser window, select **New > File**.
2.  In the **Create File** dialog box, enter a file name and then click
    **Submit**.


<a id="uploadingFiles"></a>
### Uploading Files

You can upload text and binary files to the HDFS.

1.  In the **File Browser** window, browse to the directory where you
    want to upload the file.
2.  Select **Upload \> Files**.
3.  In the box that opens, click **Upload a File** to browse to and
    select the file(s) you want to upload, and then click **Open**.

### Copying a File

1.  In the **File Browser** window, check the checkbox next to the file
    you want to copy.
2.  Click the ![image](images/copy.png) Copy button.

### Downloading Files

You can download text and binary files to the HDFS.

1.  In the **File Browser** window, check the checkbox next to the file
    you want to download.
2.  Click the **Download** button.

### Uploading Zip Archives

You can upload zip archives to the HDFS. The archive is uploaded and
extracted to a directory named archivename.

1.  In the **File Browser** window, browse to the directory where you
    want to upload the archive.
2.  Select **Upload > Zip file**.
3.  In the box that opens, click **Upload a zip file** to browse to and
    select the archive you want to upload, and then click **Open**.

### Trash Folder

File Browser supports the HDFS trash folder (*home directory*/.Trash) to
contain files and directories before they are permanently deleted. Files
in the folder have the full path of the deleted files (in order to be
able to restore them if needed) and checkpoints. The length of time a
file or directory stays in the trash depends on HDFS properties.

**Open**

1.  In the **File Browser** window, click ![image](images/fbtrash.png).

**Move Files and Directories To**

1.  In the **File Browser** window, check the checkbox next to one or
    more files and directories.
2.  Select **Delete > Move to trash**.

**Empty**

1.  In the **File Browser** window, click ![image](images/fbtrash.png).
2.  Click **Empty**.

### Renaming, Moving, Deleting, and Restoring Files and Directories


**Rename**

1.  In the **File Browser** window, check the checkbox next to the file
    or directory you want to rename.
2.  Click the **Rename** button.
3.  Enter the new name and then click **Submit**.

**Move**

1.  In the **File Browser** window, check the checkbox next to the file
    or directory you want to move.
2.  Click the **Move** button.
3.  In the **Move** dialog box, browse to or type the new directory, and
    then click **Submit**.

**Delete**

1.  In the **File Browser** window, check the checkbox next to the file
    or directory you want to delete. If you select a directory, all of
    the files and subdirectories contained within that directory are
    also deleted.
2.  Choose one of the following:
    -   **Delete > Move to trash**
    -   **Delete > Delete forever**

3.  Click **Yes** to confirm. When you move a file to trash it is stored
    in the .Trash folder in your home directory.

**Restore**

1.  In the **File Browser** window, open the .Trash folder.
2.  Navigate to the folder containing the file you want to restore.
3.  Check the checkbox next to the file.
4.  Click **Restore**.

### Changing a File's or Directory's Owner, Group, or Permissions

![image](images/note.jpg) **Note**:

Only the Hadoop superuser can change a file's or directory's owner,
group, or permissions. The user who starts Hadoop is the Hadoop
superuser. The Hadoop superuser account is not necessarily the same as a
Hue superuser account. If you create a Hue user (in User Admin) with the
same user name and password as the Hadoop superuser, then that Hue user
can change a file's or directory's owner, group, or permissions.

**Owner or Group**

1.  In the **File Browser** window, check the checkbox next to the
    select the file or directory whose owner or group you want to
    change.
2.  Choose **Change Owner/Group** from the Options menu.
3.  In the **Change Owner/Group** dialog box:
    -   Choose the new user from the **User** drop-down menu.
    -   Choose the new group from the **Group** drop-down menu.
    -   Check the **Recursive** checkbox to propagate the change.

4.  Click **Submit** to make the changes.

**Permissions**

1.  In the **File Browser** window, check the checkbox next to the file
    or directory whose permissions you want to change.
2.  Click the **Change Permissions** button.
3.  In the **Change Permissions** dialog box, select the permissions you
    want to assign and then click **Submit**.
    
    
<a id="searching"></a>
Searching for Files and Directories
-----------------------------------

To search for files or directories by name using the query search box,
enter the name of the file or directory in the query search box. File
Browser lists the files or directories matching the search criteria.

<a id="viewAndEdit"></a>
Viewing and Editing Files
-------------------------

You can view and edit files as text or binary.


**View**

1.  In the **File Browser** window, click the file you want to view.
    File Browser displays the first 4,096 bytes of the file in the
    **File Viewer** window.
    -   If the file is larger than 4,096 bytes, use the Block navigation
        buttons (First Block, Previous Block, Next Block, Last Block) to
        scroll through the file block by block. The **Viewing Bytes**
        fields show the range of bytes you are currently viewing.
    -   To switch the view from text to binary, click **View as Binary**
        to view a hex dump.
    -   To switch the view from binary to text, click **View as Text**.

**Edit**

1.  If you are viewing a text file, click **Edit File**. File Browser
    displays the contents of the file in the **File Editor** window.
2.  Edit the file and then click **Save** or **Save As** to save the
    file.

**View Location in HDFS**

Click **View File Location**. File Browser displays the file's location
in the **File Browser** window.


#### Scheduler
The application lets you build workflows and then schedule them to run regularly automatically. A monitoring interface shows the progress, logs and allow actions like pausing or stopping jobs.

   </div>
</div>
