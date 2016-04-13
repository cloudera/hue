
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Hue Shell
=========

The Hue Shell application provides access to the Pig, HBase, and Sqoop 2
command-line shells. The Shell application is designed to have the same
look and feel as a Unix terminal. In addition to the shells configured
by default, it is possible to include almost any process that exposes a
command-line interface as an option in this Hue application.

Hue Shell Installation and Configuration
----------------------------------------

Hue Shell is one of the applications installed as part of Hue. For
information about installing and configuring Hue, see Hue Installation
in
[http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/CDH4-Installation-Guide.html](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/CDH4-Installation-Guide.html).

### Unix User Accounts

To properly isolate subprocesses so as to guarantee security, each Hue
user who is using the Shell subprocess must have a Unix user account.
The link between Hue users and Unix user accounts is the username, and
so every Hue user who wants to use the Shell application must have a
Unix user account with the same name on the system that runs the Hue
Server. See Unix User Accounts in
[http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/CDH4-Installation-Guide.html](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/CDH4-Installation-Guide.html)
for instructions.

Starting Hue Shell
------------------

1.  Click the **Shell** icon (![image](images/icon_shell_24.png)) in the
    navigation bar at the top of the Hue web page. (To start a second
    instance of the Shell application, right-click the link and select
    **Open link in new tab**.) The **Shell** window opens in the Hue web
    page.
2.  Click any of the tabs at the top of the Shell window to open a
    subprocess shell of that type.
    ![image](images/note.jpg) **Note**: If a button is disabled, the
    program is not on the system path. Ask your Hue administrator to fix
    this problem.
3.  After opening a subprocess, click anywhere in the body of the Shell
    application window to focus the command line. (Tab-completion is not
    supported.)
4.  To end a process, type exit or quit depending on the type of
    subprocess you have opened.
    ![image](images/note.jpg) **Note**: If you close your browser, the
    underlying shell process remains running for the amount of time
    specified by your Hue administrator. After this time the process is
    killed.

Viewing Documentation for the Shells
------------------------------------

For information about using each of the default shells, see the
documentation on the following sites:

-   [Pig](http://archive.cloudera.com/cdh4/cdh/4/pig/)
-   [HBase](http://archive.cloudera.com/cdh4/cdh/4/hbase/)
-   [Sqoop 2](http://archive.cloudera.com/cdh4/cdh/4/sqoop2/)
