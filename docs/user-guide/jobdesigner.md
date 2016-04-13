
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Job Designer
============

The Job Designer application enables you to create and submit jobs to
the Hadoop cluster. You can include variables with your jobs to enable
you and other users to enter values for the variables when they run your
job. The Job Designer supports the actions supported by
[Oozie](http://archive.cloudera.com/cdh4/cdh/4/oozie/):
[MapReduce](/content/cloudera-content/cloudera-docs/HadoopTutorial/CDH4/index.html),
Streaming, Java, Pig, Hive, Sqoop, Shell, Ssh, DistCp, Fs, and Email.

Job Designer Installation and Configuration
-------------------------------------------

Job Designer is one of the applications installed as part of Hue. For
information about installing and configuring Hue, see the Hue Installation
manual..

In order to run DistCp, Streaming, Pig, Sqoop, and Hive jobs, Oozie must
be configured to use the Oozie ShareLib. See the Oozie Installation manual.

Starting Job Designer
---------------------

Click the **Job Designer** icon (![image](images/icon_jobsub_24.png)) in
the navigation bar at the top of the Hue web page. The **Job Designs**
page opens in the browser.

Installing the Example Job Designs
----------------------------------

![image](images/note.jpg) **Note**: You must be a superuser to perform
this task.

1.  Click ![image](images/quick_start.png). The Quick Start Wizard
    opens.
2.  Click **Step 2: Examples**.
3.  Click **Job Designer**.

Job Designs
-----------

A job design specifies several meta-level properties of a job, including
the job design name, description, the executable scripts or classes, and
any parameters for those scripts or classes.

### Filtering Job Designs

You can filter the job designs that appear in the list by owner, name,
type, and description.

**To filter the Job Designs list:**

1.  In the **Job Designs** window, click **Designs**.
2.  Enter text in the Filter text box at the top of the **Job Designs**
    window. When you type in the Filter field, the designs are
    dynamically filtered to display only those rows containing text that
    matches the specified substring.

### Creating a Job Design

1.  In the **Job Designs** window, click New Action \> Action, where
    Action is MapReduce, Streaming, Java, Pig, Hive, Sqoop, Shell, Ssh,
    DistCp, Fs, or Email.
2.  In the **Job Design (Action type)** window, specify the common and
    job type specific information.
3.  Click **Save** to save the job settings.

### Deleting and Restoring Job Designs

You can move job designs to the trash and later restore or permanently
delete them.

#### Deleting Job Designs

1.  In a Manager screen, check the checkbox next to one or more job
    designs.
2.  Choose one of the following:
    -   Delete \> Move to trash
    -   Delete \> Delete forever

#### Restoring Job Designs

1.  In a Manager screen, click ![image](images/trash.png) **Trash**.
2.  Check the checkbox next to one or more job designs.
3.  Click Restore.

### Job Design Settings

#### Job Design Common Settings

Most job design types support all the settings listed in the following
table. For job type specific settings, see:
[MapReduce](#mapreduce),
[Streaming](#streaming),
[Java](#java),
[Pig](#pig),
[Hive](#hive),
[Sqoop](#sqoop),
[Shell](#shell),
[Ssh](#ssh),
[DistCp](#distcp),
[Fs](#fs), and
[Email](#email).

All job design settings except Name and Description support the use of
variables of the form $variable\_name. When you run the job, a dialog
box will appear to enable you to specify the values of the variables.

<table>
<tr><td>Name</td><td>Identifies the job and its collection of properties and parameters.</td></tr>
<tr><td>Description</td><td>A description of the job. The description is displayed in the dialog box
that appears if you specify variables for the job.</td></tr>
<tr><td>Advanced</td><td>Advanced settings:<ul><li>Is shared- Indicate whether to share the action with all users.<li>Oozie parameters - parameters to pass to Oozie</td></tr>
<tr><td>Prepare</td><td>Specifies paths to create or delete before starting the workflow job.</td></tr>
<tr><td>Params</td>Parameters to pass to a script or command. The parameters are expressed
using the [JSP 2.0 Specification (JSP.2.3) Expression
Language](http://jcp.org/aboutJava/communityprocess/final/jsr152/),
allowing variables, functions, and complex expressions as parameters.<td></td></tr>
<tr><td>Job Properties</td><td>Job properties. To set a property value, click <b>Add Property</b>.<ol><li>Property name -  a configuration property name. This field provides autocompletion, so you can type the first few characters of a property name and then select the one you want from the drop-down
    list.<li>Valuethe property value.</td></tr>
<tr><td>Files</td><td>Files to pass to the job. Equivalent to the Hadoop -files option.</td></tr>
<tr><td>Archives</td><td>Files to pass to the job. Archives to pass to the job. Equivalent to the Hadoop -archives option.</td></tr></table>

<a id="mapreduce"></a>
#### MapReduce Job Design

A MapReduce job design consists of MapReduce functions written in Java.
You can create a MapReduce job design from existing mapper and reducer
classes without having to write a main Java class. You must specify the
mapper and reducer classes as well as other MapReduce properties in the
Job Properties setting.

<table>
<tr><td>Jar path</td><td>The fully-qualified path to a JAR file containing the classes that
implement the Mapper and Reducer functions.</td></tr>
</table>

<a id="streaming"></a>
#### Streaming Job Design

Hadoop streaming jobs enable you to create MapReduce functions in any
non-Java language that reads standard Unix input and writes standard
Unix output. For more information about Hadoop streaming jobs, see
[Hadoop
Streaming](http://archive.cloudera.com/cdh/3/hadoop-0.20.2+320/streaming.html).

<table>
<tr><td>Mapper</td><td>The path to the mapper script or class. If the mapper file is not on the
machines on the cluster, use the Files option to pass it as a part
of job submission. Equivalent to the Hadoop -mapper option.</td></tr>
<tr><td>Reducer</td><td>The path to the reducer script or class. If the reducer file is not on
the machines on the cluster, use the Files option to pass it as a
part of job submission. Equivalent to the Hadoop -reducer option.</td></tr>
</table>

<a id="java"></a>
#### Java Job Design

A Java job design consists of a main class written in Java.

<table>
<tr><td>Jar path</td><td>The fully-qualified path to a JAR file containing the main class.</td></tr>
<tr><td>Main class</td><td>The main class to invoke the program.</td></tr>
<tr><td>Args</td><td>The arguments to pass to the main class.</td></tr>
<tr><td>Java opts</td><td>The options to pass to the JVM.</td></tr>
</table>

<a id="pig"></a>
#### Pig Job Design


A Pig job design consists of a Pig script.

<table>
<tr><td>Script name</td><td>Script name or path to the Pig script.</td></tr>
</table>

<a id="hive"></a>
#### Hive Job Design

A Hive job design consists of a Hive script.

<table>
<tr><td>Script name</td><td>Script name or path to the Hive script.</td></tr>
</table>


<a id="sqoop"></a>
#### Sqoop Job Design

A Sqoop job design consists of a Sqoop command.

<table>
<tr><td>Command</td><td>The Sqoop command.</td></tr>
</table>

<a id="shell"></a>
#### Shell Job Design

A Shell job design consists of a shell command.

<table>
<tr><td>Command</td><td>The shell command.</td></tr>
<tr><td></td>Capture output<td>Indicate whether to capture the output of the command.</td></tr>
</table>

<a id="ssh"></a>
#### Ssh Job Design

A Ssh job design consists of an ssh command.

<table>
<tr><td>User</td><td>The name of the user to run the command as.</td></tr>
<tr><td>Host</td><td>The name of the host to run the command on.</td></tr>
<tr><td>Command</td><td>The ssh command.</td></tr>
<tr><td></td>Capture output<td>Indicate whether to capture the output of the command.</td></tr>
</table>

<a id="distcp"></a>
#### DistCp Job Design

A DistCp job design consists of a DistCp command.

<a id="fs"></a>
#### Fs Job Design

A Fs job design consists of a command that operates on HDFS.

<table>
<tr><td>Delete path</td><td>The path to delete. If it is a directory, it deletes recursively all its
content and then deletes the directory.</td></tr>
<tr><td></td>Create directory<td>The path of a directory to create.</td></tr>
<tr><td>Move file</td><td>The source and destination paths to the file to be moved.</td></tr>
<tr><td>Change permissions</td><td>The path whose permissions are to be changed, the permissions, and an
indicator of whether to change permission recursively.</td></tr></table>

<a id="email"></a>
#### Email Job Design

A Email job design consists of an email message.

<table>
<tr><td>To addresses</td><td>The recipient of the email message.</td></tr>
<tr><td>CC addresses (optional)</td><td>The cc recipients of the email message.</td></tr>
<tr><td>Subject</td><td>The subject of the email message.</td></tr>
<tr><td>Body</td><td>The body of the email message.</td></tr>
</table>


### Submitting a Job Design

![image](images/note.jpg) **Note**:

A job's input files must be uploaded to the cluster before you can
submit the job.

**To submit a job design:**

1.  In the **Job Designs** window, click **Designs** in the upper left
    corner. Your jobs and other users' jobs are displayed in the **Job
    Designs** window.
2.  Check the checkbox next to the job you want to submit.
3.  Click the **Submit** button.
    1.  If the job contains variables, enter the information requested
        in the dialog box that appears. For example, the sample grep
        MapReduce design displays a dialog where you specify the output
        directory.
    2.  Click **Submit** to submit the job.

After the job is complete, the Job Designer displays the results of the
job. For information about displaying job results, see [Displaying the
Results of Submitting a Job](#submitJob).

### Copying, Editing, and Deleting a Job Design

If you want to edit and use a job but you don't own it, you can make a
copy of it and then edit and use the copied job.


**Copy**

1.  In the **Job Designs** window, click **Designs**. The jobs are
    displayed in the **Job Designs** window.
2.  Check the checkbox next to the job you want to copy.
3.  Click the **Copy** button.
4.  In the **Job Design Editor** window, change the settings and then
    click **Save** to save the job settings.

**Edit**

1.  In the **Job Designs** window, click **Designs**. The jobs are
    displayed in the **Job Designs** window.
2.  Check the checkbox next to the job you want to edit.
3.  Click the **Edit** button.
4.  In the **Job Design** window, change the settings and then click
    **Save** to save the job settings.

Delete

1.  In the **Job Designs** window, click **Designs**. The jobs are
    displayed in the **Job Designs** window.
2.  Check the checkbox next to the job you want to delete.
3.  Click the **Delete** button.
4.  Click **OK** to confirm the deletion.

<a id="submitJob"></a>
Displaying Results of Submitting a Job
--------------------------------------

**To display the Job Submission History:**

In the **Job Designs** window, click the **History** tab. The jobs are
displayed in the **Job Submissions History** listed by Oozie job ID.

**To display Job Details:**

In the **Job Submission History** window, click an Oozie Job ID. The
results of the job display:

-   Actions - a list of actions in the job.
-   Click ![image](images/gear.png) to display the action configuration.
    In the action configuration for a MapReduce action, click the value
    of the mapred.output.dir property to display the job output.
-   In the root-node row, click the Id in the External Id column to view
    the job in the Job Browser.
-   Details - the job details. Click ![image](images/gear.png) to
    display the Oozie application configuration.
-   Definition - the Oozie application definition.
-   Log - the output log.
