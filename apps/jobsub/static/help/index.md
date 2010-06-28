Job Designer
============
<a target="JobSub"><img src="/jobsub/static/art/icon.png" class="help-logo"/></a>
The Job Designer lets you submit jobs to the Hadoop cluster,
and it lets you "parameterize" these jobs so that other
users may use them as well.  
<img src="/jobsub/static/help/images/job_editor.gif"/>

Currently, the Job Designer supports "streaming"
and "jar" jobs.  Note that the input files must 
already be uploaded to the cluster.
When you hit the "play" (submit) button,
Job Designer's backend server (called
"jobsubd") will run the job on your behalf.
<img src="/jobsub/static/help/images/design_list.gif"/>

When you use the syntax "$parameter_name"
in your job configuration, Hue will prompt
for a value whenever you "play" this job.  
<img src="/jobsub/static/help/images/job_input.gif"/>
