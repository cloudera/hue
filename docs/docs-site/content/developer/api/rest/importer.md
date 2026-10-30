---
title: "File Import API"
date: 2025-05-30T00:00:00+00:00
draft: false
weight: 4
---

Use the File Import API to upload, analyze and preview files before you import them into a SQL engine. It supports CSV, TSV, other delimited files and Excel spreadsheets.

All endpoints require [authentication](/developer/api/rest/#authentication). For remote files (`import_type=remote`), the API uses the file system permissions of the authenticated user.

The examples use `hue.example.com` as the server. Replace `<ACCESS_TOKEN>` with the `access` token of your session.

## Overview

The importer is turned off by default. An administrator turns it on with `is_enabled=true` in the `[desktop] [[importer]]` section of `hue.ini`. The `get_config` response reports the setting in `importer.is_enabled`.

The File Import API allows you to:

- Upload files from your local system
- Analyze file metadata to determine format and characteristics
- Check whether files have headers
- Preview file content with data types
- Get SQL type mappings for different SQL dialects

## Typical import workflow

A typical workflow for importing a file into a database table involves these steps:

1. **Upload the file** using the `/api/v1/importer/upload/file/` endpoint
2. **Detect file metadata** using the `/api/v1/importer/file/guess_metadata/` endpoint
3. **Determine if the file has a header** using the `/api/v1/importer/file/guess_header/` endpoint
4. **Preview the file** with column type detection using the `/api/v1/importer/file/preview/` endpoint
5. Use the preview data to create a table in your SQL engine of choice

## Upload a local file

Upload a file from your local system to the Hue server.

**Method and URL:** `POST /api/v1/importer/upload/file/`

**Content type:** `multipart/form-data`

**Request parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | file | Yes | The file to upload (CSV, TSV or Excel). |

The server saves the file in its temporary directory. Use the returned `file_path` with `import_type=local` in the other calls. Only the user who uploaded the file can use that path.

**Example request (curl):**

```bash
curl -X POST \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/path/to/sales_data.csv" \
  https://hue.example.com/api/v1/importer/upload/file/
```

**Example request (JavaScript):**

```javascript
// Using fetch API
const formData = new FormData();
formData.append('file', fileInputElement.files[0]);

fetch('https://hue.example.com/api/v1/importer/upload/file/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

**Example response:**

```json
{
  "file_path": "/tmp/username_abc123_sales_data.csv"
}
```

**Status codes:**

- `201 Created` - File was uploaded successfully
- `400 Bad Request` - Invalid file format or size
- `500 Internal Server Error` - Server-side error

**Restrictions:**

- The maximum file size is set by `max_local_file_size_upload_limit` in the `[desktop] [[importer]]` section of `hue.ini`. The default is 150 MiB.
- An administrator can block file extensions with `restrict_local_file_extensions` in the same section.

## Guess file metadata

Analyze a file to determine its type and metadata properties such as delimiters for CSV files or sheet names for Excel files.

**Method and URL:** `GET /api/v1/importer/file/guess_metadata/`

**Request parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | Full path to the file to analyze |
| import_type | string | Yes | Type of import, either `local` or `remote` |

**Example request (curl):**

```bash
# For a local file uploaded previously
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/guess_metadata/?file_path=/tmp/username_abc123_sales_data.csv&import_type=local"

# For a remote file on HDFS
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/guess_metadata/?file_path=/user/hue/data/sales_data.csv&import_type=remote"
```

**Example request (JavaScript):**

```javascript
// Using fetch API for a local file
fetch('https://hue.example.com/api/v1/importer/file/guess_metadata/?file_path=/tmp/username_abc123_sales_data.csv&import_type=local', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
})
.then(response => response.json())
.then(metadata => console.log(metadata))
.catch(error => console.error('Error:', error));
```

**Example responses:**

For CSV files:
```json
{
  "type": "csv",
  "field_separator": ",",
  "quote_char": "\"",
  "record_separator": "\r\n"
}
```

For TSV files:
```json
{
  "type": "tsv",
  "field_separator": "\t",
  "quote_char": "\"",
  "record_separator": "\r\n"
}
```

For Excel files:
```json
{
  "type": "excel",
  "sheet_names": ["Sales 2024", "Sales 2025", "Analytics"]
}
```

**Status codes:**

- `200 OK` - Metadata detected successfully
- `400 Bad Request` - File not found or invalid parameters
- `500 Internal Server Error` - Server-side error during detection

## Guess file header

Analyze a file to determine if it has a header row. This API uses heuristics to detect if the first row appears to contain column names rather than data.

**Method and URL:** `GET /api/v1/importer/file/guess_header/`

**Request parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | Full path to the file to analyze |
| file_type | string | Yes | Type of file (`csv`, `tsv`, `excel`, `delimiter_format`) |
| import_type | string | Yes | Type of import, either `local` or `remote` |
| sheet_name | string | No | Sheet name (required for Excel files) |

**Example request (curl):**

```bash
# For a CSV file
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/guess_header/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local"

# For an Excel file
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/guess_header/?file_path=/tmp/username_abc123_financial_report.xlsx&file_type=excel&import_type=local&sheet_name=Q1_Results"
```

**Example request (JavaScript):**

```javascript
const params = new URLSearchParams({
  file_path: '/tmp/username_abc123_sales_data.csv',
  file_type: 'csv',
  import_type: 'local'
});

fetch(`https://hue.example.com/api/v1/importer/file/guess_header/?${params.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
})
.then(response => response.json())
.then(result => {
  console.log("Has header:", result.has_header);
  // Use this information to configure preview or import
})
.catch(error => console.error('Error:', error));
```

**Example response:**

```json
{
  "has_header": true
}
```

**How header detection works:**

Hue reads a sample of the file and uses the heuristic of the Python [`csv.Sniffer.has_header`](https://docs.python.org/3/library/csv.html#csv.Sniffer.has_header) method. For Excel files, it first converts the first 20 rows of the sheet to CSV. The result is a guess. Let the user confirm it.

**Status codes:**

- `200 OK` - Header detection successful
- `400 Bad Request` - Invalid parameters or file not found
- `500 Internal Server Error` - Server-side error

## Preview file

Generate a preview of a file's content with column type mapping for creating SQL tables. The preview contains at most 50 rows. `preview_data` maps each column name to its list of values, and it is empty for an empty file.

**Method and URL:** `GET /api/v1/importer/file/preview/`

**Request parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | Full path to the file to preview |
| file_type | string | Yes | Type of file (`csv`, `tsv`, `excel`, `delimiter_format`) |
| import_type | string | Yes | Type of import (`local` or `remote`) |
| sql_dialect | string | Yes | SQL dialect for type mapping (`hive`, `impala`, `trino`, `phoenix`, `sparksql`) |
| has_header | boolean | Yes | Whether the file has a header row |
| sheet_name | string | No | Sheet name (required for Excel files) |
| field_separator | string | No | Field separator character (defaults to `,` for CSV, `\t` for TSV, required for `delimiter_format`) |
| quote_char | string | No | Quote character (defaults to `"`) |
| record_separator | string | No | Record separator character (defaults to `\n`). `\r\n` is treated as `\n`. |

The `field_separator`, `quote_char` and `record_separator` values are read as escape sequences. Send the two characters `\t` for a tab and `\n` for a line feed.

**Example request (curl):**

```bash
# For a CSV file with header
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local&sql_dialect=hive&has_header=true"

# For an Excel file with header
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_financial_report.xlsx&file_type=excel&import_type=local&sql_dialect=impala&has_header=true&sheet_name=Q1_Results"

# For a custom pipe-delimited file using delimiter_format
curl -G "https://hue.example.com/api/v1/importer/file/preview/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  --data-urlencode "file_path=/tmp/username_abc123_pipe_data.txt" \
  --data-urlencode "file_type=delimiter_format" \
  --data-urlencode "import_type=local" \
  --data-urlencode "sql_dialect=hive" \
  --data-urlencode "has_header=true" \
  --data-urlencode "field_separator=|" \
  --data-urlencode 'record_separator=\n'
```

**Example request (JavaScript):**

```javascript
// Parameters for previewing a CSV file
const params = new URLSearchParams({
  file_path: '/tmp/username_abc123_sales_data.csv',
  file_type: 'csv',
  import_type: 'local',
  sql_dialect: 'hive',
  has_header: 'true'
});

// Make the fetch request
fetch(`https://hue.example.com/api/v1/importer/file/preview/?${params.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
})
.then(response => response.json())
.then(previewData => {
  // Use preview data to display to user or generate CREATE TABLE statement
  console.log(previewData);
})
.catch(error => console.error('Error:', error));
```

**Example response:**

For a sales data CSV file:
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
      "name": "category",
      "type": "STRING"
    },
    {
      "name": "price",
      "type": "DOUBLE"
    },
    {
      "name": "quantity",
      "type": "INT"
    },
    {
      "name": "purchase_date",
      "type": "DATE"
    }
  ],
  "preview_data": {
    "transaction_id": [1001, 1002, 1003, 1004],
    "product_name": ["Laptop XPS 13", "Wireless Headphones", "Office Chair", "Notebook Set"],
    "category": ["Electronics", "Electronics", "Furniture", "Office Supplies"],
    "price": [1299.99, 149.99, 249.5, 24.95],
    "quantity": [1, 2, 1, 5],
    "purchase_date": ["2025-01-15", "2025-01-15", "2025-01-16", "2025-01-17"]
  }
}
```

**Using Preview Data to Generate a CREATE TABLE Statement:**

You can use the preview data to generate SQL statements for table creation. Here's an example for Hive:

```sql
CREATE TABLE sales_data (
  transaction_id INT,
  product_name STRING,
  category STRING,
  price DOUBLE,
  quantity INT, 
  purchase_date DATE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;
```

**About `delimiter_format` File Type:**

The `delimiter_format` file type allows you to process custom delimited files that don't follow standard CSV or TSV formats. When using this file type:

- `field_separator` is required and must be explicitly specified
- `quote_char` and `record_separator` should be provided for proper parsing
- Common examples include pipe-delimited files (`|`), semi-colon delimited files (`;`), or files with custom record separators

**Parameter Validation and Best Practices:**

- For Excel files, `sheet_name` is required and the API will return a 400 error if not provided
- For standard delimited files (`csv`, `tsv`), default values will be applied if optional parameters are not specified
- For `delimiter_format` files, you must explicitly provide at least the `field_separator`
- For all file types, it's recommended to pass the values returned by the `guess_metadata` endpoint:
  - Use `field_separator` from guess_metadata response
  - Use `quote_char` from guess_metadata response
  - Use `record_separator` from guess_metadata response
- When `import_type` is set to `remote`, the API uses the file system associated with the user's request

**Status codes:**

- `200 OK` - Preview generated successfully
- `400 Bad Request` - Invalid parameters or file not found
- `500 Internal Server Error` - Server-side error

## Get SQL type mapping

Get the list of unique SQL data types supported by a specific SQL dialect. This helps in understanding what SQL types are available when creating tables in different SQL engines.

**Method and URL:** `GET /api/v1/importer/sql_type_mapping/`

**Request parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sql_dialect | string | Yes | SQL dialect for type mapping (`hive`, `impala`, `trino`, `phoenix`, `sparksql`) |

**Example request (curl):**

```bash
curl -X GET \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://hue.example.com/api/v1/importer/sql_type_mapping/?sql_dialect=hive"
```

**Example request (JavaScript):**

```javascript
fetch('https://hue.example.com/api/v1/importer/sql_type_mapping/?sql_dialect=hive', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
})
.then(response => response.json())
.then(sqlTypes => {
  console.log(sqlTypes);
  // Use SQL types list for validation or UI display
})
.catch(error => console.error('Error:', error));
```

**Example response:**

The response is a sorted list of unique SQL data types supported by the specified dialect.

For Hive:
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

**Dialect-Specific SQL Types**

Different SQL dialects support different sets of SQL types. Here are the unique types for each dialect:

**Trino:**
```json
[
  "ARRAY",
  "BIGINT",
  "BOOLEAN",
  "DATE",
  "DECIMAL",
  "DOUBLE",
  "INTEGER",
  "INTERVAL DAY TO SECOND",
  "JSON",
  "REAL",
  "ROW",
  "SMALLINT",
  "STRING",
  "TIMESTAMP",
  "TINYINT",
  "VARBINARY",
  "VARCHAR"
]
```

**Impala:**
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
  "SMALLINT",
  "STRING",
  "STRUCT",
  "TIMESTAMP",
  "TINYINT"
]
```

**Phoenix:**
```json
[
  "ARRAY",
  "BIGINT",
  "BOOLEAN",
  "DATE",
  "DECIMAL",
  "DOUBLE",
  "FLOAT",
  "INT",
  "SMALLINT",
  "STRING",
  "TIME",
  "TIMESTAMP",
  "TINYINT",
  "UNSIGNED_INT",
  "UNSIGNED_LONG",
  "UNSIGNED_SMALLINT",
  "UNSIGNED_TINYINT",
  "VARBINARY",
  "VARCHAR"
]
```

**Spark SQL:**
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

**Key differences between dialects:**

- **Impala**: Does not support `INTERVAL` types (uses `STRING` for duration data)
- **Trino**: Uses `INTEGER` instead of `INT`, `REAL` instead of `FLOAT`, `VARCHAR` instead of `STRING`, `ROW` instead of `STRUCT`, and supports `JSON` type
- **Phoenix**: Supports unsigned integer types (`UNSIGNED_INT`, `UNSIGNED_LONG`, etc.) and has a dedicated `TIME` type
- **Spark SQL**: Uses the same types as Hive.

**Status codes:**

- `200 OK` - Mapping retrieved successfully
- `400 Bad Request` - Invalid SQL dialect
- `500 Internal Server Error` - Server-side error

## Error handling

The API returns these status codes:

- `400 Bad Request`: a parameter is missing or invalid, or the file does not exist.
- `401 Unauthorized`: the credentials are missing or invalid.
- `500 Internal Server Error`: the server failed to process the file.

Parameter validation errors list the invalid fields:

```json
{
  "sql_dialect": ["\"oracle\" is not a valid choice."]
}
```

Other errors return a message:

```json
{
  "error": "Remote file does not exist: /user/hue/data/missing.csv"
}
```

If an uploaded file is larger than the limit, the upload fails with `400 Bad Request`. The default limit is 150 MiB. An administrator can change it with `max_local_file_size_upload_limit` in the `[desktop] [[importer]]` section of `hue.ini`.

If a `guess_metadata` or `preview` call with `import_type=local` fails, Hue deletes the uploaded temporary file. Upload the file again before you retry.

## Complete workflow example

Here's an example workflow that combines all the APIs to import a CSV file into a Hive table:

### 1: Upload the file

```javascript
// Upload the CSV file
const formData = new FormData();
formData.append('file', fileInputElement.files[0]);

const uploadResponse = await fetch('https://hue.example.com/api/v1/importer/upload/file/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  },
  body: formData
});

const uploadResult = await uploadResponse.json();
const filePath = uploadResult.file_path;
```

### 2: Detect file metadata

```javascript
// Get file metadata
const metadataParams = new URLSearchParams({
  file_path: filePath,
  import_type: 'local'
});

const metadataResponse = await fetch(`https://hue.example.com/api/v1/importer/file/guess_metadata/?${metadataParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
});

const metadata = await metadataResponse.json();
const fileType = metadata.type;
const fieldSeparator = metadata.field_separator;
const quoteChar = metadata.quote_char;
const recordSeparator = metadata.record_separator;
```

### 3: Check for header row

```javascript
// Detect if file has a header
const headerParams = new URLSearchParams({
  file_path: filePath,
  file_type: fileType,
  import_type: 'local'
});

const headerResponse = await fetch(`https://hue.example.com/api/v1/importer/file/guess_header/?${headerParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
});

const headerResult = await headerResponse.json();
const hasHeader = headerResult.has_header;
```

### 4: Preview the file with column type detection

```javascript
// Generate file preview with SQL types
const previewParams = new URLSearchParams({
  file_path: filePath,
  file_type: fileType,
  import_type: 'local',
  sql_dialect: 'hive',
  has_header: hasHeader,
  field_separator: fieldSeparator,
  quote_char: quoteChar,
  record_separator: recordSeparator
});

const previewResponse = await fetch(`https://hue.example.com/api/v1/importer/file/preview/?${previewParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <ACCESS_TOKEN>'
  }
});

const preview = await previewResponse.json();
```

### 5: Generate SQL CREATE TABLE statement

```javascript
// Generate SQL CREATE TABLE statement
const tableName = 'imported_sales_data';
const columns = preview.columns.map(col => `  ${col.name} ${col.type}`).join(',\n');

const createTableSQL = `CREATE TABLE ${tableName} (\n${columns}\n)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '${fieldSeparator}'
STORED AS TEXTFILE;`;

console.log(createTableSQL);

// You can then execute this SQL using the SQL execution API
```

## Best practices

1. Handle errors for every call. Uploads can fail on size or file type limits.
2. Call the endpoints in the order of the workflow. Each step needs the output of the previous one.
3. Let users review and change the detected header, separators and column types before you create a table.
4. Delete the temporary files you no longer need. Hue stores uploaded files in the server temporary directory.
