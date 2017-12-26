
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

### Importer

### Documents
#### Sharing
#### Import / Export

## Editors
The goal of Hue’s Editor is to make data querying easy and productive.

It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.

#### Languages
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
