---
title: "API"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

# REST

The REST API is not properly public yet and can (will) be simplified in the current work in progress [HUE-1450](https://issues.cloudera.org/browse/HUE-1450).

Hue is Ajax based and has a REST API used by the browser to communicate (e.g. submit an SQL query, list some S3 files in a buck...) with the Hue server which will then perform the operation with the remote services. Currently this API is private and subject to change but can already be reused for prove of concepts until the proper public API is released.

In general we want to authenticate with a username and password, retrieve a `session` and [CSRF](https://docs.djangoproject.com/en/3.1/ref/csrf/) cookies and provide them in the follow-up calls so that Hue knows who we are and won't block you.

The [API documentation](https://docs.gethue.com/developer/api/) has been refreshed and list new endpoints.

## Quickstart

Hue is based on the [Django Web Framework](https://www.djangoproject.com/). Django comes with user authentication system. Django uses sessions and middleware to hook the authentication system into request object. Hue uses stock auth form which uses *username* and *password* and *csrftoken* form variables to authenticate.

### Curl

First get the `CSRF` token:

    curl -i -X GET https://demo.gethue.com/hue/accounts/login/?fromModal=true -o /dev/null -D -

It is important to note the `csrftoken` and `sessionid` values from the response:

    set-cookie: csrftoken=XUFgN1WPZNlaJtBeBDtBvwzrOFqRXIaMlNJv4mdvsS2bIE2Lb8LRmCh5cPUBnBdk; expires=Mon, 13-Sep-2021 20:43:47 GMT; httponly; Max-Age=31449600; Path=/
    set-cookie: sessionid=9cdltfee1q1zmt8b7slsjcomtxzgvgfz; expires=Mon, 14-Sep-2020 21:43:47 GMT; httponly; Max-Age=3600; Path=/

Then authenticate with the credendials and provide the `csrftoken` and `sessionid`  as well (note: `CRSF` currently needs to be repeated twice):

    curl -i -X POST https://demo.gethue.com/hue/accounts/login/?fromModal=true -d 'username=demo&password=demo' -o /dev/null -D - --cookie "csrftoken=XUFgN1WPZNlaJtBeBDtBvwzrOFqRXIaMlNJv4mdvsS2bIE2Lb8LRmCh5cPUBnBdk;sessionid=9cdltfee1q1zmt8b7slsjcomtxzgvgfz" -H "X-CSRFToken: XUFgN1WPZNlaJtBeBDtBvwzrOFqRXIaMlNJv4mdvsS2bIE2Lb8LRmCh5cPUBnBdk"

Then you can perform any operation as the `demo` user by providing the latest `CSRF` and the `sessionid` tokens with these parameters:

    --cookie "csrftoken=tkuKwiyRsEmt7zCqIfym4GCwPxAPQfnTm4Y97gUSszkCRih067sC2GA2mCrH6Lmu;sessionid=z6pjze6j6zrv3uoe2hxa8dfbhbn9bynp" -H "X-CSRFToken: tkuKwiyRsEmt7zCqIfym4GCwPxAPQfnTm4Y97gUSszkCRih067sC2GA2mCrH6Lmu"

Here for example we list all the databases of the `hive` connector:

    curl -X POST https://demo.gethue.com/notebook/api/autocomplete/ --data 'snippet={"type":"hive"}' --cookie "csrftoken=XUFgN1WPZNlaJtBeBDtBvwzrOFqRXIaMlNJv4mdvsS2bIE2Lb8LRmCh5cPUBnBdk;sessionid=9cdltfee1q1zmt8b7slsjcomtxzgvgfz" -H "X-CSRFToken: XUFgN1WPZNlaJtBeBDtBvwzrOFqRXIaMlNJv4mdvsS2bIE2Lb8LRmCh5cPUBnBdk"

    {"status": 0, "databases": ["a0817", "arunso", "ath", "athlete", "beingdatum_db", "bharath_practice", "chungu", "darth", "default", "demo", "diwakar", "emp", "hadooptest", "hebe", "hello", "hivedataset", "hivemap", "hivetesting", "hr_db", "icedb", "lib", "libdemo", "lti", "m", "m1", "movie", "movie1", "movielens", "mscda", "my_database", "mydb", "mydemo", "noo", "prizesh", "rajeev", "ram", "retail", "ruban", "sept9", "sept9_2020", "student", "test", "test21", "test123", "ticktick", "userdb", "vidu"]}

**Note** The `cookie` and `CSRF` tokens are omitted in the following API description to keep it simpler. Those parameters will be integrated into one in the future.

### Python

In this code snippet, we will use well-known python *requests* library. We will first acquire *csrftoken* by GET *login_url* and then create a dictionary of form data which contains *username*, *password* and *csrftoken* and the *next_url* and another dictionary for header which contains the *Referer* url and an empty dictionary for the cookies. After the POST request to *login_url* we will check the response code, which should be *r.status_code == 200*.

Once the request is successful then capture headers and cookies for subsequent requests. Subsequent *request.session* calls can be made by providing *cookies=session.cookies* and *headers=session.headers*.

    import requests

    next_url = "/"
    login_url = "http://localhost:8888/accounts/login"

    session = requests.Session()
    response = session.get(login_url)

    form_data = {
        'username': '[your Hue username]',
        'password': '[your Hue password]',
        'csrfmiddlewaretoken': session.cookies['csrftoken'],
        'next': next_url
    }
    response = session.post(login_url, data=form_data, cookies={}, headers={'Referer': login_url})

    print('Logged in successfully: %s %s' % (response.status_code == 200, response.status_code))

    cookies = session.cookies
    headers = session.headers

    response = session.get('http://localhost:8888/metastore/databases/default/metadata')
    print(response.status_code)
    print(response.text)

### jQuery

Login to a Hue and open up the browser developer console and just type the JavaScript snippets, e.g.:

    $.post("/notebook/api/autocomplete/", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

## Authentication

**Note** There is currently no error on bad authentication but instead a 302 redirect to the login page, e.g.:

    [12/Sep/2020 10:12:44 -0700] middleware   INFO     Redirecting to login page: /hue/useradmin/users/edit/romain
    [12/Sep/2020 10:12:44 -0700] access       INFO     127.0.0.1 -anon- - "POST /hue/useradmin/users/edit/romain HTTP/1.1" - (mem: 169mb)-- login redirection
    [12/Sep/2020 10:12:44 -0700] access       INFO     127.0.0.1 -anon- - "POST /hue/useradmin/users/edit/romain HTTP/1.1" returned in 0ms 302 0 (mem: 169mb)

**Note** The public API should be simpler with only one POST call and will return back only one token

### Login

    curl -v -X POST demo.gethue.com/hue/accounts/login/ -d 'username=demo&password=demo'

    ...
    * We are completely uploaded and fine
    * TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
    * TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
    * old SSL session ID is stale, removing
    * Connection state changed (MAX_CONCURRENT_STREAMS == 128)!
    < HTTP/2 302
    < server: nginx/1.19.0
    < date: Sat, 12 Sep 2020 17:53:18 GMT
    < content-type: text/html; charset=utf-8
    < content-length: 0
    < set-cookie: hue-balancer=1599933199.854.37.877815; Expires=Mon, 14-Sep-20 17:53:18 GMT; Max-Age=172800; Path=/; Secure; HttpOnly
    < x-xss-protection: 1; mode=block
    < content-security-policy: script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net data:;img-src 'self' *.google-analytics.com *.doubleclick.net http://*.tile.osm.org *.tile.osm.org *.gstatic.com data:;style-src 'self' 'unsafe-inline' fonts.googleapis.com;connect-src 'self';frame-src *;child-src 'self' data: *.vimeo.com;object-src 'none'
    < x-content-type-options: nosniff
    < content-language: en-us
    < vary: Cookie, Accept-Language
    < location: /
    < x-frame-options: SAMEORIGIN
    < set-cookie: csrftoken=zfOhD8roDLI7mEgakmBDCy7LDMvkEE2z3uUTIyyVnurhqLZhluhjO76K541MRwAw; expires=Sat, 11-Sep-2021 17:53:18 GMT; httponly; Max-Age=31449600; Path=/
    < set-cookie: sessionid=tzx37xo7izrdfs35o30grdf9u0b2999q; expires=Sat, 12-Sep-2020 18:53:18 GMT; httponly; Max-Age=3600; Path=/
    < strict-transport-security: max-age=15724800; includeSubDomains
    <
    * Connection #0 to host demo.gethue.com left intact

**Note** In certain cases an initial GET is needed in order to retrieve the CSRF token, which can then be provided in the POST with the credentials.

### Logout

    curl -v -X POST https://demo.gethue.com/hue/accounts/logout/

## SQL Querying

### Execute a Query

Now that we are logged-in, here is how to execute a `SHOW TABLES` SQL query via the `hive` connector. You could repeat the steps with any query you want, e.g. `SELECT * FROM web_logs LIMIT 100`.

Until Editor v2 is out [HUE-8768](https://issues.cloudera.org/browse/HUE-8768), the API is pretty complicated but still functional:

For a `SHOW TABLES`, first we send the query statement:

    curl -X POST https://demo.gethue.com/notebook/api/execute/hive --data 'executable={"statement":"SHOW TABLES","database":"default"}&notebook={"type":"query","snippets":[{"id":1,"statement_raw":"SHOW TABLES","type":"hive","variables":[]}],"name":"","isSaved":false,"sessions":[]}&snippet={"id":1,"type":"hive","result":{},"statement":"SHOW TABLES","properties":{}}'

    {"status": 0, "history_id": 17880, "handle": {"statement_id": 0, "session_type": "hive", "has_more_statements": false, "guid": "EUI32vrfTkSOBXET6Eaa+A==\n", "previous_statement_hash": "3070952e55d733fb5bef249277fb8674989e40b6f86c5cc8b39cc415", "log_context": null, "statements_count": 1, "end": {"column": 10, "row": 0}, "session_id": 63, "start": {"column": 0, "row": 0}, "secret": "RuiF0LEkRn+Yok/gjXWSqg==\n", "has_result_set": true, "session_guid": "c845bb7688dca140:859a5024fb284ba2", "statement": "SHOW TABLES", "operation_type": 0, "modified_row_count": null}, "history_uuid": "63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"}

Then check the operation status until it is available for fetching its result:

    curl -X POST https://demo.gethue.com/notebook/api/check_status --data 'notebook={"type":"hive"}&snippet={"history_id": 17886,"type":"hive","result":{"handle":{"guid": "0J6PwGcSQaCJjagzYUBHzA==\n","secret": "uiP3IS4fR/mxkLJER5wRCg==\n","has_result_set": true}},"status":""}'

    {"status": 0, "query_status": {"status": "available", "has_result_set": true}}

And now ask for the resultset of the statement:

    curl -X POST https://demo.gethue.com/notebook/api/fetch_result_data --data 'notebook={"type":"hive"}&snippet={"history_id": 17886,"type":"hive","result":{"handle":{"guid": "0J6PwGcSQaCJjagzYUBHzA==\n","secret": "uiP3IS4fR/mxkLJER5wRCg==\n","has_result_set": true}},"status":""}'

    {"status": 0, "result": {"has_more": true, "type": "table", "meta": [{"comment": "from deserializer", "type": "STRING_TYPE", "name": "tab_name"}], "data": [["adavi"], ["adavi1"], ["adavi2"], ["ambs_feed"], ["apx_adv_deduction_data_process_total"], ["avro_table"], ["avro_table1"], ["bb"], ["bharath_info1"], ["bucknew"], ["bucknew1"], ["chungu"], ["cricket3"], ["cricket4"], ["cricket5_view"], ["cricketer"], ["cricketer_view"], ["cricketer_view1"], ["demo1"], ["demo12345"], ["dummy"], ["embedded"], ["emp"], ["emp1_sept9"], ["emp_details"], ["emp_sept"], ["emp_tbl1"], ["emp_tbl2"], ["empdtls"], ["empdtls_ext"], ["empdtls_ext_v2"], ["employee"], ["employee1"], ["employee_ins"], ["empppp"], ["events"], ["final"], ["flight_data"], ["gopalbhar"], ["guruhive_internaltable"], ["hell"], ["info1"], ["lost_messages"], ["mnewmyak"], ["mortality"], ["mscda"], ["myak"], ["mysample"], ["mysample1"], ["mysample2"], ["network"], ["ods_t_exch_recv_rel_wfz_stat_szy"], ["olympicdata"], ["p_table"], ["partition_cricket"], ["partitioned_user"], ["s"], ["sample"], ["sample_07"], ["sample_08"], ["score"], ["stg_t_exch_recv_rel_wfz_stat_szy"], ["stocks"], ["students"], ["studentscores"], ["studentscores2"], ["t1"], ["table_name"], ["tablex"], ["tabley"], ["temp"], ["test1"], ["test2"], ["test21"], ["test_info"], ["topage"], ["txnrecords"], ["u_data"], ["udata"], ["user_session"], ["user_test"], ["v_empdtls"], ["v_empdtls_ext"], ["v_empdtls_ext_v2"], ["web_logs"]], "isEscaped": true}}

And if we wanted to get the execution log for this statement:

    curl -X POST https://demo.gethue.com/notebook/api/get_logs --data 'notebook={"type":"hive","sessions":[]}&snippet={"history_id": 17886,"type":"hive","result":{"handle":{"guid": "0J6PwGcSQaCJjagzYUBHzA==\n","secret": "uiP3IS4fR/mxkLJER5wRCg==\n","has_result_set": true}},"status":"","properties":{},"sessions":[]}'

    {"status": 0, "progress": 5, "jobs": [], "logs": "", "isFullLogs": false}

### Listing Databases

    $.post("/notebook/api/autocomplete/", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### Listing Tables

    $.post("/notebook/api/autocomplete/<DB>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### Table details and Columns

    $.post("/notebook/api/autocomplete/<DB>/<TABLE>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### Column details

    $.post("/notebook/api/autocomplete/<DB>/<TABLE>/<COL1>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

For nested columns:

    $.post("/notebook/api/autocomplete/<DB>/<TABLE>/<COL1>/<COL2>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### Listing Functions

Default functions:

    $.post("/notebook/api/autocomplete/", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      }),
      "operation": "functions"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

For a specific database:

    $.post("/notebook/api/autocomplete/<DB>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      }),
      "operation": "functions"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

For a specific function/UDF details (e.g. trunc):

    $.post("/notebook/api/autocomplete/<function_name>", {
      "snippet": ko.mapping.toJSON({
          type: "hive"
      }),
      "operation": "function"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

## File Browsing

### List

Hue's [File Browser](https://docs.gethue.com/user/browsing/#data) offer uploads, downloads and listing of data in HDFS, S3, ADLS storages.

Here is how to list the content of a path, here the S3 bucket `S3A://gethue-demo`:

    curl -X GET "https://demo.gethue.com/filebrowser/view=S3A://gethue-demo?pagesize=45&pagenum=1&filter=&sortby=name&descending=false&format=json"

    {
      ...........
      "files": [
      {
      "humansize": "0\u00a0bytes",
      "url": "/filebrowser/view=s3a%3A%2F%2Fdemo-hue",
      "stats": {
      "size": 0,
      "aclBit": false,
      "group": "",
      "user": "",
      "mtime": null,
      "path": "s3a://demo-hue",
      "atime": null,
      "mode": 16895
      },
      "name": "demo-hue",
      "mtime": "",
      "rwx": "drwxrwxrwx",
      "path": "s3a://demo-hue",
      "is_sentry_managed": false,
      "type": "dir",
      "mode": "40777"
      },
      {
      "humansize": "0\u00a0bytes",
      "url": "/filebrowser/view=S3A%3A%2F%2F",
      "stats": {
      "size": 0,
      "aclBit": false,
      "group": "",
      "user": "",
      "mtime": null,
      "path": "S3A://",
      "atime": null,
      "mode": 16895
      },
      "name": ".",
      "mtime": "",
      "rwx": "drwxrwxrwx",
      "path": "S3A://",
      "is_sentry_managed": false,
      "type": "dir",
      "mode": "40777"
      }
      ],
      ...........
    }

### Get file content

How to get the file content and its metadata. Here with the public file of demo.gethue.com [s3a://demo-hue/web_log_data/index_data.csv](https://demo.gethue.com/hue/filebrowser/view=s3a%3A%2F%2Fdemo-hue%2Fweb_log_data%2Findex_data.csv):

**Note** It needs the `XMLHttpRequest` header to return the data in json:

    curl  -X GET "https://demo.gethue.com/filebrowser/view=s3a://demo-hue/web_log_data/index_data.csv?offset=0&length=204800&compression=none&mode=text" -H "X-requested-with: XMLHttpRequest"

    {
      "show_download_button": true,
      "is_embeddable": false,
      "editable": false,
      "mtime": "October 31, 2016 03:34 PM",
      "rwx": "-rw-rw-rw-",
      "path": "s3a://demo-hue/web_log_data/index_data.csv",
      "stats": {
      "size": 6199593,
      "aclBit": false,
      ...............
      "contents": "code,protocol,request,app,user_agent_major,region_code,country_code,id,city,subapp,latitude,method,client_ip,  user_agent_family,bytes,referer,country_name,extension,url,os_major,longitude,device_family,record,user_agent,time,os_family,country_code3
        200,HTTP/1.1,GET /metastore/table/default/sample_07 HTTP/1.1,metastore,,00,SG,8836e6ce-9a21-449f-a372-9e57641389b3,Singapore,table,1.2931000000000097,GET,128.199.234.236,Other,1041,-,Singapore,,/metastore/table/default/sample_07,,103.85579999999999,Other,"demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:49 +0000] ""GET /metastore/table/default/sample_07 HTTP/1.1"" 200 1041 ""-"" ""Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)""
        ",Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org),2014-05-04T06:35:49Z,Other,SGP
        200,HTTP/1.1,GET /metastore/table/default/sample_07 HTTP/1.1,metastore,,00,SG,6ddf6e38-7b83-423c-8873-39842dca2dbb,Singapore,table,1.2931000000000097,GET,128.199.234.236,Other,1041,-,Singapore,,/metastore/table/default/sample_07,,103.85579999999999,Other,"demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:50 +0000] ""GET /metastore/table/default/sample_07 HTTP/1.1"" 200 1041 ""-"" ""Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)""
        ",Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org),2014-05-04T06:35:50Z,Other,SGP
      ...............
    }

## Data Importer

### File import

First guessing the format of the file `s3a://demo-hue/web_log_data/index_data.csv`:

    curl -X POST https://demo.gethue.com/indexer/api/indexer/guess_format  --data 'fileFormat={"inputFormat":"file","path":"s3a://demo-hue/web_log_data/index_data.csv"}'

    {"status": 0, "fieldSeparator": ",", "hasHeader": true, "quoteChar": "\"", "recordSeparator": "\\n", "type": "csv"}

Then getting some data sample as well as the column types (column names will be picked from the header line if present):

    curl -X POST https://demo.gethue.com/indexer/api/indexer/guess_field_types  --data 'fileFormat={"inputFormat":"file","path":"s3a://demo-hue/web_log_data/index_data.csv","format":{"type":"csv","fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\"","hasHeader":true,"status":0}}'

    {
      "sample": [["200", "HTTP/1.1", "GET /metastore/table/default/sample_07 HTTP/1.1", "metastore", "", "00", "SG", "8836e6ce-9a21-449f-a372-9e57641389b3", "Singapore", "table", "1.2931000000000097", "GET", "128.199.234.236", "Other", "1041", "-", "Singapore", "", "/metastore/table/default/sample_07", "", "103.85579999999999", "Other", "demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:49 +0000] \"GET /metastore/table/default/sample_07 HTTP/1.1\" 200 1041 \"-\" \"Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)\"\n", "Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)", "2014-05-04T06:35:49Z", "Other", "SGP"],
      ....
      "columns": [{"operations": [], "comment": "", "nested": [], "name": "code", "level": 0, "keyType": "string", "required": false, "precision": 10, "keep": true, "isPartition": false, "length": 100, "partitionValue": "", "multiValued": false, "unique": false, "type": "long", "showProperties": false, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "protocol", "level": 0, "keyType": "string", "required": false, "precision": 10, "keep": true, "isPartition": false, "length": 100, "partitionValue": "", "multiValued": false, "unique": false, "type": "string", "showProperties": false, "scale": 0},
      .....
    }

Then we submit via `https://demo.gethue.com/indexer/api/importer/submit` and provide the `source` and `destination` parameters. We get back an `operation id` (i.e. some SQL Editor query history id).

If the `show_command` parameter is given, the API call will instead return the generated SQL queries that will import the data.

    {"status": 0, "history_id": 17820, "handle": {"statement_id": 0, "session_type": "hive", "has_more_statements": true, "guid": "uu6K3SSWSY6mx/fbh0nm2w==\n", "previous_statement_hash": "4bee3a62b3c7142c60475021469483bff81ba09bd07b8e527179e617", "log_context": null, "statements_count": 4, "end": {"column": 53, "row": 0}, "session_id": 55, "start": {"column": 0, "row": 0}, "secret": "8mKu1bhdRtWXu82DXjDZdg==\n", "has_result_set": false, "session_guid": "fd4c667f3a5e4507:0335af7716db3d9e", "statement": "DROP TABLE IF EXISTS `default`.`hue__tmp_index_data`", "operation_type": 0, "modified_row_count": null}, "history_uuid": "bf5804f5-6f12-47a8-8ba6-0ed7032ebe93"}

## Connectors

### List

Get the list of configured [connectors](/administrator/configuration/connectors/):

    curl -L -X POST demo.gethue.com/desktop/connectors/api/instances

## Data Catalog

The [metadata API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata) is powering the external [Catalog integrations](/user/browsing/#data-catalogs).

### Searching for entities

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        sources: ko.mapping.toJSON(["sql", "hdfs", "s3"]),
        field_facets: ko.mapping.toJSON([]),
        limit: 10
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

Searching for entities with the dummy backend:

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

### Finding an entity in order to get its id

    $.get("/metadata/api/navigator/find_entity", {
        type: "table",
        database: "default",
        name: "sample_07",
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

Adding/updating a comment with the dummy backend:

    $.post("/metadata/api/catalog/update_properties/", {
        id: "22",
        properties: ko.mapping.toJSON({"description":"Adding a description"}),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

### Adding a tag with the dummy backend

    $.post("/metadata/api/catalog/add_tags/", {
      id: "22",
      tags: ko.mapping.toJSON(["usage"]),
      interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
       "id": "32",
       "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
       console.log(ko.mapping.toJSON(data));
    });

### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
      "id": "32",
      "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


### Getting the model mapping

    $.get("/metadata/api/catalog/models/properties/mappings/", function(data) {
      console.log(ko.mapping.toJSON(data));
    });


### Getting a namespace

    $.post("/metadata/api/catalog/namespace/", {
      namespace: 'huecatalog'
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### Creating a namespace

    $.post("/metadata/api/catalog/namespace/create/", {
      "namespace": "huecatalog",
      "description": "my desc"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


### Creating a namespace property

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

### Map a namespace property to a class

    $.post("/metadata/api/catalog/namespace/property/map/", {
      "class": "hv_view",
      "properties": ko.mapping.toJSON([{
          namespace: "huecatalog",
          name: "relatedQueries"
      }])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });



# Programming

Here is some overview about using the Python commands an shell and some examples below:

* [Hue API: Execute some builtin or shell commands](http://gethue.com/hue-api-execute-some-builtin-commands/).
* [How to manage the Hue database with the shell](http://gethue.com/how-to-manage-the-hue-database-with-the-shell/).

## Python

### Making a user admin

Via the Hue shell:

    build/env/bin/hue shell

Then type something similar to:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

### Changing user password

In the Hue shell:

    from django.contrib.auth.models import User

    user = User.objects.get(username='example')
    user.set_password('some password')
    user.save()


### Counting user documents

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
