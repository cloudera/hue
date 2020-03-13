---
title: "0.3.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -30
tags: ['skipIndexing']
---

### v0.3.0, released November 23rd, 2009

Cloudera Desktop 0.3.0 is an update release from the previous version 0.2.0.
In this release, we have focused on ease of installation and system
compatibility. Additionally, we have included one new application, allowing the
administrator to manage users on the Hadoop cluster.

IMPORTANT UPGRADE NOTES:

After installing Cloudera Desktop 0.3.0, the first username and password you
use to log in will become your superuser account. After your first login, all
subsequent accounts will have to be created through the User Manager
application.


NEW FEATURES

- User Manager

  Cloudera Desktop now includes a "User Manager" application, allowing cluster
  administrators to create and remove accounts for the members of their
  organization. Additionally, the default authentication mechanism now checks
  logins against this built in user database.

- hadoop-0.20-conf-pseudo-desktop RPM and Debian packages

  Cloudera now distributes a new package called
  hadoop-0.20-conf-pseudo-desktop. This package will install and configure
  pseudo-distributed Hadoop cluster as well as Cloudera Desktop on a single
  node.

  Please see http://archive.cloudera.com for more information.


IMPROVEMENTS

- Python 2.4 Support

Cloudera Desktop has been backported to now run on Python version 2.4 or newer.
This enables simpler installation on Red Hat Enterprise Linux (RHEL) or CentOS 5.

- Standalone Installation

The previous version of Cloudera Desktop depended on network access during the
installation process. The Desktop RPMs and Debian packages are now able to be
installed in a disconnected/secured environment without requiring network
access.

- Significant internal refactoring / SDK Development

Cloudera Desktop has undergone significant internal refactoring, working towards
the goal of a publicly available Developer SDK. Several of the existing
Desktop Applications have been refactored to use new reusable constructs, which
we will be sharing with the community at large in the coming months.


BUG FIXES

- The requirement of Firefox 3.5 has been relaxed to Firefox 3.0 or newer.
