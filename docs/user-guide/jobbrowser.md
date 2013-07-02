
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Job Browser
===========

The Job Browser application lets you to examine the Hadoop MapReduce
jobs running on your Hadoop cluster. Job Browser presents the job and
tasks in layers. The top layer is a list of jobs, and you can link to a
list of that job's tasks. You can then view a task's attempts and the
properties of each attempt, such as state, start and end time, and
output size. To troubleshoot failed jobs, you can also view the logs of
each attempt.

Job Browser Installation and Configuration
------------------------------------------

Job Browser is one of the applications installed as part of Hue. For
information about installing and configuring Hue, see the Hue Installation
manual.

Job Browser can display both MRv1 and MRv2 jobs, but must be configured
to display one type at a time. 

Starting Job Browser
--------------------

Click the **Job Browser** icon (![image](images/icon_jobbrowser_24.png))
in the navigation bar at the top of the Hue web page.

If there are no jobs that have been run, the **Welcome to the Job
Browser** page opens, with links to the Job Designer and Beeswax.

If there are jobs running, then the Job Browser list appears.

Filtering the Job Browser List
------------------------------

-   To filter the jobs by their state (such as **Running** or
    **Completed**), choose a state from the **Job status** drop-down
    menu.
-   To filter by a user who ran the jobs, enter the user's name in the
    **User Name** query box.
-   To filter by job name, enter the name in the **Text** query box.
-   To clear the filters, choose **All States** from the **Job status**
    drop-down menu and delete any text in the **User Name** and **Text**
    query boxes.
-   To display retired jobs, check the **Show retired jobs** checkbox.
    Retired jobs show somewhat limited information – for example,
    information on maps and reduces and job duration is not available.
    Jobs are designated as Retired by the JobTracker based on the value
    of mapred.jobtracker.retirejob.interval. The retired jobs no longer
    display after the JobTracker is restarted.

Viewing Job Information and Logs
--------------------------------

![image](images/note.jpg) **Note**: At any level you can view the log
for an object by clicking the ![image](images/log.png) icon in the Logs
column.

**To view job information for an individual job:**

1.  In the **Job Browser** window, click **View** at the right of the
    job you want to view. This shows the **Job** page for the job, with
    the recent tasks associated with the job are displayed in the
    **Tasks** tab.
2.  Click the **Metadata** tab to view the metadata for this job.
3.  Click the **Counters** tab to view the counter metrics for the job.

**To view details about the tasks associated with the job:**

1.  In the **Job** window, click the **View All Tasks** link at the
    right just above the **Recent Tasks** list. This lists all the tasks
    associated with the job.
2.  Click **Attempts** to the right of a task to view the attempts for
    that task.

**To view information about an individual task:**

1.  In the **Job** window, click the **View** link to the right of the
    task. The attempts associated with the task are displayed.
2.  Click the **Metadata** tab to view metadata for this task. The
    metadata associated with the task is displayed.
3.  To view the Hadoop counters for a task, click the **Counters** tab.
    The counters associated with the task are displayed.
4.  To return to the **Job** window for this job, click the job number
    in the status panel at the left of the window.

**To view details about a task attempt:**

1.  In the **Job Task** window, click the **View** link to the right of
    the task attempt. The metadata associated with the attempt is
    displayed under the **Metadata** tab.
2.  To view the Hadoop counters for the task attempt, click the
    **Counters** tab. The counters associated with the attempt are
    displayed.
3.  To view the logs associated with the task attempt, click the
    **Logs** tab. The logs associated with the task attempt are
    displayed.
4.  To return to the list of tasks for the current job, click the task
    number in the status panel at the left of the window.

Viewing Job Output
------------------

1.  In the **Job Browser** window, click the link in the ID column.
2.  To view the output of the job, click the link under **OUTPUT** in
    the panel at the left of the window. This takes you to the job
    output directory in the **File Browser**.
