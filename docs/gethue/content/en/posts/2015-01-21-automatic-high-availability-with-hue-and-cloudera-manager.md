---
title: Automatic High Availability with Hue and Cloudera Manager
author: admin
type: post
date: 2015-01-21T17:42:45+00:00
url: /automatic-high-availability-with-hue-and-cloudera-manager/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
slide_template:
  - default
categories:
  - Development

---
<span style="color: #ff0000;"><em>December 8th 2015 update: this post is now deprecated as of Hue 3.9: <a style="color: #ff0000;" href="https://gethue.com/automatic-high-availability-and-load-balancing-of-hue-in-cloudera-manager-with-monitoring/">https://gethue.com/automatic-high-availability-and-load-balancing-of-hue-in-cloudera-manager-with-monitoring/</a></em></span>

By default, Hue installs on a single machine, which means Hue is both constrained to that machine’s CPU and memory, which can limit the total number of active users before Hue becomes unstable. Furthermore, even a lightly loaded machine could crash, which would bring Hue out of service. This tutorial demonstrates hue-lb-example, an example load balancer that can automatically configure [NGINX][1] and [HAProxy][2] for a Cloudera Manager-managed Hue.

Before we demonstrate its use, we need to install a couple things first.

## Configuring Hue in Cloudera Manager

Hue should be set up on at least two of the nodes in Cloudera Manager and be configured to use a database like MySQL, PostgreSQL, or Oracle configured in a high availability manner. Furthermore, the database must be configured to be accessible from all the Hue instances. You can find detailed instructions on setting up or migrating the database from SQLite [here][3].

Once the database has been set up, the following instructions describe setting up a fresh install. If you have an existing Hue, jump to step 5.

  1. From Cloudera Manager
  2. Go to “Add a Service -> Hue”, and follow the directions to create the first Hue instance.

    [<img class="aligncenter  wp-image-2047" src="https://cdn.gethue.com/uploads/2015/01/hue-lb-0-1024x547.png"  />

][4]
  3. Once complete, stop the Hue instance so we can change the underlying database.
  4. Go to “Hue -> Configuration -> Database” and enter in the database connection information, and save.[<img class="aligncenter  wp-image-2053" src="https://cdn.gethue.com/uploads/2015/01/hust-lb-db-1024x488.png" />][5]
  5. Go to “Hue -> Instances -> Add a Role Instance”[<img class="aligncenter  wp-image-2049" src="https://cdn.gethue.com/uploads/2015/01/hue-lb-1-1024x386.png"  />][6]
  6. Select “Hue” and select which services you would like to expose on Hue. If you are using Kerberos, make sure to also add a "Kerberos Ticket Renewer" on the same machine as this new Hue role.[<img class="aligncenter  wp-image-2052" src="https://cdn.gethue.com/uploads/2015/01/hue-lb-2-1024x544.png"  />][7]
  7. On “Customize Role Assignments”, add at least one other “Hue Server” instance another machine.
  8. Start the new Hue Server.[<img class="aligncenter  wp-image-2051" src="https://cdn.gethue.com/uploads/2015/01/hue-lb-3-1024x410.png"  />][8]

## Installing the Dependencies

On a Redhat/Fedora-based system:

<pre><code class="bash">% sudo yum install git nginx haproxy python python-pip

% pip install virtualenv

</code></pre>

On a Debian/Ubuntu-based system:

<pre><code class="bash">% sudo apt-get install git nginx haproxy python python-pip

% pip install virtualenv

</code></pre>

## Running the load balancers

First we want to start the load balancer:

<pre><code class="bash">% cd $HUE_HOME_DIR/tools/load-balancer

</code></pre>

Next we install the load balancer specific dependencies in a python virtual environment to keep those dependencies from affecting other projects on the system.

<pre><code class="bash">% virtualenv build

% source build/bin/activate

% pip install -r requirements.txt

</code></pre>

Finally, modify `etc/hue-lb.toml` to point at your instance of Cloudera Manager (as in "cloudera-manager.example.com" without the port or "http://"), and provide a username and password for an account that has read access to the Hue state.

Now we are ready to start the load balancers. Run:

<pre><code class="bash">% ./bin/supervisord

% ./bin/supervisorctl status

haproxy RUNNING pid 36920, uptime 0:00:01

monitor-hue-lb RUNNING pid 36919, uptime 0:00:01

nginx RUNNING pid 36921, uptime 0:00:01

</code></pre>

You should be able to access Hue from either `http://HUE-LB-HOSTNAME:8000` for NGINX, or `http://HUE-LB-HOSTNAME:8001` for HAProxy. To demonstrate the that it’s load balancing:

  1. Go into Cloudera Manager, then “Hue”, then “Instances”.
  2. Stop the first Hue instance.
  3. Access the URL and verify it works.
  4. Start the first instance, and stop the second instance.
  5. Access the URL and verify it works

[<img class=" size-full wp-image-2055 alignnone" src="https://cdn.gethue.com/uploads/2015/01/hue-lb-4.png"  />][9]

##

Finally, if you want to shut down the load balancers, run:

<pre><code class="bash">% ./bin/supervisorctl shutdown

</code></pre>

## Automatic Updates from Cloudera Manager

The hue load balancer uses [Supervisor][10], a service that monitors and controls other services. It can be configured to automatically restart services if they crashed, or trigger scripts if certain events occur. The load balancer starts and monitors the NGINX or HAProxy through another process named `monitor-hue-lb`. It accomplishes this through the use of Cloudera Manager API to access the status of Hue in Cloudera Manager, and automatically add and remove Hue from the load balancers. If it detects that a new Hue instances has been added or removed, it updates the configuration of all the active load balancers and triggers them to reload without dropping any connections.

## Sticky Sessions

Both NGINX and HAProxy are configured to route users to the same backend, otherwise known as sticky sessions. This is both done for performance issues as it’s more likely the Hue backend will have the user’s data cached in the same Hue instance, but also because Impala currently does not yet support native high availability ([IMPALA-1653][11]). This means that the underlying Impala session opened by one Hue instance cannot be accessed by another Hue instance. By using sticky sessions, users will be always routed to the same Hue instance, so they will be able to still access their Impala sessions. That is, of course, assuming that Hue instance is still active. If not, the user will be routed to one of the other active Hue sessions.

Next steps (for C6) will be to make all the above done with one click in Cloudera Manager by shipping a parcel with all the dependencies (or downloading them automatically) and adding a new 'HA' role in the Hue service.

Have any questions? Feel free to contact us on [hue-user][12] or [@gethue][13]!

 [1]: http://nginx.org "NGINX"
 [2]: http://haproxy.org "HAProxy"
 [3]: http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cdh_ig_hue_database.html "here"
 [4]: https://cdn.gethue.com/uploads/2015/01/hue-lb-0.png
 [5]: https://cdn.gethue.com/uploads/2015/01/hust-lb-db.png
 [6]: https://cdn.gethue.com/uploads/2015/01/hue-lb-1.png
 [7]: https://cdn.gethue.com/uploads/2015/01/hue-lb-2.png
 [8]: https://cdn.gethue.com/uploads/2015/01/hue-lb-3.png
 [9]: https://cdn.gethue.com/uploads/2015/01/hue-lb-4.png
 [10]: http://supervisord.org/ "Supervisor"
 [11]: https://issues.cloudera.org/browse/IMPALA-1653
 [12]: http://groups.google.com/a/cloudera.org/group/hue-user
 [13]: https://twitter.com/gethue
