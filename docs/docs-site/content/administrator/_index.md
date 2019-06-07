+++
title = "Administrator"
date = 2019-03-13T18:27:26-07:00
weight = 1
chapter = false
pre = "<b>1. </b>"
+++

### Guide

The following instructions describe how to install Hue and configure it to points to external services
(e.g. Databases, Hadoop, S3, ...).

Hue consists of a web service that runs on a special node in your cluster.
Choose one node where you want to run Hue. For optimal performance, this should be one of the nodes
within your cluster, though it can be a remote node as long as there are no
overly restrictive firewalls.

You can download the [Hue tarballs](https://github.com/cloudera/hue/releases) here.