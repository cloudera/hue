---
title: "REST"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

Use the REST API to run SQL queries, manage files in the configured storages, import files, search for tables and manage connectors.

The examples use these placeholders:

```bash
export HUE_URL=https://hue.example.com
export TOKEN=<your access token>
```

## Quickstart

1. [Authenticate](#authentication) and get an access token.
2. Send the token in the `Authorization` header of every request.

```bash
curl -X POST "$HUE_URL/api/v1/token/auth/" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo"}'

curl -X POST "$HUE_URL/api/v1/editor/execute/hive" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'statement=SHOW TABLES'
```

Read the full [query example](#execute-a-query) below.

### Python

Install the [requests](https://pypi.org/project/requests/) library:

```bash
pip install requests
```

Then authenticate and run a statement:

```python
import time

import requests

HUE_URL = "https://hue.example.com"

response = requests.post(
    f"{HUE_URL}/api/v1/token/auth/",
    json={"username": "demo", "password": "demo"},
)
response.raise_for_status()
headers = {"Authorization": f"Bearer {response.json()['access']}"}

response = requests.post(
    f"{HUE_URL}/api/v1/editor/execute/hive",
    headers=headers,
    data={"statement": "SELECT 1, 2, 3"},
)
operation_id = response.json()["history_uuid"]

while True:
    response = requests.post(
        f"{HUE_URL}/api/v1/editor/check_status",
        headers=headers,
        data={"operationId": operation_id},
    )
    if response.json()["query_status"]["status"] not in ("waiting", "running"):
        break
    time.sleep(1)

response = requests.post(
    f"{HUE_URL}/api/v1/editor/fetch_result_data",
    headers=headers,
    data={"operationId": operation_id},
)
print(response.json()["result"]["data"])
```

### JavaScript

This example uses [Axios](https://axios-http.com/):

```javascript
const axios = require('axios');

const client = axios.create({ baseURL: 'https://hue.example.com' });

async function main() {
  const auth = await client.post('/api/v1/token/auth/', { username: 'demo', password: 'demo' });
  client.defaults.headers.common['Authorization'] = `Bearer ${auth.data.access}`;

  const types = await client.get('/api/v1/connector/types');
  console.log(types.data);
}

main();
```

## Conventions

- All paths start with `/api/v1/`. A trailing slash is optional, except for `connector/instance/new/<DIALECT>/<INTERFACE>` and `connector/instance/get/<ID>`, which must not end with one.
- Requests are form data (`application/x-www-form-urlencoded`) unless the endpoint says otherwise. The token endpoints also accept JSON. `storage/rename` requires a JSON body.
- The editor, connector and catalog endpoints return `200 OK` with a body containing `"status": 0` on success. On failure, `status` is not 0 (`-1` is the generic error, other values include `-2` for an expired session and `1` for a query error) and `message` holds the reason.
- The storage endpoints return plain HTTP status codes. On failure, the body is an error message or `{"error": "<reason>"}`.
- A request without valid credentials returns `401 Unauthorized`:

```json
{"detail": "Authentication credentials were not provided."}
```

- The server publishes its OpenAPI schema at `/api/schema` and an interactive Swagger page at `/api/swagger`.

## Authentication

The API accepts these authentication methods, in order of priority. The administrator can change the list with `api_auth` in the `[desktop] [[auth]]` section of `hue.ini`.

1. **JWT access token** in the `Authorization: Bearer <token>` header.
2. **Session cookie** from a browser login.

The token endpoints check your credentials against the same [authentication backends](/administrator/configuration/server/#authentication) as the login page.

### Get a token

Send your credentials to get an access token and a refresh token.

**Method and URL:** `POST /api/v1/token/auth/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | Yes | Your Hue username. |
| password | string | Yes | Your Hue password. |

```bash
curl -X POST "$HUE_URL/api/v1/token/auth/" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo"}'
```

```json
{"refresh": "<refresh token>", "access": "<access token>"}
```

An access token is valid for one day. A refresh token is valid for seven days.

**Errors:** `401 Unauthorized` when the credentials are wrong.

### Use a token

Send the `access` value as a bearer token:

```bash
curl -X POST "$HUE_URL/api/v1/query/create_notebook" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"status": 0, "notebook": {"name": "My Notebook", "uuid": "1e23314f-b01e-4c18-872f-dc143475f063", "type": "notebook", "sessions": [], "snippets": []}}
```

An invalid or expired token returns `401 Unauthorized`:

```json
{"detail": "Given token not valid for any token type", "code": "token_not_valid", "messages": [{"token_class": "AccessToken", "token_type": "access", "message": "Token is invalid or expired"}]}
```

### Verify a token

**Method and URL:** `POST /api/v1/token/verify/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| token | string | Yes | The token to check. |

```bash
curl -X POST "$HUE_URL/api/v1/token/verify/" -d "token=$TOKEN"
```

A valid token returns `200 OK` and `{}`. An invalid or expired token returns `401 Unauthorized`.

### Refresh a token

**Method and URL:** `POST /api/v1/token/refresh/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| refresh | string | Yes | The `refresh` token from the authentication response. |

```bash
curl -X POST "$HUE_URL/api/v1/token/refresh/" -d "refresh=<refresh token>"
```

```json
{"access": "<new access token>"}
```

**Errors:** `401 Unauthorized` when the refresh token is invalid or expired.

### Session cookie

If you call the API from a browser session, Hue also accepts the session cookie. For `POST` requests, send the value of the `csrftoken` cookie in the `X-CSRFToken` header. Without it, the request fails with `403 Forbidden`. Bearer token requests do not need the CSRF header.

### Custom JWT

You can authenticate with a JWT issued by your own identity provider. Hue verifies RS256 signatures. Add this to `hue.ini`:

```ini
[desktop]
[[auth]]
[[[jwt]]]
key_server_url=https://ext_authz:8000
issuer=<your_external_app>
audience=hue
username_header=sub
```

To forward the JWT to services such as Impala, also set:

```ini
[desktop]
use_thrift_http_jwt=true
```

You can also write your own [Django REST Framework authentication class](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication). Then list it in `hue.ini`, separated by commas if you use several:

```ini
[desktop]
[[auth]]
api_auth=<your_own_custom_auth_backend>
```

## SQL querying

### Execute a query

Submit a statement to a dialect.

**Method and URL:** `POST /api/v1/editor/execute/<dialect>`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| dialect | path | No | The configured dialect, for example `hive`. Use `<dialect>-<id>`, for example `hive-1`, to pick an interpreter by id. If you omit it, Hue uses the first interpreter. |
| statement | string | Yes | The SQL statement. Do not use double quotes or line breaks in it. |
| database | string | No | The database to run the statement in. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/execute/hive" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'statement=SHOW TABLES'
```

```json
{"status": 0, "history_id": 17880, "history_uuid": "63ce87ba-ca0f-4653-8aeb-e9f5c1781b78", "handle": {"statement_id": 0, "session_type": "hive", "has_more_statements": false, "statements_count": 1, "has_result_set": true, "statement": "SHOW TABLES", "operation_type": 0, "modified_row_count": null}}
```

Keep the `history_uuid` value. It is the `operationId` for the next calls.

**Errors:** `200 OK` with a non-zero `status` and a `message`, for example `{"status": -1, "message": "<reason>"}`.

### Check the status

Poll until the result is ready.

**Method and URL:** `POST /api/v1/editor/check_status`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| operationId | string | Yes | The `history_uuid` returned by the execute call. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/check_status" \
  -H "Authorization: Bearer $TOKEN" \
  -d "operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"
```

```json
{"status": 0, "query_status": {"status": "available", "has_result_set": true}}
```

The query is ready when `query_status.status` is `available`. While it runs, the value is `waiting` or `running`.

### Fetch the results

**Method and URL:** `POST /api/v1/editor/fetch_result_data`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| operationId | string | Yes | The `history_uuid` returned by the execute call. |
| rows | integer | No | Number of rows to fetch. The default is 100. |
| startOver | boolean | No | Set to `true` to read from the first row again. The default is `false`. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/fetch_result_data" \
  -H "Authorization: Bearer $TOKEN" \
  -d "operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78" -d "rows=100"
```

```json
{"status": 0, "result": {"has_more": true, "type": "table", "meta": [{"comment": "from deserializer", "type": "STRING_TYPE", "name": "tab_name"}], "data": [["web_logs"], ["sample_07"]], "isEscaped": true}}
```

Call it again to get the next rows while `has_more` is `true`.

The related calls `POST /api/v1/editor/fetch_result_metadata` and `POST /api/v1/editor/fetch_result_size` take the same `operationId` parameter.

### Get the logs

**Method and URL:** `POST /api/v1/editor/get_logs`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| operationId | string | Yes | The `history_uuid` returned by the execute call. |
| from | integer | No | Line to start reading from. |
| size | integer | No | Number of lines to read. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/get_logs" \
  -H "Authorization: Bearer $TOKEN" \
  -d "operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"
```

```json
{"status": 0, "progress": 5, "jobs": [], "logs": "", "isFullLogs": false}
```

### Cancel or close a statement

Use `POST /api/v1/editor/cancel_statement` to stop a running statement. Use `POST /api/v1/editor/close_statement` to release its resources after you fetched the results. Both take the `operationId` parameter.

```bash
curl -X POST "$HUE_URL/api/v1/editor/cancel_statement" \
  -H "Authorization: Bearer $TOKEN" \
  -d "operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78"
```

### Get the query history

**Method and URL:** `GET /api/v1/editor/get_history`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| doc_type | string | Yes | The dialect, for example `hive`, `impala` or `mysql`. |
| doc_text | string | No | Filter on the name, description or statement. |
| doc_connector | string | No | Filter on a connector id. |
| page | integer | No | Page number. The default is 1. |
| limit | integer | No | Page size. The default is 50 and the maximum is 100. |

```bash
curl "$HUE_URL/api/v1/editor/get_history?doc_type=hive&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"status": 0, "count": 1, "history": [{"name": "", "id": 2008, "uuid": "5b48c678-1224-4863-b523-3baab82402a7", "type": "query-hive", "data": {"statement": "CREATE TABLE w12( Name STRING, Money BIGINT )", "lastExecuted": 1621502970360, "status": "failed", "parentSavedQueryUuid": ""}, "absoluteUrl": "/editor?editor=2008"}], "message": "History fetched"}
```

### Browse databases, tables and columns

The autocomplete endpoint lists the objects of a dialect. All calls are `POST` requests with the same parameters.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| snippet | JSON string | No | Selects the dialect, for example `{"type":"hive"}`. You can use a connector id instead, for example `{"type":"1"}`. When omitted, it defaults to the connector with id `1`. |
| operation | string | No | `schema` (default), `functions` or `function`. |

| Purpose | URL |
|---------|-----|
| List databases | `/api/v1/editor/autocomplete/` |
| List tables of a database | `/api/v1/editor/autocomplete/<DB>/` |
| List columns of a table | `/api/v1/editor/autocomplete/<DB>/<TABLE>/` |
| Describe a column | `/api/v1/editor/autocomplete/<DB>/<TABLE>/<COLUMN>/` |

```bash
curl -X POST "$HUE_URL/api/v1/editor/autocomplete/" \
  -H "Authorization: Bearer $TOKEN" \
  -d 'snippet={"type":"hive"}'
```

```json
{"status": 0, "databases": ["default", "information_schema", "sys"]}
```

To list functions, add `operation=functions`. Add a database to the path for the functions of that database. To get the details of one function, use its name in the path and `operation=function`.

```bash
curl -X POST "$HUE_URL/api/v1/editor/autocomplete/" \
  -H "Authorization: Bearer $TOKEN" \
  -d 'snippet={"type":"hive"}' -d 'operation=functions'
```

### Describe a database, table or column

**Method and URL:**

- `POST /api/v1/editor/describe/<DB>/`
- `POST /api/v1/editor/describe/<DB>/<TABLE>/`
- `POST /api/v1/editor/describe/<DB>/<TABLE>/stats/<COLUMN>/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| source_type | string | No | The dialect, for example `hive`, or a connector id. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/describe/default/web_logs/" \
  -H "Authorization: Bearer $TOKEN" \
  -d 'source_type=hive'
```

### Get sample data

**Method and URL:**

- `POST /api/v1/editor/sample/<DB>/<TABLE>/`
- `POST /api/v1/editor/sample/<DB>/<TABLE>/<COLUMN>/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| snippet | JSON string | No | Selects the dialect, for example `{"type":"hive"}`. When omitted, it defaults to the connector with id `1`. |

```bash
curl -X POST "$HUE_URL/api/v1/editor/sample/default/web_logs/" \
  -H "Authorization: Bearer $TOKEN" \
  -d 'snippet={"type":"hive"}'
```

### Analyze a table

Compute the statistics of a table.

**Method and URL:**

- `POST /api/v1/<DIALECT>/analyze/<DB>/<TABLE>/`

The statistics are always computed for the whole table, even if you add a column to the URL.

The supported dialects are `impala` and `beeswax` (Hive). Other dialects return `204 No Content`.

```bash
curl -X POST "$HUE_URL/api/v1/impala/analyze/default/web_logs/" \
  -H "Authorization: Bearer $TOKEN"
```

### Get the configuration

Get the interpreters, browsers and settings available to the current user.

**Method and URL:** `POST /api/v1/get_config/`

```bash
curl -X POST "$HUE_URL/api/v1/get_config/" \
  -H "Authorization: Bearer $TOKEN"
```

The response is a JSON object with the keys `app_config`, `main_button_action`, `button_actions`, `default_sql_interpreter`, `cluster_type`, `clusters`, `hue_config`, `storage_browser` and `documents`, among others. The exact content depends on the server configuration.

## File browsing

The [File Browser](/user/browsing/#data) lists, reads and changes files in HDFS (`hdfs://` or no prefix), S3 (`s3a://`), ADLS (`abfs://`), Google Cloud Storage (`gs://`) and Ozone (`ofs://`). Only the storages enabled on the server and allowed for your user are available.

Paths are passed in the `path` parameter, not in the URL.

### Get the filesystems

Get the filesystems you can use and your home directory on each.

**Method and URL:** `GET /api/v1/storage/filesystems`

```bash
curl "$HUE_URL/api/v1/storage/filesystems" -H "Authorization: Bearer $TOKEN"
```

```json
[{"name": "hdfs", "user_home_directory": "/user/demo", "config": {"is_trash_enabled": true, "is_hdfs_superuser": false, "groups": [], "users": [], "superuser": "hdfs", "supergroup": "supergroup"}}, {"name": "s3a", "user_home_directory": "s3a://demo-gethue/user/demo", "config": {}}]
```

### List a directory

**Method and URL:** `GET /api/v1/storage/list`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | No | The directory to list. The default is `/`. |
| pagenum | integer | No | Page number. The default is 1. |
| pagesize | integer | No | Page size. The default is 30. |
| sortby | string | No | `type`, `name` (default), `atime`, `mtime`, `user`, `group` or `size`. |
| descending | boolean | No | Sort in descending order. The default is `false`. |
| filter | string | No | Keep only the names that contain this text. |

```bash
curl "$HUE_URL/api/v1/storage/list?path=s3a://demo-gethue/&pagesize=45&pagenum=1" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "files": [
    {
      "path": "s3a://demo-gethue/data",
      "type": "dir",
      "rwx": "drwxrwxrwx",
      "size": 0,
      "user": "",
      "group": "",
      "mtime": null,
      "atime": null,
      "mode": 16895,
      "aclBit": false
    }
  ],
  "page": {"page_number": 1, "page_size": 45, "total_pages": 1, "total_size": 1}
}
```

**Errors:** `400` when the path is not a directory, `404` when the page does not exist, `403` when listing all buckets is not allowed.

### Get the stats of a path

**Method and URL:** `GET /api/v1/storage/stat`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file or directory. |

```bash
curl "$HUE_URL/api/v1/storage/stat?path=/user/demo/weblogs.csv" -H "Authorization: Bearer $TOKEN"
```

The response has the same fields as an entry of the directory listing. It returns `404` when the path does not exist.

### Preview a file

Read a part of a text file.

**Method and URL:** `GET /api/v1/storage/display`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file to read. |
| offset | integer | No | First byte to read. The default is 0. |
| length | integer | No | Number of bytes to read. The default is the server chunk size. A value above the maximum chunk size returns `400`. |
| begin, end | integer | No | Alternative to `offset` and `length`. First byte (starting at 1) and last byte. |
| compression | string | No | The compression of the file. |
| mode | string | No | Only `text` is accepted. |
| encoding | string | No | Character encoding. The default is the server encoding. |

```bash
curl "$HUE_URL/api/v1/storage/display?path=s3a://demo-gethue/data/web_logs/index_data.csv&offset=0&length=204800" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"contents": "code,protocol,request\n200,HTTP/1.1,GET /metastore/table/default/sample_07 HTTP/1.1\n", "offset": 0, "length": 204800, "end": 76, "mode": "text"}
```

**Errors:** `400` when the path is not a file or the range is invalid, `422` when the content cannot be decoded as text.

### Download a file

**Method and URL:** `GET /api/v1/storage/download`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file to download. |
| disposition | string | No | Set to `inline` to display the file instead of downloading it, when the file type allows it. |

```bash
curl -o weblogs.csv "$HUE_URL/api/v1/storage/download?path=/user/demo/weblogs.csv" \
  -H "Authorization: Bearer $TOKEN"
```

**Errors:** `400` when the path is not a file, `403` when you cannot read it or downloads are disabled, `404` when it does not exist.

### Upload a file

**Method and URL:** `POST /api/v1/storage/upload/file`

Send the file as `multipart/form-data`.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| destination_path | query string | Yes | The destination of the file. |
| overwrite | query boolean | No | Replace an existing file. The default is `false`. |
| file | form file | Yes | The file to upload. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/upload/file?destination_path=s3a://demo-gethue/web_log_data/&overwrite=false" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@README.md"
```

A successful upload returns `201 Created` and a `file_stats` object that describes the new file. Errors return `{"error": "<reason>"}` with status `400`, `401`, `404` or `500`.

### Create a directory

**Method and URL:** `POST /api/v1/storage/create/directory`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The parent directory. |
| name | string | Yes | The name of the new directory. It cannot contain `/` or `#`. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/create/directory" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo" -d "name=reports"
```

It returns `201 Created`. It returns `409` when the directory exists and `400` when a parameter is missing or invalid.

### Create a file

**Method and URL:** `POST /api/v1/storage/create/file`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The parent directory. |
| name | string | Yes | The name of the new file. It cannot contain `/`. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/create/file" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo" -d "name=notes.txt"
```

It returns `201 Created`. It returns `409` when the file exists and `400` when a parameter is missing or invalid.

### Save a file

Write the content of a file. It creates the file when the path does not exist.

**Method and URL:** `POST /api/v1/storage/save`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file to write. |
| contents | string | Yes | The new content. |
| encoding | string | Yes | The character encoding, for example `utf-8`. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/save" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/notes.txt" -d "encoding=utf-8" --data-urlencode "contents=Hello"
```

It returns `200 OK`.

### Rename

**Method and URL:** `POST /api/v1/storage/rename`

Send a JSON body.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| source_path | string | Yes | The file or directory to rename. |
| destination_path | string | Yes | The new path. It can be relative to the parent of the source. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/rename" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"source_path": "/user/demo/a.csv", "destination_path": "/user/demo/b.csv"}'
```

It returns `200 OK`, or `400` with the validation errors.

### Move and copy

**Method and URL:**

- `POST /api/v1/storage/move`
- `POST /api/v1/storage/copy`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| source_path | string | Yes | The file or directory. |
| destination_path | string | Yes | The destination directory. It must already exist. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/copy" \
  -H "Authorization: Bearer $TOKEN" \
  -d "source_path=/user/demo/a.csv" -d "destination_path=/user/demo/archive"
```

It returns `200 OK`. It returns `409` when a file with the same name already exists in the destination directory and `400` when a parameter is missing or invalid, or when the destination is not a directory. On Ozone, a copy can return `500` with `{"skipped_files": ...}` for files larger than the configured chunk size.

### Delete

**Method and URL:** `POST /api/v1/storage/delete`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file or directory. |
| skip_trash | boolean | No | Delete permanently instead of moving to the trash. The default is `false`. Only HDFS supports the trash. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/delete" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/a.csv" -d "skip_trash=false"
```

It returns `200 OK`.

### Change the owner or permissions

**Method and URL:**

- `POST /api/v1/storage/chown`
- `POST /api/v1/storage/chmod`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file or directory. |
| user | string | `chown` | The new owner. |
| group | string | `chown` | The new group. |
| recursive | boolean | No | `chown` only. Apply to the content of a directory. |
| permission | JSON string | `chmod` | The permission flags. |

The `permission` object has the boolean keys `user_read`, `user_write`, `user_execute`, `group_read`, `group_write`, `group_execute`, `other_read`, `other_write`, `other_execute`, `sticky` and `recursive`.

```bash
curl -X POST "$HUE_URL/api/v1/storage/chmod" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/a.csv" \
  -d 'permission={"user_read":true,"user_write":true,"group_read":true,"other_read":true}'
```

It returns `200 OK`.

### Get a content summary

Get the size and the number of files of a path on HDFS or Ozone.

**Method and URL:** `GET /api/v1/storage/content_summary`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file or directory. |

```bash
curl "$HUE_URL/api/v1/storage/content_summary?path=/user/demo/weblogs.csv" \
  -H "Authorization: Bearer $TOKEN"
```

It returns `400` when the path is missing, `404` when it does not exist and `500` when the summary fails.

### Set the replication factor

Set the replication factor of a file on HDFS.

**Method and URL:** `POST /api/v1/storage/replication`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | The file. |
| replication_factor | integer | Yes | The new replication factor. |

```bash
curl -X POST "$HUE_URL/api/v1/storage/replication" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/weblogs.csv" -d "replication_factor=2"
```

### Trash

The trash is only available on HDFS.

| Purpose | Method and URL | Parameters |
|---------|----------------|------------|
| Get the trash path of a path | `GET /api/v1/storage/trash/path` | `path` |
| Restore a path from the trash | `POST /api/v1/storage/trash/restore` | `path` |
| Empty your trash | `POST /api/v1/storage/trash/purge` | None |

```bash
curl -X POST "$HUE_URL/api/v1/storage/trash/restore" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/.Trash/Current/user/demo/a.csv"
```

### Bulk operations

These endpoints apply an operation to several paths. Repeat the `path` parameter (or `source_path` for move and copy) once for each item.

| Operation | Method and URL |
|-----------|----------------|
| Move | `POST /api/v1/storage/move/bulk` |
| Copy | `POST /api/v1/storage/copy/bulk` |
| Delete | `POST /api/v1/storage/delete/bulk` |
| Restore from the trash | `POST /api/v1/storage/trash/restore/bulk` |
| Change the owner | `POST /api/v1/storage/chown/bulk` |
| Change the permissions | `POST /api/v1/storage/chmod/bulk` |

```bash
curl -X POST "$HUE_URL/api/v1/storage/delete/bulk" \
  -H "Authorization: Bearer $TOKEN" \
  -d "path=/user/demo/a.csv" -d "path=/user/demo/b.csv"
```

It returns `200 OK` when all operations succeed. Otherwise, it returns `500` with an object that maps each failed path to its error.

## Importer

Use the Importer endpoints to upload a file, detect its format and preview it. These endpoints are under development and do not create the table yet. Read the [File Import API](/developer/api/rest/importer/) for the parameters, responses and a full workflow.

| Purpose | Method and URL |
|---------|----------------|
| Upload a local file | `POST /api/v1/importer/upload/file/` |
| Detect the file format | `GET /api/v1/importer/file/guess_metadata/` |
| Detect a header row | `GET /api/v1/importer/file/guess_header/` |
| Preview a file | `GET /api/v1/importer/file/preview/` |
| List the SQL types of a dialect | `GET /api/v1/importer/sql_type_mapping/` |

## Connectors

[Connectors](/administrator/configuration/connectors/) describe the interpreters, browsers and catalogs of the server. Creating, updating, deleting and testing a connector requires admin privileges.

### List the instances

**Method and URL:** `GET /api/v1/connector/instances`

```bash
curl "$HUE_URL/api/v1/connector/instances" -H "Authorization: Bearer $TOKEN"
```

```json
{"connectors": [{"category": "editor", "category_name": "Editor", "description": "", "values": []}, {"category": "browsers", "category_name": "Browsers", "description": "", "values": []}]}
```

The categories are `editor`, `browsers`, `catalogs`, `optimizers`, `schedulers` and `plugins`.

### List the types

**Method and URL:** `GET /api/v1/connector/types`

```bash
curl "$HUE_URL/api/v1/connector/types" -H "Authorization: Bearer $TOKEN"
```

The response has a `connectors` list grouped by category, and a `categories` list. Each connector type has a `dialect`, an `interface`, a `nice_name` and its default `settings`.

### Get a template for a new instance

Pick a `dialect` and `interface` from the list of types.

**Method and URL:** `POST /api/v1/connector/instance/new/<DIALECT>/<INTERFACE>`

```bash
curl -X POST "$HUE_URL/api/v1/connector/instance/new/hive/hiveserver2" \
  -H "Authorization: Bearer $TOKEN"
```

The response is `{"connector": {...}}`. Edit it and send it to the update call.

### Get an instance

**Method and URL:** `GET /api/v1/connector/instance/get/<ID>`

```bash
curl "$HUE_URL/api/v1/connector/instance/get/41" -H "Authorization: Bearer $TOKEN"
```

```json
{"id": 41, "name": "Hive Docker Local", "description": "Recommended", "dialect": "hive", "settings": [{"name": "server_host", "value": "localhost"}]}
```

### Create or update an instance

**Method and URL:** `POST /api/v1/connector/instance/update`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| connector | JSON string | Yes | The connector. Without an `id`, Hue creates a new instance. With an `id`, it updates that instance. It needs `nice_name`, `description` and `settings`. A new instance also needs `dialect` and `interface`. |

```bash
curl -X POST "$HUE_URL/api/v1/connector/instance/update" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'connector={"nice_name":"Hive Docker Local","description":"Recommended","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"},{"name":"server_port","value":10000}]}'
```

```json
{"connector": {"id": 41, "name": 41, "nice_name": "Hive Docker Local"}, "saved_as": true}
```

### Delete an instance

**Method and URL:** `POST /api/v1/connector/instance/delete`

```bash
curl -X POST "$HUE_URL/api/v1/connector/instance/delete" \
  -H "Authorization: Bearer $TOKEN" \
  -d 'connector={"id": "41"}'
```

### Test an instance

Check that the connection works.

**Method and URL:** `POST /api/v1/connector/instance/test`

The `connector` parameter is the same JSON object as for the update call.

```bash
curl -X POST "$HUE_URL/api/v1/connector/instance/test" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'connector={"nice_name":"Hive Docker Local","dialect":"hive","interface":"hiveserver2","settings":[{"name":"server_host","value":"localhost"}]}'
```

```json
{"warnings": "", "hasWarnings": false}
```

### Install the examples

Install or update the connector examples.

**Method and URL:** `POST /api/v1/connector/examples/install`

```bash
curl -X POST "$HUE_URL/api/v1/connector/examples/install" -H "Authorization: Bearer $TOKEN"
```

```json
{"status": 0, "message": "Added connectors: ..."}
```

## Users

### List the users

Requires admin privileges.

**Method and URL:** `GET /api/v1/iam/get_users`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | No | Filter on a username. |
| groups | string | No | Filter on a group. Repeat it to match several groups. |
| is_active | boolean | No | Set to `true` to keep only the active users. |

```bash
curl "$HUE_URL/api/v1/iam/get_users?username=demo&is_active=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Get users by id

Requires admin privileges, or sharing enabled on the server.

**Method and URL:** `GET /api/v1/iam/users`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| userids | JSON list | Yes | Up to 100 user ids. |

```bash
curl -G "$HUE_URL/api/v1/iam/users" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'userids=[1100714,1100715]'
```

```json
{"users": [{"id": 1100714, "username": "demo", "first_name": "", "last_name": "", "email": "", "last_login": "2021-10-06T01:36:49.663", "editURL": "/useradmin/users/edit/demo"}]}
```

### Search users and groups

**Method and URL:** `GET /api/v1/iam/users/autocomplete`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| filter | string | No | Search text. |
| count | integer | No | Maximum number of results. The default is 100. |
| extend_user | boolean | No | Set to `true` to include the groups of each user. |
| include_myself | boolean | No | Include your own user in the results. |
| only_mygroups | boolean | No | Admins only. Return only your groups. |

```bash
curl "$HUE_URL/api/v1/iam/users/autocomplete?filter=de&count=10" \
  -H "Authorization: Bearer $TOKEN"
```

Non-admin users only see the users of their groups, and only when sharing is enabled.

## Data catalog

Search for documents, tables and files.

**Method and URL:** `POST /api/v1/metadata/search/entities_interactive/`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| query_s | JSON string | Yes | The search text, for example `"*sample"` (with the quotes). |
| sources | JSON list | Yes | Where to search, for example `["documents", "sql"]`. |
| limit | integer | No | Maximum number of results. The default is 25. |
| field_facets | JSON list | No | The facets to return, for example `["type", "owner"]`. |
| interface | string | No | The catalog to use. The default is the configured catalog. |

```bash
curl -X POST "$HUE_URL/api/v1/metadata/search/entities_interactive/" \
  -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'query_s="*sample"' \
  --data-urlencode 'sources=["documents"]'
```

```json
{"status": 0, "count": 1, "results": [{"hue_name": "sample", "hue_description": "", "link": "/editor?editor=2008", "doc_type": "query-hive", "last_modified": "2021-05-20T08:09:30.360", "owner": "demo", "type": "HUE", "uuid": "5b48c678-1224-4863-b523-3baab82402a7", "parentUuid": "d1a5a0a9-0f2b-4d3f-a8a1-4ac1d7b0a7d1", "originalName": "sample"}]}
```

When `sources` contains `documents`, Hue searches its own documents. Otherwise, it queries the configured catalog and returns `{"status": 1, "message": "Navigator not enabled"}` if there is none.
