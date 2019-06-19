---
title: "Reference Architecture"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

A recommended setup consists in:

* 2 Hues and 1 Load Balancer
* Databases: MySQL InnoDB, PostgreSQL, Oracle
* Authentication: [LDAP or Username/Password](../user-management/)

### Load Balancers

Hue is often run with:

* Cherrypy with [NGINX](http://gethue.com/using-nginx-to-speed-up-hue-3-8-0/) (recommended)
* Cherrypy with HTTPD (built-in when using Cloudera Manager)
* Gunicorn is coming with [HUE-8739](https://issues.cloudera.org/browse/HUE-8739)
* [Apache mod Python](http://gethue.com/how-to-run-hue-with-the-apache-server/)

### Task Server

** Not fully supported yet**

The task server is currently a work in progress to outsource all the blocking or resource intensive operations
outside of the API server. Follow [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) for more information
on when first usable task will be released.

Until then, here is how to try the task server service.

Make sure you have Rabbit MQ installed and running.

    sudo apt-get install rabbitmq-server -y

In hue.ini, telling the API server that the Task Server is available:

    [desktop]
    [[task_server]]
    enabled=true

Starting the Task server:

    ./build/env/bin/celery worker -l info -A desktop

Available tasks

#### Query Task

When the task server is enabled, SQL queries are going to be submitted outside of the Hue servers.

To configure the storage to use to persist those, edit the `result_file_storage` setting:

    [desktop]
    [[task_server]]
    result_file_storage='{"backend": "django.core.files.storage.FileSystemStorage", "properties": {"location": "/var/lib/hue/query-results"}}'


### Task Scheduler

For schedules configured statically in Python:

    ./build/env/bin/celery -A desktop beat -l info

For schedules configured dynamically via a table with Django Celery Beat:

    [desktop]
    [[task_server]]
    beat_enabled=false

Then:

    ./build/env/bin/celery -A desktop beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

Note: the first time the tables need to be created with:

    ./build/env/bin/hue migrate

### Monitoring

Performing a `GET /desktop/debug/is_alive` will return a 200 response if running.

### Proxy

A Web proxy lets you centralize all the access to a certain URL and prettify the address (e.g. ec2-54-247-321-151.compute-1.amazonaws.com --> demo.gethue.com).

Here is one way to do it with [NGINX](http://gethue.com/using-nginx-to-speed-up-hue-3-8-0/) or [Apache](http://gethue.com/i-put-a-proxy-on-hue/).
