---
title: "REST"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

Interact with the Query server (e.g. submit a SQL query, upload some files in cloud storages, search for a table...) via a REST API.

Users authenticate with the same credentials as they would do in the Browser login page.

## Quickstart

The API can be called directly via REST.

First [authenticate](/developer/api/rest/#authentication) with your account credentials and get a token. Then provide the token in all following requests as header, e.g.

    curl -X POST https://demo.gethue.com/api/v1/editor/execute/hive --data 'statement=SHOW TABLES' -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

The default content type is form data, e.g.:

    -H "Content-Type: application/x-www-form-urlencoded" -d 'username=demo&password=demo'

It is possible to submit data in JSON format for the calls also reading the data via `request.body`:

    -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo"}'

### Curl

Calling without credentials:

    curl -X POST https://demo.gethue.com/api/v1/query/create_notebook -H "Content-Type: application/json"

    {"detail":"Authentication credentials were not provided."}

Authenticating and getting a [JWT token](https://jwt.io/):

    curl -X POST https://demo.gethue.com/api/v1/token/auth/ -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo"}'

    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

Re-using the token when making actual calls:

    curl -X POST https://demo.gethue.com/api/v1/query/create_notebook -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

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

    response = session.post("https://demo.gethue.com/api/v1/token/auth", data=data)
    print('Auth: %s %s' % ('success' if response.status_code == 200 else 'error', response.status_code))

    token = json.loads(response.content)['access']
    print('Token: %s' % token)

    response = requests.post(
      'https://demo.gethue.com/api/v1/query/autocomplete',
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

      axios.post('api/v1/token/auth/', {username: "hue", password: "hue"}).then(function(data) {
        console.log(data['data']);

        // Util to check if cached token is still valid before asking to auth for a new one
        axios.post('api/v1/token/verify/', {token: data['access']});

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + data['access'];
      }).then(function() {
        axios.post('api/v1/query/sqlite', {statement:"SELECT 1000, 1001"}).then(function(data) {
          console.log(data['data']);
        });

        axios.post('api/v1/connectors/types/').then(function(data) {
          console.log(data['data']);
        });
      });
    </script>

## Authentication

The API authenticates via the [authentication backends](/administrator/configuration/server/#authentication) of the server (same as going via the login page). This is consistent and users are free to interact via their browsers or API.

Then a JWT token is returned and needs to be passed as a bearer in the headers for all the API calls.

**Wrong credentials**: on bad authentication, it will return a `401 unauthorized` response, e.g.:

    curl -X POST https://demo.gethue.com/api/v1/editor/create_notebook -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM5NjMxLCJqdGkiOiI0NTY3NTA4MzM5YjY0MjFmYTMzZDJjMzViZWUyMDAyMCIsInVzZXJfaWQiOjF9.qrMNrr69eo38dOsV2aYp8k6WqBeyJZkbSuavxA_o_kM"

    {"detail":"Given token not valid for any token type","code":"token_not_valid","messages":[{"token_class":"AccessToken","token_type":"access","message":"Token is invalid or expired"}]}

    [09/Jul/2021 23:58:40 -0700] access       INFO     demo.gethue.com -anon- - "POST /api/v1/editor/create_notebook HTTP/1.1" returned in 2ms 401 183 (mem: 124mb)

### Authenticate

Provide login credentials and get a [JWT token](https://jwt.io/):

    curl -X POST https://demo.gethue.com/api/v1/token/auth -d 'username=demo&password=demo'

    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA"}

And keep the `access` token as the value of the bearer header in the API calls.

### Validate token

The validity (i.e. did it expire?) of an `access` token can be verified:

    curl -X POST https://demo.gethue.com/api/v1/token/verify/ -d 'token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIxNjM4NTMxLCJqdGkiOiJhZjgwN2E0ZjBmZDI0ZWMxYWQ2NTUzZjEyMjIyYzU4YyIsInVzZXJfaWQiOjF9.dQ1P3hbzSytp9-o8bWlcOcwrdwRVy95M2Eolph92QMA'

### Refresh token

Similarly, an `access` token validity can be extended via a refresh sending the `refresh` token obtained in the initial authentication.

    curl -X POST https://demo.gethue.com/api/v1/token/refresh/ -d 'refresh=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyMTcyNDYzMSwianRpIjoiOGM0NDRjYzRhN2VhNGMxZDliMGZhNmU1YzUyMjM1MjkiLCJ1c2VyX2lkIjoxfQ.t6t7_eYrNhpGN3-Jz5MDLXM8JtGP7V9Y9lacOTInqqQ'

### Custom JWT Authentication

Users can authenticate with their own JWT with the help of custom backend **(supporting RSA256)**. To enable it, add the following in the `hue.ini`:

    [desktop]
    [[auth]]
    [[[jwt]]]
    key_server_url=https://ext_authz:8000
    issuer=<your_external_app>
    audience=hue
    username_header=sub

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

Selecting the **dialect** argument in `/api/v1/editor/execute/<dialect>`:
- **hive**: select the configured Hive dialect
- **1**: select the connector id 1
- **hive-1**: select the interpreter id 1 and hints that it is a Hive dialect
- If blank will pick the first interpreter

Optional parameter:
- **database**: select a specific database

For a `SHOW TABLES`, first we send the query statement:

    curl -X POST https://demo.gethue.com/api/v1/editor/execute/hive --data 'statement=SHOW TABLES'

    {"status": 0, "history_id": 17880, "handle": {"statement_id": 0, "session_type": "hive", "has_more_statements": false, "guid": "EUI32vrfTkSOBXET6Eaa+A==\n", "previous_statement_hash": "3070952e55d733fb5bef249277fb8674989e40b6f86c5cc8b39cc415", "log_context": null, "statements_count": 1, "end": {"column": 10, "row": 0}, "session_id": 63, "start": {"column": 0, "row": 0}, "secret": "RuiF0LEkRn+Yok/gjXWSqg==\n", "has_result_set": true, "session_guid": "c845bb7688dca140:859a5024fb284ba2", "statement": "SHOW TABLES", "operation_type": 0, "modified_row_count": null}, "history_uuid": "63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"}

Then check the operation (its value is **history_uuid** from the execute response) status until its result is ready to fetch:

    curl -X POST https://demo.gethue.com/api/v1/editor/check_status --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "query_status": {"status": "available", "has_result_set": true}}

And now ask for the resultset of the statement:

    curl -X POST https://demo.gethue.com/api/v1/editor/fetch_result_data --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "result": {"has_more": true, "type": "table", "meta": [{"comment": "from deserializer", "type": "STRING_TYPE", "name": "tab_name"}], "data": [["adavi"], ["adavi1"], ["adavi2"], ["ambs_feed"], ["apx_adv_deduction_data_process_total"], ["avro_table"], ["avro_table1"], ["bb"], ["bharath_info1"], ["bucknew"], ["bucknew1"], ["chungu"], ["cricket3"], ["cricket4"], ["cricket5_view"], ["cricketer"], ["cricketer_view"], ["cricketer_view1"], ["demo1"], ["demo12345"], ["dummy"], ["embedded"], ["emp"], ["emp1_sept9"], ["emp_details"], ["emp_sept"], ["emp_tbl1"], ["emp_tbl2"], ["empdtls"], ["empdtls_ext"], ["empdtls_ext_v2"], ["employee"], ["employee1"], ["employee_ins"], ["empppp"], ["events"], ["final"], ["flight_data"], ["gopalbhar"], ["guruhive_internaltable"], ["hell"], ["info1"], ["lost_messages"], ["mnewmyak"], ["mortality"], ["mscda"], ["myak"], ["mysample"], ["mysample1"], ["mysample2"], ["network"], ["ods_t_exch_recv_rel_wfz_stat_szy"], ["olympicdata"], ["p_table"], ["partition_cricket"], ["partitioned_user"], ["s"], ["sample"], ["sample_07"], ["sample_08"], ["score"], ["stg_t_exch_recv_rel_wfz_stat_szy"], ["stocks"], ["students"], ["studentscores"], ["studentscores2"], ["t1"], ["table_name"], ["tablex"], ["tabley"], ["temp"], ["test1"], ["test2"], ["test21"], ["test_info"], ["topage"], ["txnrecords"], ["u_data"], ["udata"], ["user_session"], ["user_test"], ["v_empdtls"], ["v_empdtls_ext"], ["v_empdtls_ext_v2"], ["web_logs"]], "isEscaped": true}}

And if we wanted to get the execution log for this statement:

    curl -X POST https://demo.gethue.com/api/v1/editor/get_logs --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

    {"status": 0, "progress": 5, "jobs": [], "logs": "", "isFullLogs": false}

Same but in Python:

    params = {
      'statement': 'SELECT 1, 2, 3',
    }

    response = requests.post(
      'https://demo.gethue.com/api/v1/editor/execute/mysql',
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
      'https://demo.gethue.com/api/v1/editor/check_status',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data=data
    )
    print(response.status_code)
    print(response.text)


    response = requests.post(
      'https://demo.gethue.com/api/v1/editor/fetch_result_data',
      headers={
        'Authorization': 'Bearer %s' % token,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data=data
    )
    print(response.status_code)
    print(response.text)

### Listing Databases

    curl -X POST https://demo.gethue.com/api/v1/editor/autocomplete/ -d 'snippet={"type":"hive"}'

    {"status": 0, "databases": ["default", "information_schema", "sys"]}

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

### Database details

    curl -X POST https://demo.gethue.com/api/v1/editor/autocomplete/<DB>/ -d 'snippet={"type":"hive"}'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

Describe database API:

    curl -X POST https://demo.gethue.com/api/v1/editor/describe/<DB>/ -d 'source_type=mysql'

- **source_type:** select from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

### Table details

    curl -X POST https://demo.gethue.com/api/v1/editor/autocomplete/<DB>/<TABLE>/ -d 'snippet={"type":"hive"}'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

Describe table API:

    curl -X POST https://demo.gethue.com/api/v1/editor/describe/<DB>/<TABLE>/ -d 'source_type=1'

- **source_type:** select from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

Analyze API:

    curl -X POST https://demo.gethue.com/api/v1/<DIALECT>/analyze/<DB>/<TABLE>/

- Currently supported **dialects:** impala, beeswax (hive)

Sample table data API:

    curl -X POST https://demo.gethue.com/api/v1/editor/sample/<DB>/<TABLE>/ -d 'snippet={"type":"hive"}'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

### Column details

    curl -X POST https://demo.gethue.com/api/v1/editor/autocomplete/<DB>/<TABLE>/<COL1>/ -d 'snippet={"type":"hive"}'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

Analyze API:

    curl -X POST https://demo.gethue.com/api/v1/<DIALECT>/analyze/<DB>/<TABLE>/<COL1>/

- Currently supported **dialects:** impala, beeswax (hive)

Sample column data API:

    curl -X POST https://demo.gethue.com/api/v1/editor/sample/<DB>/<TABLE>/<COL1>/ -d 'snippet={"type":"hive"}'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)

### Listing Functions

Default functions:

    curl  -X POST https://demo.gethue.com/api/v1/editor/autocomplete -d 'snippet={"type":"hive"}' -d 'operation=functions'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)
- **operation:** specify the type of operation (e.g., `functions`)

For a specific database:

    curl  -X POST https://demo.gethue.com/api/v1/editor/autocomplete/<DB> -d 'snippet={"type":"impala"}' -d 'operation=functions'

- **snippet:** select the `type` from the configured dialects (e.g. `impala`) or connector IDs (e.g. `1`)
- **operation:** specify the type of operation (e.g., `functions`)

For a specific function/UDF details (e.g. trunc):

    curl  -X POST https://demo.gethue.com/api/v1/editor/autocomplete/<function_name> -d 'snippet={"type":"hive"}' -d 'operation=function'

- **snippet:** select the `type` from the configured dialects (e.g. `hive`) or connector IDs (e.g. `1`)
- **operation:** specify the type of operation (e.g., `function`)

### Query history

We can choose a dialect for `doc_type` e.g. impala, mysql, hive, phoenix, etc.

    curl -X GET https://demo.gethue.com/api/v1/editor/get_history?doc_type=hive

    {"status": 0, "count": 3, "history": [{"name": "", "id": 2008, "uuid": "5b48c678-1224-4863-b523-3baab82402a7", "type": "query-hive", "data": {"statement": "CREATE TABLE w12( Name STRING, Money BIGINT )", "lastExecuted": 1621502970360, "status": "failed", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2008"}, {"name": "", "id": 2006, "uuid": "1cd32ae0-9b61-46ae-8fd4-72c4255209c3", "type": "query-hive", "data": {"statement": "CREATE TABLE q13( Name STRING, Money BIGINT )", "lastExecuted": 1621498889058, "status": "expired", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2006"}, {"name": "", "id": 2003, "uuid": "e5ec1fa4-1a36-4e42-a814-a685b0142223", "type": "query-hive", "data": {"statement": "CREATE TABLE q11( Name STRING, Money BIGINT );\nINSERT INTO q11 VALUES ('abc', 100);", "lastExecuted": 1621498771619, "status": "expired", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2003"}], "message": "History fetched"}

### Get Configuration

    curl -X POST https://demo.gethue.com/api/v1/get_config/

    {"app_config": {"editor": {"name": "editor", "displayName": "Editor", "buttonName": "Query", "interpreters": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, {"name": "notebook", "type": "notebook", "displayName": "Notebook", "buttonName": "Notebook", "tooltip": "Notebook", "page": "/notebook", "is_sql": false, "dialect": "notebook"}], "default_limit": 5000, "interpreter_names": ["mysql", "notebook"], "page": "/editor/?type=mysql", "default_sql_interpreter": "mysql"}, "catalogs": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "page": "/editor/?type=mysql", "is_sql": true, "is_catalog": true}], "browser": {"name": "browser", "displayName": "Browsers", "buttonName": "Browse", "interpreters": [{"type": "hdfs", "displayName": "Files", "buttonName": "Browse", "tooltip": "Files", "page": "/filebrowser/view=%2Fuser%2Fdemo"}, {"type": "tables", "displayName": "Tables", "buttonName": "Browse", "tooltip": "Tables", "page": "/metastore/tables"}, {"type": "yarn", "displayName": "Jobs", "buttonName": "Jobs", "tooltip": "Jobs", "page": "/jobbrowser/"}, {"type": "importer", "displayName": "Importer", "buttonName": "Import", "tooltip": "Importer", "page": "/indexer/importer"}], "interpreter_names": ["hdfs", "tables", "yarn", "importer"]}, "home": {"name": "home", "displayName": "Home", "buttonName": "Documents", "interpreters": [], "page": "/home"}}, "main_button_action": {"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, "button_actions": [{"name": "editor", "displayName": "Editor", "buttonName": "Query", "interpreters": [{"name": "MySQL", "type": "mysql", "id": "mysql", "displayName": "MySQL", "buttonName": "Query", "tooltip": "Mysql Query", "optimizer": "off", "page": "/editor/?type=mysql", "is_sql": true, "is_batchable": true, "dialect": "mysql", "dialect_properties": {}}, {"name": "notebook", "type": "notebook", "displayName": "Notebook", "buttonName": "Notebook", "tooltip": "Notebook", "page": "/notebook", "is_sql": false, "dialect": "notebook"}], "default_limit": 5000, "interpreter_names": ["mysql", "notebook"], "page": "/editor/?type=mysql", "default_sql_interpreter": "mysql"}], "default_sql_interpreter": "mysql", "cluster_type": "direct", "has_computes": false, "hue_config": {"enable_sharing": true, "is_admin": true}, "clusters": [{"id": "default", "name": "default", "type": "direct", "credentials": {}}], "documents": {"types": ["directory", "gist", "query-mysql"]}, "status": 0}

## File Browsing

Hue's [File Browser](https://docs.gethue.com/user/browsing/#data) offer uploads, downloads, operations (create, delete, chmod...) and listing of data in HDFS (`hdfs://` or no prefix), S3 (`s3a://` prefix), ADLS (`adls://` or `abfs://` prefixes), Ozone (`ofs://` prefix) storages.

### Get Filesystems

Get the filesystems details such as configured filesystems in Hue which user has access to and its home directories:

    curl -X GET https://demo.gethue.com/api/v1/storage/filesystems
    
    [{"file_system": "hdfs", "user_home_directory": "/user/demo"}, {"file_system": "s3a", "user_home_directory": "s3a://<some_s3_path>"}, {"file_system": "abfs", "user_home_directory": "abfs://<some_abfs_path>"}, {"file_system": "ofs", "user_home_directory": "ofs://<some_ofs_path>"}]

### List

Here is how to list the content of a path, here a S3 bucket `s3a://demo-gethue`:

    curl -X GET https://demo.gethue.com/api/v1/storage/view=s3a://demo-gethue

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

    curl -X GET https://demo.gethue.com/api/v1/storage/view=s3a://demo-gethue/data/web_logs/index_data.csv

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

    curl -X GET https://demo.gethue.com/api/v1/storage/download=/user/hue/weblogs.csv

    curl -X GET https://demo.gethue.com/api/v1/storage/download=s3a://demo-gethue/data/web_logs/index_data.csv

- **download:** path of the file you want to download

### Upload

Upload a local file to a remote destination directory:

    curl -X POST https://demo.gethue.com/api/v1/storage/upload/file?dest=s3a://demo-gethue/web_log_data/ --form hdfs_file=@README.md

- **dest:** Path of the directory for uploading a file. A new directory is created in the specified path if it does not exist.
- **hdfs_file:** relative or absolute path to a file. It should be read more like a `local_file`, this field is not related to HDFS.

### Create Directory

Create a directory at a specific path:

    curl -X POST https://demo.gethue.com/api/v1/storage/mkdir
    
- **name:** name of the directory you want to create
- **path:** path where you want to create the directory

### Create File

Create a file at a specific path:

    curl -X POST https://demo.gethue.com/api/v1/storage/touch
    
- **name:** name of the file you want to create
- **path:** path where you want to create the file

### Rename

Rename a file or directory:

    curl -X POST https://demo.gethue.com/api/v1/storage/rename
    
- **src_path:** path of the file or directory you want to rename
- **dest_path:** path after renaming the selected file or directory

### Move

Move a file or directory to a destination path:

    curl -X POST https://demo.gethue.com/api/v1/storage/move
    
- **src_path:** path of the file or directory that you want to move
- **dest_path:** path at which you want to move the selected file or directory

### Copy

Copy a file or directory to a destination path:

    curl -X POST https://demo.gethue.com/api/v1/storage/copy
    
- **src_path:** path of the file or directory you want to copy
- **dest_path:** path at which you want to save the copy of the selected file or directory

**Note:** On the **Apache Ozone** filesystem, the copy operation returns a string of skipped files if their size is greater than the configured chunk size.

### Get Content Summary

Fetch the content summary for a specific file on **HDFS** or **Apache Ozone**:

    curl -X GET https://demo.gethue.com/api/v1/storage/content_summary=/user/hue/weblogs.csv

    curl -X GET https://demo.gethue.com/api/v1/storage/content_summary=ofs://ozone1/testvolume/testbucket/testfile.csv

### Delete

Delete a file or directory:

    curl -X POST https://demo.gethue.com/api/v1/storage/rmtree
    
- **path:** path of the file or directory you want to delete
- **skip_trash:** Boolean value to indicate whether to move the deleted file or directory to the trash directory. Specify `False` to move the file to the trash.

**Note:** Currently, the `skip_trash` field is only supported on HDFS.

### Set Replication

Set the replication factor for a file on **HDFS**:

    curl -X POST https://demo.gethue.com/api/v1/storage/set_replication
    
- **src_path:** path of the file for setting the replication factor
- **replication_factor:** numerical value for setting the replication factor for the file

### Restore Trash

Restore a specific file or directory from trash on **HDFS**:

    curl -X POST https://demo.gethue.com/api/v1/storage/trash/restore
    
- **path:** path of the file or directory that you want to restore from the trash directory

### Purge Trash

Purge the trash directory on **HDFS**:

    curl -X POST https://demo.gethue.com/api/v1/storage/trash/purge

## Importer

The File Import API provides endpoints for uploading, analyzing, and previewing files that can be imported into various SQL engines. This API simplifies the process of creating database tables from files like CSV, TSV, and Excel spreadsheets.

### Overview

The File Import API allows you to:

- Upload files from your local system
- Analyze file metadata to determine format and characteristics
- Check whether files have headers
- Preview file content with data types
- Get SQL type mappings for different SQL dialects

### Typical Import Workflow

A typical workflow for importing a file into a database table involves these steps:

1. **Upload the file** using the `/api/v1/importer/upload/file/` endpoint
2. **Detect file metadata** using the `/api/v1/importer/file/guess_metadata/` endpoint
3. **Determine if the file has a header** using the `/api/v1/importer/file/guess_header/` endpoint
4. **Preview the file** with column type detection using the `/api/v1/importer/file/preview/` endpoint
5. Use the preview data to create a table in your SQL engine of choice

### Upload a Local File

Upload a file from your local system to the Hue server.

**Endpoint:** `/api/v1/importer/upload/file/`

**Method:** `POST`

**Content Type:** `multipart/form-data`

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | The file to upload (csv, tsv, excel) |

**Example using cURL:**

```bash
curl -X POST \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -F "file=@/path/to/sales_data.csv" \
  https://demo.gethue.com/api/v1/importer/upload/file/
```

**Response:**

```json
{
  "file_path": "/tmp/username_abc123_sales_data.csv"
}
```

**Status Codes:**

- `201 Created` - File was uploaded successfully
- `400 Bad Request` - Invalid file format or size
- `500 Internal Server Error` - Server-side error

**Restrictions:**
- Maximum file size is determined by the configuration `IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT`
- Certain file extensions may be restricted based on `IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS`

### Guess File Metadata

Analyze a file to determine its type and metadata properties such as delimiters for CSV files or sheet names for Excel files.

**Endpoint:** `/api/v1/importer/file/guess_metadata/`

**Method:** `GET`

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | String | Yes | Full path to the file to analyze |
| import_type | String | Yes | Type of import, either `local` or `remote` |

**Example using cURL:**

```bash
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_metadata/?file_path=/tmp/username_abc123_sales_data.csv&import_type=local"
```

**Response Examples:**

For CSV files:
```json
{
  "type": "csv",
  "field_separator": ",",
  "quote_char": "\"",
  "record_separator": "\n"
}
```

For Excel files:
```json
{
  "type": "excel",
  "sheet_names": ["Sales 2024", "Sales 2025", "Analytics"]
}
```

### Guess File Header

Analyze a file to determine if it has a header row.

**Endpoint:** `/api/v1/importer/file/guess_header/`

**Method:** `GET`

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | String | Yes | Full path to the file to analyze |
| file_type | String | Yes | Type of file (`csv`, `tsv`, `excel`, `delimiter_format`) |
| import_type | String | Yes | Type of import, either `local` or `remote` |
| sheet_name | String | No | Sheet name (required for Excel files) |

**Example using cURL:**

```bash
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_header/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local"
```

**Response:**

```json
{
  "has_header": true
}
```

### Preview File

Generate a preview of a file's content with column type mapping for creating SQL tables.

**Endpoint:** `/api/v1/importer/file/preview/`

**Method:** `GET`

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | String | Yes | Full path to the file to preview |
| file_type | String | Yes | Type of file (`csv`, `tsv`, `excel`, `delimiter_format`) |
| import_type | String | Yes | Type of import (`local` or `remote`) |
| sql_dialect | String | Yes | SQL dialect for type mapping (`hive`, `impala`, `trino`, `phoenix`, `sparksql`) |
| has_header | Boolean | Yes | Whether the file has a header row |
| sheet_name | String | No | Sheet name (required for Excel files) |
| field_separator | String | No | Field separator character (defaults to `,` for CSV, `\t` for TSV, required for `delimiter_format`) |
| quote_char | String | No | Quote character (defaults to `"`) |
| record_separator | String | No | Record separator character (defaults to `\n`) |

**Example using cURL:**

```bash
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local&sql_dialect=hive&has_header=true"

# For a custom pipe-delimited file using delimiter_format
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_pipe_data.txt&file_type=delimiter_format&import_type=local&sql_dialect=hive&has_header=true&field_separator=|&quote_char=\"&record_separator=\n"
```

**About `delimiter_format` File Type:**

The `delimiter_format` file type should be used for custom delimited files that don't follow standard CSV or TSV formats. When using this file type:
- `field_separator` is required and must be explicitly specified
- `quote_char` and `record_separator` should be provided for proper parsing
- Values from the `guess_metadata` response should be passed to ensure consistent parsing

**Parameter Validation Notes:**
- For Excel files, `sheet_name` is required
- For standard formats (CSV/TSV), appropriate defaults are applied
- For `delimiter_format`, always specify the required parameters
- It's recommended to always pass the `record_separator` from the `guess_metadata` response

**Response:**

```json
{
  "type": "csv",
  "columns": [
    {
      "name": "transaction_id",
      "type": "INT"
    },
    {
      "name": "product_name",
      "type": "STRING"
    },
    {
      "name": "price",
      "type": "DOUBLE"
    }
  ],
  "preview_data": [
    ["1001", "Laptop XPS 13", "1299.99"],
    ["1002", "Wireless Headphones", "149.99"],
    ["1003", "Office Chair", "249.50"]
  ]
}
```

### Get SQL Type Mapping

Get the list of unique SQL data types supported by a specific SQL dialect.

**Endpoint:** `/api/v1/importer/sql_type_mapping/`

**Method:** `GET`

**Request Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sql_dialect | String | Yes | SQL dialect for type mapping (`hive`, `impala`, `trino`, `phoenix`, `sparksql`) |

**Example using cURL:**

```bash
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/sql_type_mapping/?sql_dialect=hive"
```

**Response:**

```json
[
  "ARRAY",
  "BIGINT",
  "BINARY",
  "BOOLEAN",
  "DATE",
  "DECIMAL",
  "DOUBLE",
  "FLOAT",
  "INT",
  "INTERVAL DAY TO SECOND",
  "SMALLINT",
  "STRING",
  "STRUCT",
  "TIMESTAMP",
  "TINYINT"
]
```

### Complete Workflow Example

Here's an example workflow that combines all the APIs to import a CSV file into a Hive table:

1. **Upload the file**
2. **Detect file metadata**
3. **Check for header row**
4. **Preview the file with column type detection**
5. **Generate SQL CREATE TABLE statement**

For the full code example and best practices, refer to the [File Import documentation](/developer/api/rest/importer/).

## Connectors

### List

Get the list of configured [connectors](/administrator/configuration/connectors/):

    curl -X GET https://demo.gethue.com/api/v1/connector/instances

    {"connectors": [{"category": "editor", "category_name": "Editor", "description": "", "values": []}, {"category": "browsers", "category_name": "Browsers", "description": "", "values": []}, {"category": "catalogs", "category_name": "Catalogs", "description": "", "values": []}, {"category": "optimizers", "category_name": "Optimizers", "description": "", "values": []}, {"category": "schedulers", "category_name": "Schedulers", "description": "", "values": []}, {"category": "plugins", "category_name": "Plugins", "description": "", "values": []}]}

### Types

    curl -X GET https://demo.gethue.com/api/v1/connector/types

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

    curl -X POST https://demo.gethue.com/api/v1/connector/instance/new/<DIALECT>/<INTERFACE>

And get back a template that we send to the /update call:

    curl -X POST https://demo.gethue.com/api/v1/connector/instance/new/hive/sqlalchemy -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Get

    curl -X GET https://demo.gethue.com/api/v1/connector/instance/get/<ID>

### Update

This is the same as creating a new connector instance, but as we provide the `id` we will update the existing instance:

    curl -X POST https://demo.gethue.com/api/v1/connector/instance/update -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"id":"41","category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Delete

    curl -X POST https://demo.gethue.com/api/v1/connector/instance/delete -d 'connector={"id": "1"}'

### Test

Check if the connectivity is healthy:

    curl -X POST https://demo.gethue.com/api/v1/connector/instance/test/ -d 'connector={"nice_name":"Hive Docker Local","name":"41","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000},{"name":"is_llap","value":false},{"name":"use_sasl","value":"true"}],"id":"41","category":"editor","description":"Recommended","dialect_properties":{"is_sql":true,"sql_identifier_quote":"`","sql_identifier_comment_single":"--","has_catalog":false,"has_database":true,"has_table":true,"has_live_queries":false,"has_optimizer_risks":true,"has_optimizer_values":true,"has_auto_limit":false,"has_reference_language":true,"has_reference_functions":true,"has_use_statement":true}}'

### Examples

Install or update the connector examples:

    curl -X POST https://demo.gethue.com/api/v1/connector/examples/install/

## IAM

### Get users

Get user records in Hue. Requires **admin privileges**.

    curl -X GET https://demo.gethue.com/api/v1/iam/get_users

Optional GET params:
- **username:** filter by username
- **groups:** filter by specific group
- **is_active:** filter by active status

E.g. `?username=demo&groups=default&is_active=true`

Search user records by list of user IDs. Requires **admin privileges**.

    curl -X GET https://demo.gethue.com/api/v1/iam/users?userids=[1100714,1100715]
    
    {"users": [{"id": 1100714,"username": "demo","first_name": "","last_name": "","email": "","last_login": "2021-10-06T01:36:49.663","editURL": "/useradmin/users/edit/demo"},{"id": 1100715,"username": "hue","first_name": "","last_name": "","email": "","last_login": "2021-08-11T07:15:48.793","editURL": "/useradmin/users/edit/hue"}]}

User list_for_autocomplete API:

    curl -X GET https://demo.gethue.com/api/v1/iam/users/autocomplete
 
Optional GET params:
- **extend_user:** true or false (info about each user's groups)
- **filter:** search term
- **count:** Number of records (default is 100)

## Data Catalog

The [metadata API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata) is powering the external [Catalog integrations](/user/browsing/#data-catalogs).

### Searching for entities
    
    curl -X POST https://demo.gethue.com/api/v1/metadata/search/entities_interactive/ -d 'query_s="*sample"&sources=["documents", "sql", "hdfs", "s3"]'

Some of the parameters:
- **query_s:** search term
- **sources:** sources to search from `["documents", "sql", "hdfs", "s3"]`
- **field_facets:** `['type', 'owner', 'tags', 'lastModified']`
- **limit:** 10

Searching for entities with the `dummy` catalog:

    curl -X POST https://demo.gethue.com/api/v1/metadata/search/entities_interactive/ -d 'query_s="*sample"&interface="dummy"'
