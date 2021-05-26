---
title: "REST"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

Interact with the API server (e.g. submit a SQL query, list some S3 files in a bucket, search for a table...) with via a REST API.

Users authenticate with the same credentials as they would do in the Browser login page.

## Quickstart

The API can be called directly via REST. Some JavaScript and Python wrappers are not documented yet.

### Curl

Calling without credentials:

    curl -X POST -H "Content-Type: application/json" http://localhost:9000/api/query/create_notebook
    {"detail":"Authentication credentials were not provided."}

Authenticating and getting a [JWT token](https://jwt.io/):

    curl -X POST -H "Content-Type: application/json" -d '{"username": "hue", "password": "hue"}' http://localhost:9000/api/token/auth/
    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

Re-using the token when making actual calls:

    url -X POST -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"   http://localhost:9000/api/v1/create_notebook
    {"status": 0, "notebook": {"name": "My Notebook", "uuid": "1e23314f-b01e-4c18-872f-dc143475f063", "description": "", "type": "notebook", "isSaved": false, "isManaged": false, "skipHistorify": false, "sessions": [], "snippets": [], "directoryUuid": null}}

### Python

In this code snippet, we will use the [requests](https://pypi.org/project/requests/) library:

    pip install requests

And then:

    import json
    import requests

    session = requests.Session()

    data = {
      'username': 'demo',
      'password': 'demo',
    }

    response = session.post("http://localhost:9000/api/token/auth", data=data)
    print('Auth: %s %s' % ('success' if response.status_code == 200 else 'error', response.status_code))

    token = json.loads(response.content)['access']
    print('Token: %s' % token)

    response = requests.post(
      'http://localhost:9000/api/query/autocomplete',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data={'snippet': json.dumps({"type":"mysql"})}
    )
    print(response.status_code)
    print(response.text)

### JavaScript

In the meantime, with Axios:

    <script src="https://unpkg.com/axios@0.21.1/dist/axios.min.js"></script>

    <script type="text/javascript">
      // const API_URL = "https://api.gethue.com"; // http://localhost:8005
      const API_URL = "/";
      axios.defaults.baseURL = API_URL;

      axios.post('api/token/auth/', {username: "hue", password: "hue"}).then(function(data) {
        console.log(data['data']);

        // Util to check if cached token is still valid before asking to auth for a new one
        axios.post('api/token/verify/', {token: data['access']});

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + data['access'];
      }).then(function() {
        axios.post('api/query/sqlite', {statement:"SELECT 1000, 1001"}).then(function(data) {
          console.log(data['data']);
        });

        axios.post('api/connectors/types/').then(function(data) {
          console.log(data['data']);
        });
      });
    </script>

## Authentication

The API only supports JWT but users need to provide the credentials they are using in the regular login form or [authentication backends](/administrator/configuration/server/#authentication). This is consistent and users are free to interact with the service via their Browser or API.

**Wrong credentials**: there is currently no error on bad authentication but instead a 302 redirect to the login page, e.g.:

    curl -X POST -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM" http://localhost:9000/notebook/execute/v1/create_notebook

    [21/May/2021 16:26:46 -0700] middleware   INFO     Redirecting to login page: /notebook/execute/v1/create_notebook
    [21/May/2021 16:26:46 -0700] access       INFO     127.0.0.1 -anon- - "POST /notebook/execute/v1/create_notebook HTTP/1.1" - (mem: 172mb)-- login redirection
    [21/May/2021 16:26:46 -0700] access       INFO     127.0.0.1 -anon- - "POST /notebook/execute/v1/create_notebook HTTP/1.1" returned in 4ms 302 0

It is possible to submit data in **JSON format**:

    -H "Content-Type: application/json" -d '{"username": "hue", "password": "hue"}'

### Authentication

Authenticating and getting a [JWT token](https://jwt.io/):

    curl -X POST -d 'username=hue,password=hue' http://localhost:9000/api/token/
    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

### Check token

    curl -X POST -d 'token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA' http://localhost:9000/api/token/verify/

### Refresh token

    curl -X POST 'refresh=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ' http://localhost:9000/api/token/refresh/


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
