---
title: "APIs"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 5
---

Hue can be accessed directly via a Django Python Shell or by its REST API.


## REST

REST APIs are not all public yet but this is work in progress in [HUE-1450](https://issues.cloudera.org/browse/HUE-1450).

Hue is Ajax based and has a REST API used by the browser to communicate (e.g. submit a query or workflow,
list some S3 files, export a document...). Currently this API is private and subject to change but
can be easily reused. You would need to GET */accounts/login* to get the CSRF token
and POST it back along *username* and *password* and reuse the *sessionid* cookie in next
communication calls.

### Quickstart

Hue is based on the Django Web Framework. Django comes with user authentication system. Django uses sessions and middleware to hook the authentication system into request object. Hue uses stock auth form which uses *username* and *password* and *csrftoken* form variables to authenticate.

In this code snippet, we will use well-known python *requests* library. We will first acquire *csrftoken* by GET *login_url* and then create a dictionary of form data which contains *username*, *password* and *csrftoken* and the *next_url* and another dictionary for header which contains the *Referer* url and an empty dictionary for the cookies. After the POST request to *login_url* we will check the reponse code, which should be *r.status_code == 200*.

Once the request is successful then capture headers and cookies for subsequent requests. Subsequent *request.session* calls can be made by providing *cookies=session.cookies* and *headers=session.headers*.

    import requests

    def login_djangosite():
    next_url = "/"
    login_url = "http://localhost:8888/accounts/login?next=/"

    session = requests.Session()
    r = session.get(login_url)
    form_data = dict(username="[your hue username]",password="[your hue password]",
                      csrfmiddlewaretoken=session.cookies['csrftoken'],next=next_url)
    r = session.post(login_url, data=form_data, cookies=dict(), headers=dict(Referer=login_url))

    # check if request executed successfully?
    print r.status_code

    cookies = session.cookies
    headers = session.headers

    r=session.get('http://localhost:8888/metastore/databases/default/metadata',
    cookies=session.cookies, headers=session.headers)
    print r.status_code

    # check metadata output
    print r.text


### Data Catalog

The [metadata API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata) is powering [Search and Tagging here](http://gethue.com/improved-sql-exploration-in-hue-4-3/) and the [Query Assistant with Navigator Optimizer Integration](http://gethue.com/hue-4-sql-editor-improvements/).

The backends is pluggable by providing alternative [client interfaces](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/catalog):

* Cloudera Navigator (default)
* Apache Atlas ([HUE-8749](https://issues.cloudera.org/browse/HUE-8749))
* Dummy (skeleton for integrating new catalogs)

#### Searching for entities

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        sources: ko.mapping.toJSON(["sql", "hdfs", "s3"]),
        field_facets: ko.mapping.toJSON([]),
        limit: 10
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });


#### Searching for entities with the dummy backend

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Finding an entity in order to get its id

    $.get("/metadata/api/navigator/find_entity", {
        type: "table",
        database: "default",
        name: "sample_07",
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Adding/updating a comment with the dummy backend

    $.post("/metadata/api/catalog/update_properties/", {
        id: "22",
        properties: ko.mapping.toJSON({"description":"Adding a description"}),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Adding a tag with the dummy backend

    $.post("/metadata/api/catalog/add_tags/", {
      id: "22",
      tags: ko.mapping.toJSON(["usage"]),
      interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
       "id": "32",
       "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
       console.log(ko.mapping.toJSON(data));
    });

#### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
      "id": "32",
      "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Getting the model mapping of custom metadata

    $.get("/metadata/api/catalog/models/properties/mappings/", function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Getting a namespace

    $.post("/metadata/api/catalog/namespace/", {
      namespace: 'huecatalog'
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

#### Creating a namespace

    $.post("/metadata/api/catalog/namespace/create/", {
      "namespace": "huecatalog",
      "description": "my desc"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Creating a namespace property

    $.post("/metadata/api/catalog/namespace/property/create/", {
      "namespace": "huecatalog",
      "properties": ko.mapping.toJSON({
        "name" : "relatedEntities2",
        "displayName" : "Related objects",
        "description" : "My desc",
        "multiValued" : true,
        "maxLength" : 50,
        "pattern" : ".*",
        "enumValues" : null,
        "type" : "TEXT"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Map a namespace property to a class entity

    $.post("/metadata/api/catalog/namespace/property/map/", {
      "class": "hv_view",
      "properties": ko.mapping.toJSON([{
          namespace: "huecatalog",
          name: "relatedQueries"
      }])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


## Python

* [Hue API: Execute some builtin or shell commands](http://gethue.com/hue-api-execute-some-builtin-commands/).
* [How to manage the Hue database with the shell](http://gethue.com/how-to-manage-the-hue-database-with-the-shell/).

### How to count documents of a user

On the command line:

    ./build/env/bin/hue shell

If using Cloudera Manager, as a *root* user launch the shell.

Export the configuration directory:

    export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE_SERVER | tail -1 | awk '{print $9}'`"
    echo $HUE_CONF_DIR
    > /var/run/cloudera-scm-agent/process/2061-hue-HUE_SERVER

Get the process id:

    lsof -i :8888|grep -m1 hue|awk '{ print $2 }'
    > 14850

In order to export all Hue's env variables:

    for line in `strings /proc/$(lsof -i :8888|grep -m1 hue|awk '{ print $2 }')/environ|egrep -v "^HOME=|^TERM=|^PWD="`;do export $line;done

And finally launch the shell by:

    HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue shell
    > ALERT: This appears to be a CM Managed environment
    > ALERT: HUE_CONF_DIR must be set when running hue commands in CM Managed environment
    > ALERT: Please run 'hue <command> --cm-managed'

Then use the Python code to access a certain user information:

    Python 2.7.6 (default, Oct 26 2016, 20:30:19)
    Type "copyright", "credits" or "license" for more information.

    IPython 5.2.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    from django.contrib.auth.models import User
    from desktop.models import Document2

    user = User.objects.get(username='demo')
    Document2.objects.documents(user=user).count()

    In [8]: Document2.objects.documents(user=user).count()
    Out[8]: 1167

    In [10]: Document2.objects.documents(user=user, perms='own').count()
    Out[10]: 1166

    In [11]: Document2.objects.documents(user=user, perms='own', include_history=True).count()
    Out[11]: 7125

    In [12]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True).count()
    Out[12]: 7638

    In [13]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True, include_managed=True).count()
    Out[13]: 31408

    Out[14]:
    (85667L,
    {u'desktop.Document': 18524L,
      u'desktop.Document2': 31409L,
      u'desktop.Document2Permission': 556L,
      u'desktop.Document2Permission_groups': 277L,
      u'desktop.Document2Permission_users': 0L,
      u'desktop.Document2_dependencies': 15087L,
      u'desktop.DocumentPermission': 1290L,
      u'desktop.DocumentPermission_groups': 0L,
      u'desktop.DocumentPermission_users': 0L,
      u'desktop.Document_tags': 18524L})
