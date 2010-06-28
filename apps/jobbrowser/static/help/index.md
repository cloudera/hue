Job Browser
===========
<a target="JobBrowser"><img src="/jobbrowser/static/art/icon_huge.png" class="help-logo"/></a>
The Job Browser application lets you examine
jobs running on your cluster.  
<img src="/jobbrowser/static/help/images/job_list.gif"/>

Diving into a Job
-----------------
A MapReduce job, as presented by the Job Browser,
has many layers.  You start with a list of jobs,
then dig down into that job's tasks.  Each
task may have multiple task attempts.
It is often useful, if a job has failed, to examine
the "logs" tab of one of the attempts.
<img src="/jobbrowser/static/help/images/task_list.gif"/>

Killing Jobs
------------
If you are the user who submitted the job, you
can kill the job by hitting the "Stop" icon.

Viewing Metadata and Counters
-----------------------------
Job Metadata (like where the inputs and outputs are)
and counters are available using the Job Browser.
