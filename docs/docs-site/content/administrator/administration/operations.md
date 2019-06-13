---
title: "Operations"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

## Admin Wizard

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

### Configuration

Displays a list of the installed Hue applications and their
configuration. The location of the folder containing the Hue
configuration files is shown at the top of the page. Hue configuration
settings are in the hue.ini configuration file.

Click the tabs under **Configuration Sections and Variables** to see the
settings configured for each application. For information on configuring
these settings, see Hue Configuration in the Hue installation manual.


Hue ships with a default configuration that will work for
pseudo-distributed clusters.  If you are running on a real cluster, you must
make a few changes to the `hue.ini` configuration file (`/etc/hue/hue.ini` when installed from the
package version) or `pseudo-distributed.ini` in `desktop/conf` when in development mode).
The following sections describe the key configuration options you must make to configure Hue.


<div class="note">
To list all available configuration options, run:

    $ /usr/share/hue/build/env/bin/hue config_help | less

This commands outlines the various sections and options in the configuration,
and provides help and information on the default values.
</div>


<div class="note">
To view the current configuration from within Hue, open:

    http://<hue>/hue/dump_config
</div>

<div class="note">
Hue loads and merges all of the files with extension `.ini`
located in the `/etc/hue` directory.  Files that are alphabetically later
take precedence.
</div>


### Configuration Validation

Hue can detect certain invalid configuration.

To view the configuration of a running Hue instance, navigate to
`http://myserver:8888/hue/dump_config`, also accessible through the About
application.


### Server Logs

Displays the Hue Server log and allows you to download the log to your
local system in a zip file.

### Threads

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Threads page can be very helpful in debugging purposes. It includes a daemonic thread and the thread objects serving concurrent requests. The host name, thread name identifier and current stack frame of each are displayed. Those are useful when Hue “hangs”, sometimes in case of a request too CPU intensive. There is also a REST API to get the dump of Threads using 'desktop/debug/threads'

### Metrics

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Hue uses the **PyFormance** Python library to collect the metrics. These metrics are represented as gauge, counters, meter, rate of events over time, histogram, statistical distribution of values. A REST API endpoint '/desktop/metrics/' to get all the metrics dump as json is also exposed

The below metrics of most concern to us are displayed on the page:

- requests.active
- requests.exceptions
- requests.response-time
- threads.daemon
- threads.total
- users
- users.active

One of the most useful ones are the percentiles of response time of requests and the count of active users.
Admins can either filter a particular property in all the metrics or select a particular metric for all properties

### Logging

The Hue logs are found in `/var/log/hue`, or in a `logs` directory under your
Hue installation root. Inside the log directory you can find:

* An `access.log` file, which contains a log for all requests against the Hue
web server.
* A `supervisor.log` file, which contains log information for the supervisor
process.
* A `supervisor.out` file, which contains the stdout and stderr for the
supervisor process.
* A `.log` file for each supervised process described above, which contains
the logs for that process.
* A `.out` file for each supervised process described above, which contains
the stdout and stderr for that process.

If users on your cluster have problems running Hue, you can often find error
messages in these log files. If you are unable to start Hue from the init
script, the `supervisor.log` log file can often contain clues.

In addition to logging `INFO` level messages to the `logs` directory, the Hue
web server keeps a small buffer of log messages at all levels in memory. You can
view these logs by visiting `http://myserver:8888/hue/logs`. The `DEBUG` level
messages shown can sometimes be helpful in troubleshooting issues.

## Commands

Type the following command from the Hue installation root.

    cd /usr/lib/hue (or /opt/cloudera/parcels/CDH-XXXXX/share/hue if using parcels and CM)
    build/env/bin/hue shell

To list all the available commands:

    build/env/bin/hue

## Troubleshooting

To troubleshoot why Hue is slow or consuming high memory, admin can enable instrumentation by setting the `instrumentation` flag to True.

    [desktop]
    instrumentation=true

If `django_debug_mode` is enabled, instrumentation is automatically enabled. This flag appends the response time and the total peak memory used since Hue started for every logged request.

### Instrumentation enabled

<pre>
[17/Apr/2018 15:18:43 -0700] access       INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" `returned in 97ms (mem: 135mb)`
</pre>

### Instrumentation not enabled

<pre>
[23/Apr/2018 10:59:01 -0700] INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" returned in 88ms
</pre>

## Database

See the dedicated [Database section]({{% param baseURL %}}administrator/administration/database/).
