---
title: "REST"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

Interact with the Query server (e.g. submit a SQL query, download some S3 files, search for a table...) via a REST API.

Users authenticate with the same credentials as they would do in the Browser login page.

## Quickstart

The API can be called directly via REST.

First [authenticate](/developer/api/rest/#authentication) with your account credentials and get a token. Then provide the token in all following requests as header, e.g.

    curl -X POST https://demo.gethue.com/api/editor/execute/hive --data 'statement=SHOW TABLES' -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

The default content type is form data, e.g.:

    -H "Content-Type: application/x-www-form-urlencoded" -d 'username=demo&password=demo'

It is possible to submit data in JSON format for the calls also reading the data via `request.body`:

    -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo"}'

### Curl

Calling without credentials:

    curl -X POST https://demo.gethue.com/api/query/create_notebook -H "Content-Type: application/json"

    {"detail":"Authentication credentials were not provided."}

Authenticating and getting a [JWT token](https://jwt.io/):

    curl -X POST https://demo.gethue.com/api/token/auth/ -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo"}'

    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

Re-using the token when making actual calls:

    curl -X POST https://demo.gethue.com/api/query/create_notebook -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

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

    response = session.post("https://demo.gethue.com/api/token/auth", data=data)
    print('Auth: %s %s' % ('success' if response.status_code == 200 else 'error', response.status_code))

    token = json.loads(response.content)['access']
    print('Token: %s' % token)

    response = requests.post(
      'https://demo.gethue.com/api/query/autocomplete',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data={'snippet': json.dumps({"type":"1"})}
    )
    print(response.status_code)
    print(response.text)

### JavaScript

In the meantime, with Axios:

    <script src="https://unpkg.com/axios@0.21.1/dist/axios.min.js"></script>

    <script type="text/javascript">
      const API_URL = "https://demo.gethue.com";
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

The API authenticates via the [authentication backends](/administrator/configuration/server/#authentication) of the server (same as going via the login page). This is consistent and users are free to interact via their browsers or API.

Then a JWT token is returned and needs to be passed as a bearer in the headers for all the API calls.

**Wrong credentials**: on bad authentication, it will return a `401 unauthorized` response, e.g.:

    curl -X POST https://demo.gethue.com/api/editor/create_notebook -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

    {"detail":"Given token not valid for any token type","code":"token_not_valid","messages":[{"token_class":"AccessToken","token_type":"access","message":"Token is invalid or expired"}]}

    [09/Jul/2021 23:58:40 -0700] access       INFO     demo.gethue.com -anon- - "POST /api/editor/create_notebook HTTP/1.1" returned in 2ms 401 183 (mem: 124mb)

### Authenticate

Provide login credentials and get a [JWT token](https://jwt.io/):

    curl -X POST https://demo.gethue.com/api/token/auth -d 'username=demo&password=demo'

    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

And keep the `access` token as the value of the bearer header in the API calls.

### Validate token

The validity (i.e. did it expire?) of an `access` token can be verified:

    curl -X POST https://demo.gethue.com/api/token/verify/ -d 'token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA'

### Refresh token

Similarly, an `access` token validity can be extended via a refresh sending the `refresh` token obtained in the initial authentication.

    curl -X POST https://demo.gethue.com/api/token/refresh/ -d 'refresh=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ'

### Custom JWT Authentication

Users can authenticate with their own JWT with the help of custom backend **(supporting RSA256)**. To enable it, add the following in the `hue.ini`:

    [desktop]
    [[auth]]
    [[[jwt]]]
    is_enabled=true
    key_server_url=https://ext_authz:8000
    issuer=<your_external_app>
    audience=hue

Also, to allow Hue to send this JWT to external services like Impala, enable the following flag in `hue.ini`:

    [desktop]
    use_thrift_http_jwt=true

If you wish to implement your own custom auth (having customized connection with external auth server or using different signing algorithm etc.), then you can follow the [Django REST Framework custom pluggability](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication) and add like this [dummy auth](https://github.com/cloudera/hue/blob/d75c8fc7b307fc67ef9a2a58e36cfb4ace6cd461/desktop/core/src/desktop/auth/api_authentications.py#L119).

And then, add it in `hue.ini` (comma separated and in order of priority if multiple auth backends present):

    [desktop]
    [[auth]]
    api_auth=<your_own_custom_auth_backend>

## SQL Querying

### Execute a Query

Now that we are authenticated, here is how to execute a `SHOW TABLES` SQL query via the `hive` connector. You could repeat the steps with any query you want, e.g. `SELECT * FROM web_logs LIMIT 100`.

Selecting the **dialect** argument in `/api/editor/execute/<dialect>`:
- **hive**: select the configured Hive dialect
- **1**: select the connector id 1
- **hive-1**: select the interpreter id 1 and hints that it is a Hive dialect
- If blank will pick the first interpreter

Optional parameter:
- **database**: select a specific database

For a `SHOW TABLES`, first we send the query statement:

    curl -X POST https://demo.gethue.com/api/editor/execute/hive --data 'statement=SHOW TABLES'

    {"status": 0, "history_id": 17880, "handle": {"statement_id": 0, "session_type": "hive", "has_more_statements": false, "guid": "EUI32vrfTkSOBXET6Eaa+A==\n", "previous_statement_hash": "3070952e55d733fb5bef249277fb8674989e40b6f86c5cc8b39cc415", "log_context": null, "statements_count": 1, "end": {"column": 10, "row": 0}, "session_id": 63, "start": {"column": 0, "row": 0}, "secret": "RuiF0LEkRn+Yok/gjXWSqg==\n", "has_result_set": true, "session_guid": "c845bb7688dca140:859a5024fb284ba2", "statement": "SHOW TABLES", "operation_type": 0, "modified_row_count": null}, "history_uuid": "63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"}

Then check the operation (its value is **history_uuid** from the execute response) status until its result is ready to fetch:

    curl -X POST https://demo.gethue.com/api/editor/check_status --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "query_status": {"status": "available", "has_result_set": true}}

And now ask for the resultset of the statement:

    curl -X POST https://demo.gethue.com/api/editor/fetch_result_data --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "result": {"has_more": true, "type": "table", "meta": [{"comment": "from deserializer", "type": "STRING_TYPE", "name": "tab_name"}], "data": [["adavi"], ["adavi1"], ["adavi2"], ["ambs_feed"], ["apx_adv_deduction_data_process_total"], ["avro_table"], ["avro_table1"], ["bb"], ["bharath_info1"], ["bucknew"], ["bucknew1"], ["chungu"], ["cricket3"], ["cricket4"], ["cricket5_view"], ["cricketer"], ["cricketer_view"], ["cricketer_view1"], ["demo1"], ["demo12345"], ["dummy"], ["embedded"], ["emp"], ["emp1_sept9"], ["emp_details"], ["emp_sept"], ["emp_tbl1"], ["emp_tbl2"], ["empdtls"], ["empdtls_ext"], ["empdtls_ext_v2"], ["employee"], ["employee1"], ["employee_ins"], ["empppp"], ["events"], ["final"], ["flight_data"], ["gopalbhar"], ["guruhive_internaltable"], ["hell"], ["info1"], ["lost_messages"], ["mnewmyak"], ["mortality"], ["mscda"], ["myak"], ["mysample"], ["mysample1"], ["mysample2"], ["network"], ["ods_t_exch_recv_rel_wfz_stat_szy"], ["olympicdata"], ["p_table"], ["partition_cricket"], ["partitioned_user"], ["s"], ["sample"], ["sample_07"], ["sample_08"], ["score"], ["stg_t_exch_recv_rel_wfz_stat_szy"], ["stocks"], ["students"], ["studentscores"], ["studentscores2"], ["t1"], ["table_name"], ["tablex"], ["tabley"], ["temp"], ["test1"], ["test2"], ["test21"], ["test_info"], ["topage"], ["txnrecords"], ["u_data"], ["udata"], ["user_session"], ["user_test"], ["v_empdtls"], ["v_empdtls_ext"], ["v_empdtls_ext_v2"], ["web_logs"]], "isEscaped": true}}

And if we wanted to get the execution log for this statement:

    curl -X POST https://demo.gethue.com/api/editor/get_logs --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "progress": 5, "jobs": [], "logs": "", "isFullLogs": false}

Same but in Python:

    params = {
      'statement': 'SELECT 1, 2, 3',
    }

    response = requests.post(
      'https://demo.gethue.com/api/editor/execute/mysql',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data=params
    )
    print(response.status_code)
    print(response.text)

    resp_content = json.loads(response.text)

    data = {
      'operationId': resp_content['history_uuid'],
    }

    response = requests.post(
      'https://demo.gethue.com/api/editor/check_status',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data=data
    )
    print(response.status_code)
    print(response.text)


    response = requests.post(
      'https://demo.gethue.com/api/editor/fetch_result_data',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data=data
    )
    print(response.status_code)
    print(response.text)

### Listing Databases

    curl -X POST https://demo.gethue.com/api/editor/autocomplete/

### Database details

    curl -X POST https://demo.gethue.com/api/editor/autocomplete/<DB>/

Describe database API:

    curl -X POST https://demo.gethue.com/api/editor/describe/<DB>/ -d 'source_type=mysql'

- **source_type:** select the configured databases (e.g. `hive`) or connector ID (e.g. `1`)

### Table details

    curl -X POST https://demo.gethue.com/api/editor/autocomplete/<DB>/<TABLE>/

Describe table API:

    curl -X POST https://demo.gethue.com/api/editor/describe/<DB>/<TABLE>/ -d 'source_type=1'

- **source_type:** select the configured databases (e.g. `hive`) or connector ID (e.g. `1`)

Analyze API:

    curl -X POST https://demo.gethue.com/api/<DIALECT>/analyze/<DB>/<TABLE>/

- Currently supported **dialects:** impala, beeswax (hive)

Sample table data API:

    curl -X POST https://demo.gethue.com/api/editor/sample/<DB>/<TABLE>/

### Column details

    curl -X POST https://demo.gethue.com/api/editor/autocomplete/<DB>/<TABLE>/<COL1>/

Analyze API:

    curl -X POST https://demo.gethue.com/api/<DIALECT>/analyze/<DB>/<TABLE>/<COL1>/

- Currently supported **dialects:** impala, beeswax (hive)

Sample column data API:

    curl -X POST https://demo.gethue.com/api/editor/sample/<DB>/<TABLE>/<COL1>/

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

### Query history

We can choose a dialect for `doc_type` e.g. impala, mysql, hive, phoenix, etc.

    curl -X GET https://demo.gethue.com/api/editor/get_history?doc_type=hive

    {"status": 0, "count": 3, "history": [{"name": "", "id": 2008, "uuid": "5b48c678-1224-4863-b523-3baab82402a7", "type": "query-hive", "data": {"statement": "CREATE TABLE w12( Name STRING, Money BIGINT )", "lastExecuted": 1621502970360, "status": "failed", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2008"}, {"name": "", "id": 2006, "uuid": "1cd32ae0-9b61-46ae-8fd4-72c4255209c3", "type": "query-hive", "data": {"statement": "CREATE TABLE q13( Name STRING, Money BIGINT )", "lastExecuted": 1621498889058, "status": "expired", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2006"}, {"name": "", "id": 2003, "uuid": "e5ec1fa4-1a36-4e42-a814-a685b0142223", "type": "query-hive", "data": {"statement": "CREATE TABLE q11( Name STRING, Money BIGINT );\nINSERT INTO q11 VALUES ('abc', 100);", "lastExecuted": 1621498771619, "status": "expired", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2003"}], "message": "History fetched"}

### Get Configuration

    curl -X POST https://demo.gethue.com/api/get_config/

    {"app_config": {"editor": {"name": "editor", "displayName": "Editor", "buttonName": "Query", "interpreters": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, {"name": "notebook", "type": "notebook", "displayName": "Notebook", "buttonName": "Notebook", "tooltip": "Notebook", "page": "/notebook", "is_sql": false, "dialect": "notebook"}], "default_limit": 5000, "interpreter_names": ["mysql", "notebook"], "page": "/editor/?type=mysql", "default_sql_interpreter": "mysql"}, "catalogs": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "page": "/editor/?type=mysql", "is_sql": true, "is_catalog": true}], "browser": {"name": "browser", "displayName": "Browsers", "buttonName": "Browse", "interpreters": [{"type": "hdfs", "displayName": "Files", "buttonName": "Browse", "tooltip": "Files", "page": "/filebrowser/view=%2Fuser%2Fdemo"}, {"type": "tables", "displayName": "Tables", "buttonName": "Browse", "tooltip": "Tables", "page": "/metastore/tables"}, {"type": "yarn", "displayName": "Jobs", "buttonName": "Jobs", "tooltip": "Jobs", "page": "/jobbrowser/"}, {"type": "importer", "displayName": "Importer", "buttonName": "Import", "tooltip": "Importer", "page": "/indexer/importer"}], "interpreter_names": ["hdfs", "tables", "yarn", "importer"]}, "home": {"name": "home", "displayName": "Home", "buttonName": "Documents", "interpreters": [], "page": "/home"}}, "main_button_action": {"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, "button_actions": [{"name": "editor", "displayName": "Editor", "buttonName": "Query", "interpreters": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, {"name": "notebook", "type": "notebook", "displayName": "Notebook", "buttonName": "Notebook", "tooltip": "Notebook", "page": "/notebook", "is_sql": false, "dialect": "notebook"}], "default_limit": 5000, "interpreter_names": ["mysql", "notebook"], "page": "/editor/?type=mysql", "default_sql_interpreter": "mysql"}], "default_sql_interpreter": "mysql", "cluster_type": "direct", "has_computes": false, "hue_config": {"enable_sharing": true, "is_admin": true}, "clusters": [{"id": "default", "name": "default", "type": "direct", "credentials": {}}], "documents": {"types": ["directory", "gist", "query-mysql"]}, "status": 0}

## File Browsing

Hue's [File Browser](https://docs.gethue.com/user/browsing/#data) offer uploads, downloads, operations (create, delete, chmod...) and listing of data in HDFS (`hdfs://` or no prefix), S3 (`s3a://` prefix), ADLS (`adls://` or `abfs://` prefixes) storages.

### Get Filesystems

Get the filesystems details such as configured filesystems in Hue which user has access to and its home directories:

    curl -X GET https://demo.gethue.com/api/storage/filesystems
    
    [{"file_system": "hdfs", "user_home_directory": "/user/demo"}, {"file_system": "s3a", "user_home_directory": "s3a://<some_s3_path>"}, {"file_system": "abfs", "user_home_directory": "abfs://<some_abfs_path>"}]

### List

Here is how to list the content of a path, here a S3 bucket `s3a://demo-gethue`:

    curl -X GET https://demo.gethue.com/api/storage/view=s3a://demo-gethue

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
      "path": "s3a://demo-gethue",
      "atime": null,
      "mode": 16895
      },
      "name": "demo-hue",
      "mtime": "",
      "rwx": "drwxrwxrwx",
      "path": "s3a://demo-gethue",
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

Some of the parameters:
 - pagesize=45
 - pagenum=1
 - filter=
 - sortby=name
 - descending=false

E.g. `?pagesize=45&pagenum=1&filter=&sortby=name&descending=false`

### Preview

How to get the some of the file content and its stats/metadata.

Example with a S3 file:

    curl -X GET https://demo.gethue.com/api/storage/view=s3a://demo-gethue/data/web_logs/index_data.csv

    {
      "show_download_button": true,
      "is_embeddable": false,
      "editable": false,
      "mtime": "October 31, 2016 03:34 PM",
      "rwx": "-rw-rw-rw-",
      "path": "s3a://demo-gethue/data/web_logs/index_data.csv",
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

Some of the parameters:
- offset=0
- length=204800
- compression=none
- mode=text

E.g. `?offset=0&length=204800&compression=none&mode=text`

### Download

Specify a path of the file to download:

    curl -X GET https://demo.gethue.com/api/storage/download=/user/hue/weblogs.csv

    curl -X GET https://demo.gethue.com/api/storage/download=s3a://demo-gethue/data/web_logs/index_data.csv

- download: file path from any configured remote file system

### Upload

Upload a local file to a remote destination folder:

    curl -X POST https://demo.gethue.com/api/storage/upload/file?dest=s3a://demo-gethue/web_log_data/ --form hdfs_file=@README.md

- **dest:** folder path will be created if it does not exist yet
- **hdfs_file:** relative or absolute path to a file. It should be read more like `local_file`, it is not related to HDFS

### Create Directory

Create a directory at a specific path:

    curl -X POST https://demo.gethue.com/api/storage/mkdir
    
- **name:** name of the directory
- **path:** specific path where user wants to create the directory

## Data Importer

### File import

We have 2 options here.

- **Remote file**
  + In this option we are choosing a file from HDFS/S3 file system.


- **Small Local file**
  + In this option we can choose a file from local file system.

We need to pass two main parameters `inputFormat` and `path` to the `guess_format` api.
  - For example:
    + In remote file, parameters are `inputFormat=file` and `path=s3a://demo-gethue/data/web_logs/index_data.csv`
    + In small local file, parameter are `inputFormat=localfile`  and `path=/Users/hue/Downloads/test_demo/flights11.csv`

**Note:** Here value of `inputFormat` is constant according to the option we choose and the value of `path` should be from valid file system as explained above.

Now guessing the format of the file:

    curl -X POST https://demo.gethue.com/api/indexer/guess_format  --data 'fileFormat={"inputFormat":"file","path":"s3a://demo-gethue/data/web_logs/index_data.csv"}'

    {"status": 0, "fieldSeparator": ",", "hasHeader": true, "quoteChar": "\"", "recordSeparator": "\\n", "type": "csv"}

Then getting some data sample as well as the column types (column names will be picked from the header line if present):

    curl -X POST https://demo.gethue.com/api/indexer/guess_field_types  --data 'fileFormat={"inputFormat":"file","path":"s3a://demo-gethue/data/web_logs/index_data.csv","format":{"type":"csv","fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\"","hasHeader":true,"status":0}}'

    {
      "sample": [["200", "HTTP/1.1", "GET /metastore/table/default/sample_07 HTTP/1.1", "metastore", "", "00", "SG", "8836e6ce-9a21-449f-a372-9e57641389b3", "Singapore", "table", "1.2931000000000097", "GET", "128.199.234.236", "Other", "1041", "-", "Singapore", "", "/metastore/table/default/sample_07", "", "103.85579999999999", "Other", "demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:49 +0000] \"GET /metastore/table/default/sample_07 HTTP/1.1\" 200 1041 \"-\" \"Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)\"\n", "Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)", "2014-05-04T06:35:49Z", "Other", "SGP"],
      ....
      "columns": [{"operations": [], "comment": "", "nested": [], "name": "code", "level": 0, "keyType": "string", "required": false, "precision": 10, "keep": true, "isPartition": false, "length": 100, "partitionValue": "", "multiValued": false, "unique": false, "type": "long", "showProperties": false, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "protocol", "level": 0, "keyType": "string", "required": false, "precision": 10, "keep": true, "isPartition": false, "length": 100, "partitionValue": "", "multiValued": false, "unique": false, "type": "string", "showProperties": false, "scale": 0},
      .....
    }

Then we submit via `https://demo.gethue.com/api/indexer/importer/submit` and provide the `source` and `destination` parameters. We get back an `operation id` (i.e. some SQL Editor query history id).

If the `show_command` parameter is given, the API call will instead return the generated SQL queries that will import the data.

    curl -X  POST https://demo.gethue.com/api/indexer/importer/submit --data 'source={"sourceType":"hive","inputFormat":"localfile","path":"/Users/hue/Downloads/test_demo/flights_13.csv","format":{"hasHeader":true}}&destination={"sourceType":"hive","name":"default.test1","outputFormat":"table","columns":[{"name":"date","type":"timestamp"},{"name":"hour","type":"bigint"},{"name":"minute","type":"bigint"},{"name":"dep","type":"bigint"},{"name":"arr","type":"bigint"},{"name":"dep_delay","type":"bigint"},{"name":"arr_delay","type":"bigint"},{"name":"carrier","type":"string"},{"name":"flight","type":"bigint"},{"name":"dest","type":"string"},{"name":"plane","type":"string"},{"name":"cancelled","type":"boolean"},{"name":"time","type":"bigint"},{"name":"dist","type":"bigint"}], "nonDefaultLocation":""}'

    {"status": 0, "handle": {"secret": "C5vnlrpVTxuOpHZfTrLfmg==", "guid": "8ytLYHTsTlq8vYSiYXoyKQ==", "operation_type": 0, "has_result_set": false, "modified_row_count": null, "log_context": null, "session_guid": "d04b246456e87e61:b86340ae83f6a586", "session_id": 748, "session_type": "hive", "statement_id": 0, "has_more_statements": false, "statements_count": 1, "previous_statement_hash": "94ea45e37bbbbc7bb7e20b5d0efe0db8c9794dd526b5a3386bae3596", "start": {"row": 0, "column": 0}, "end": {"row": 0, "column": 305}, "statement": "CREATE TABLE IF NOT EXISTS default.yuyu11 (\n  `date` timestamp,\n  `hour` bigint,\n  `minute` bigint,\n  `dep` bigint,\n  `arr` bigint,\n  `dep_delay` bigint,\n  `arr_delay` bigint,\n  `carrier` string,\n  `flight` bigint,\n  `dest` string,\n  `plane` string,\n  `cancelled` boolean,\n  `time` bigint,\n  `dist` bigint)"}, "history_id": 2492, "history_uuid": "c60dc4dd-4d39-42fd-85f5-af155d99b626"}

## Connectors

### List

Get the list of configured [connectors](/administrator/configuration/connectors/):

    curl -X GET https://demo.gethue.com/api/connector/instances

    {"connectors": [{"category": "editor", "category_name": "Editor", "description": "", "values": []}, {"category": "browsers", "category_name": "Browsers", "description": "", "values": []}, {"category": "catalogs", "category_name": "Catalogs", "description": "", "values": []}, {"category": "optimizers", "category_name": "Optimizers", "description": "", "values": []}, {"category": "schedulers", "category_name": "Schedulers", "description": "", "values": []}, {"category": "plugins", "category_name": "Plugins", "description": "", "values": []}]}

### Types

    curl -X GET https://demo.gethue.com/api/connector/types

    { "connectors": [ { "category": "editor", "category_name": "Editor", "description": "", "values": [ { "dialect": "hive", "nice_name": "Hive", "description": "Recommended", "category": "editor", "interface": "hiveserver2", "settings": [ { "name": "server_host", "value": "localhost" }, { "name": "server_port", "value": 10000 }, { "name": "is_llap", "value": false }, { "name": "use_sasl", "value": true } ], "properties": { "is_sql": true, "sql_identifier_quote": "`", "sql_identifier_comment_single": "--", "has_catalog": false, "has_database": true, "has_table": true, "has_live_queries": false, "has_optimizer_risks": true, "has_optimizer_values": true, "has_auto_limit": false, "has_reference_language": true, "has_reference_functions": true, "has_use_statement": true } },
    ...........
    { "category": "browsers", "category_name": "Browsers", "description": "", "values": [ { "nice_name": "HDFS", "dialect": "hdfs", "interface": "rest", "settings": [ { "name": "server_url", "value": "http://localhost:50070/webhdfs/v1" }, { "name": "default_fs", "value": "fs_defaultfs=hdfs://localhost:8020" } ], "category": "browsers", "description": "", "properties": {} },
    ...........
    { "nice_name": "S3", "dialect": "s3", "settings": [], "category": "browsers", "description": "", "properties": {} }, { "nice_name": "ADLS", "dialect": "adls-v1", "settings": [], "category": "browsers", "description": "", "properties": {} } ] }, { "category": "catalogs", "category_name": "Catalogs", "description": "", "values": [ { "nice_name": "Hive Metastore", "dialect": "hms", "interface": "hiveserver2", "settings": [ { "name": "server_host", "value": "" }, { "name": "server_port", "value": "" } ], "category": "catalogs", "description": "", "properties": {} }, { "nice_name": "Atlas", "dialect": "atlas", "interface": "rest", "settings": [], "category": "catalogs", "description": "", "properties": {} },
    ...........
    ] }, { "category": "optimizers", "category_name": "Optimizers", "description": "", "values": [ { "nice_name": "Optimizer", "dialect": "optimizer", "settings": [], "category": "optimizers", "description": "", "properties": {} } ] }, { "category": "schedulers", "category_name": "Schedulers", "description": "", "values": [ { "nice_name": "Oozie", "dialect": "oozie", "settings": [], "category": "schedulers", "description": "", "properties": {} },
    ...........
    ] }, { "category": "plugins", "category_name": "Plugins", "description": "", "values": [] } ], "categories": [ { "name": "Editor", "type": "editor", "description": "" }, { "name": "Browsers", "type": "browsers", "description": "" }, { "name": "Catalogs", "type": "catalogs", "description": "" }, { "name": "Optimizers", "type": "optimizers", "description": "" }, { "name": "Schedulers", "type": "schedulers", "description": "" }, { "name": "Plugins", "type": "plugins", "description": "" } ] }

### Create

First step is to get the config of the connector we want to instantiate. In input we pick a type of connector from the list of above types by specifying its `dialect` and `interface` names.

    curl -X POST https://demo.gethue.com/api/connector/instance/new/<DIALECT>/<INTERFACE>

And get back a template that we send to the /update call:

    curl -X POST https://demo.gethue.com/api/connector/instance/new/hive/sqlalchemy -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Get

    curl -X GET https://demo.gethue.com/api/connector/instance/get/<ID>

### Update

This is the same as creating a new connector instance, but as we provide the `id` we will update the existing instance:

    curl -X POST https://demo.gethue.com/api/connector/instance/update -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"id":"41","category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Delete

    curl -X POST https://demo.gethue.com/api/connector/instance/delete -d 'connector={"id": "1"}'

### Test

Check if the connectivity is healthy:

    curl -X POST https://demo.gethue.com/api/connector/instance/test/ -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"id":"41","category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Examples

Install or update the connector examples:

    curl -X POST https://demo.gethue.com/api/connector/examples/install/

## IAM

### Get users

Get user records in Hue. Requires **admin privileges**.

    curl -X GET https://demo.gethue.com/api/iam/get_users

Optional GET params:
- **username:** filter by username
- **groups:** filter by specific group
- **is_active:** filter by active status

E.g. `?username=demo&groups=default&is_active=true`

Search user records by list of user IDs. Requires **admin privileges**.

    curl -X GET https://demo.gethue.com/api/iam/users?userids=[1100714,1100715]
    
    {"users": [{"id": 1100714,"username": "demo","first_name": "","last_name": "","email": "","last_login": "2021-10-06T01:36:49.663","editURL": "/useradmin/users/edit/demo"},{"id": 1100715,"username": "hue","first_name": "","last_name": "","email": "","last_login": "2021-08-11T07:15:48.793","editURL": "/useradmin/users/edit/hue"}]}

User list_for_autocomplete API:

    curl -X GET https://demo.gethue.com/api/iam/users/autocomplete
 
Optional GET params:
- **extend_user:** true or false (info about each user's groups)
- **filter:** search term
- **count:** Number of records (default is 100)

## Data Catalog

The [metadata API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata) is powering the external [Catalog integrations](/user/browsing/#data-catalogs).

### Searching for entities
    
    curl -X POST https://demo.gethue.com/api/metadata/search/entities_interactive/ -d 'query_s="*sample"&sources=["documents", "sql", "hdfs", "s3"]'

Some of the parameters:
- **query_s:** search term
- **sources:** sources to search from `["documents", "sql", "hdfs", "s3"]`
- **field_facets:** `['type', 'owner', 'tags', 'lastModified']`
- **limit:** 10

Searching for entities with the `dummy` catalog:

    curl -X POST https://demo.gethue.com/api/metadata/search/entities_interactive/ -d 'query_s="*sample"&interface="dummy"'

### Finding an entity

e.g. in order to get its id:

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

### Adding a tag

    $.post("/metadata/api/catalog/add_tags/", {
      id: "22",
      tags: ko.mapping.toJSON(["usage"]),
      interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

### Deleting a property

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

### Map a namespace property

To a class:

    $.post("/metadata/api/catalog/namespace/property/map/", {
      "class": "hv_view",
      "properties": ko.mapping.toJSON([{
          namespace: "huecatalog",
          name: "relatedQueries"
      }])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });
