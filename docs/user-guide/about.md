
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

About Hue
=========

The **About Hue** application displays the version of Hue you are
running. If you are a superuser, it lets you perform Hue setup tasks,
and lets you view configuration and logs.

Starting About Hue
------------------

To start the About Hue application, click
![image](images/quick_start.png) in the navigation bar at the top of the
Hue browser page. It opens to the Quick Start Wizard screen.

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
2.  **Examples** contains links to install examples into the Beeswax,
    Cloudera Impala, Metastore Manager, Job Designer, Oozie
    Editor/Dashboard, and Pig Editor applications.
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
