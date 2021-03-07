---
title: Storing passwords in file script rather than in hue.ini configuration
author: admin
type: post
date: 2015-09-09T21:33:25+00:00
url: /storing-passwords-in-script-rather-than-hue-ini-files/
sf_remove_promo_bar:
  - 1
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
categories:

---
This article details how to store passwords in a script launched from the OS rather than have clear text passwords in the hue*.ini files.

Some passwords go in Hue ini configuration file making them easily visible to Hue admin user or by users of cluster management software. You can use the password_script feature to prevent passwords from being visible.

[<img src="https://cdn.gethue.com/uploads/2015/09/hue_password_files.png"  />][1]

Prior to 3.8, Hue only supported clear text passwords in all the Hue configuration files. In 3.8, Hue added functionality that pulls the password by running a shell script and using the stdout from the shell script to get the password.

### Instructions

Starting in 3.8, Hue now supports the ability to provide a password script in the hue.ini that outputs a password to stdout and Hue will use this password on startup instead of a clear text password in the hue.ini.

Any parameter that defines a password in the hue.ini can be replaced with the same parameter name with the addition of _script at the end of the parameter and set to a value that points to a shell script.

On startup, Hue runs the startup script and grabs the password from stdout. This is an example configuration:

<pre><code class="bash">[desktop]

ldap_username=hueservice

ldap_password_script="/var/lib/hue/hue_passwords.sh ldap_password"

ssl_password_script="/var/lib/hue/hue_passwords.sh ssl_password"

[[ldap]]

bind_password_script="/var/lib/hue/hue_passwords.sh bind_password"

[[database]]

password_script="/var/lib/hue/hue_passwords.sh database"

</code></pre>

The script should go in a location where it can be read and executed by only the hue user. You can have a script per password or a single script that takes parameters. Here is an example single script that takes parameters that matches the above config:

<pre><code class="bash">#!/bin/bash

SERVICE=$1

if [[ ${SERVICE} == "ldap_password" ]]

then

echo "password"

fi

if [[ ${SERVICE} == "ssl_password" ]]

then

echo "password"

fi

if [[ ${SERVICE} == "bind_password" ]]

then

echo "Password1"

fi

if [[ ${SERVICE} == "database_password" ]]

then

echo "password"

fi

</code></pre>

Starting in Cloudera Manager 5.5 passwords are not stored in configuration files in clear text anymore.  As a result on Cloudera Manager 5.5 and higher you will need to know the password for Hue's DB connection to be able to run the Hue command line.

## **Running Hue command line on Cloudera Manager 5.5 and above**

  1. Set HUE_CONF_DIR to the current Hue configuration created by Cloudera Manager.
  2. export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 \`"
  3. Run the Hue Command line by including the following environment variables:
      * HUE_DATABASE_PASSWORD=<dbpassword> - This defines the password Hue should use to connect to the DB.
      * HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 - This configures the Hue command line to run even if there are other unknown passwords defined in the Cloudera Manager created hue.ini.  Such as bind_password or ssl_password.
      * HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 HUE_DATABASE_PASSWORD=password /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue <command>
      * **Note:** When you include environment variables on the command line without a ";" between them as the above command does, they will only apply to that command.  You won't have HUE_DATABASE_PASSWORD in the environment after the command finishes.

Example running changepassword:

[root@nightly55-1 ~]# export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 \`"

[root@nightly55-1 ~]# HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 HUE_DATABASE_PASSWORD=password /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue changepassword admin

Changing password for user 'admin'

Password:

Password (again):

Password changed successfully for user 'admin'

If you are performing command line actions that require other password, such as bind_password for syncing LDAP users and groups, you need to include environment variables to set those as well.  Here is a list:

HUE_AUTH_PASSWORD = password used to authenticate to HS2/Impala.

HUE_LDAP_PASSWORD = password used to authenticate to HS2/Impala.

HUE_SSL_PASSWORD = password used for private key file.

HUE_SMTP_PASSWORD = password used for SMTP.

HUE_LDAP_BIND_PASSWORD = password used for Ldap Bind.

## **Running Hue command line on Cloudera Manager 5.4 and below**

  1. Set HUE_CONF_DIR to the current Hue configuration created by Cloudera Manager.
  2. export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 \`"
  3. Run the Hue command line.
  4. /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue <command>

Example running changepassword.

<pre>[root@cdhnok54-1 tmp]# export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 `"
[root@cdhnok54-1 tmp]# /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue changepassword admin
Changing password for user 'admin'
Password:
Password (again):
Password changed successfully for user 'admin'</pre>

 [1]: https://cdn.gethue.com/uploads/2015/09/hue_password_files.png
