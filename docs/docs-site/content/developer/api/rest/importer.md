---
title: "File Import API"
date: 2025-05-30T00:00:00+00:00
draft: false
weight: 4
---

The File Import API provides endpoints for uploading, analyzing, and previewing files that can be imported into various SQL engines. This API simplifies the process of creating database tables from files like CSV, TSV, and Excel spreadsheets.

> **Note**: All API endpoints require authentication. For endpoints that work with remote files (`import_type=remote`), the API uses the file system permissions associated with the authenticated user's session.

## Overview

The File Import API allows you to:

- Upload files from your local system
- Analyze file metadata to determine format and characteristics
- Check whether files have headers
- Preview file content with data types
- Get SQL type mappings for different SQL dialects

## Typical Import Workflow

A typical workflow for importing a file into a database table involves these steps:

1. **Upload the file** using the `/api/v1/importer/upload/file/` endpoint
2. **Detect file metadata** using the `/api/v1/importer/file/guess_metadata/` endpoint
3. **Determine if the file has a header** using the `/api/v1/importer/file/guess_header/` endpoint
4. **Preview the file** with column type detection using the `/api/v1/importer/file/preview/` endpoint
5. Use the preview data to create a table in your SQL engine of choice

## Upload a Local File

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

**Example using JavaScript:**

```javascript
// Using fetch API
const formData = new FormData();
formData.append('file', fileInputElement.files[0]);

fetch('https://demo.gethue.com/api/v1/importer/upload/file/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
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

## Guess File Metadata

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
# For a local file uploaded previously
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_metadata/?file_path=/tmp/username_abc123_sales_data.csv&import_type=local"

# For a remote file on HDFS
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_metadata/?file_path=/user/hue/data/sales_data.csv&import_type=remote"
```

**Example using JavaScript:**

```javascript
// Using fetch API for a local file
fetch('https://demo.gethue.com/api/v1/importer/file/guess_metadata/?file_path=/tmp/username_abc123_sales_data.csv&import_type=local', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
  }
})
.then(response => response.json())
.then(metadata => console.log(metadata))
.catch(error => console.error('Error:', error));
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

For TSV files:
```json
{
  "type": "tsv",
  "field_separator": "\t",
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

**Status Codes:**

- `200 OK` - Metadata detected successfully
- `400 Bad Request` - File not found or invalid parameters
- `500 Internal Server Error` - Server-side error during detection

## Guess File Header

Analyze a file to determine if it has a header row. This API uses heuristics to detect if the first row appears to contain column names rather than data.

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
# For a CSV file
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_header/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local"

# For an Excel file
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/guess_header/?file_path=/tmp/username_abc123_financial_report.xlsx&file_type=excel&import_type=local&sheet_name=Q1_Results"
```

**Example using JavaScript:**

```javascript
const params = new URLSearchParams({
  file_path: '/tmp/username_abc123_sales_data.csv',
  file_type: 'csv',
  import_type: 'local'
});

fetch(`https://demo.gethue.com/api/v1/importer/file/guess_header/?${params.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
  }
})
.then(response => response.json())
.then(result => {
  console.log("Has header:", result.has_header);
  // Use this information to configure preview or import
})
.catch(error => console.error('Error:', error));
```

**Response:**

```json
{
  "has_header": true
}
```

**How Header Detection Works:**

The header detection algorithm uses multiple factors to make an educated guess:

1. Checks if the first row contains text while subsequent rows contain numeric values
2. Examines if the first row's data types differ from the majority of other rows
3. Looks for common header naming patterns (e.g., id, name, date, etc.)
4. Checks if the first row has no duplicate values while data rows might have duplicates

**Status Codes:**

- `200 OK` - Header detection successful
- `400 Bad Request` - Invalid parameters or file not found
- `500 Internal Server Error` - Server-side error

## Preview File

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
# For a CSV file with header
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_sales_data.csv&file_type=csv&import_type=local&sql_dialect=hive&has_header=true"

# For an Excel file with header
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_financial_report.xlsx&file_type=excel&import_type=local&sql_dialect=impala&has_header=true&sheet_name=Q1_Results"

# For a custom pipe-delimited file using delimiter_format
curl -X GET \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  "https://demo.gethue.com/api/v1/importer/file/preview/?file_path=/tmp/username_abc123_pipe_data.txt&file_type=delimiter_format&import_type=local&sql_dialect=hive&has_header=true&field_separator=|&quote_char=\"&record_separator=\n"
```

**Example using JavaScript:**

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
fetch(`https://demo.gethue.com/api/v1/importer/file/preview/?${params.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
  }
})
.then(response => response.json())
.then(previewData => {
  // Use preview data to display to user or generate CREATE TABLE statement
  console.log(previewData);
})
.catch(error => console.error('Error:', error));
```

**Response:**

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
  "preview_data": [
    ["1001", "Laptop XPS 13", "Electronics", "1299.99", "1", "2025-01-15"],
    ["1002", "Wireless Headphones", "Electronics", "149.99", "2", "2025-01-15"],
    ["1003", "Office Chair", "Furniture", "249.50", "1", "2025-01-16"],
    ["1004", "Notebook Set", "Office Supplies", "24.95", "5", "2025-01-17"]
  ]
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

**Status Codes:**

- `200 OK` - Preview generated successfully
- `400 Bad Request` - Invalid parameters or file not found
- `500 Internal Server Error` - Server-side error

## Get SQL Type Mapping

Get the list of unique SQL data types supported by a specific SQL dialect. This helps in understanding what SQL types are available when creating tables in different SQL engines.

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

**Example using JavaScript:**

```javascript
fetch('https://demo.gethue.com/api/v1/importer/sql_type_mapping/?sql_dialect=hive', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
  }
})
.then(response => response.json())
.then(sqlTypes => {
  console.log(sqlTypes);
  // Use SQL types list for validation or UI display
})
.catch(error => console.error('Error:', error));
```

**Response:**

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

**Key Differences Between Dialects:**

- **Impala**: Does not support `INTERVAL` types (uses `STRING` for duration data)
- **Trino**: Uses `INTEGER` instead of `INT`, `REAL` instead of `FLOAT`, `VARCHAR` instead of `STRING`, `ROW` instead of `STRUCT`, and supports `JSON` type
- **Phoenix**: Supports unsigned integer types (`UNSIGNED_INT`, `UNSIGNED_LONG`, etc.) and has a dedicated `TIME` type
- **Spark SQL**: Similar to Hive but follows more standard SQL conventions

**Status Codes:**

- `200 OK` - Mapping retrieved successfully
- `400 Bad Request` - Invalid SQL dialect
- `500 Internal Server Error` - Server-side error

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Example Error Responses:**

File not found:
```json
{
  "error": "File /tmp/nonexistent_file.csv not found"
}
```

Invalid parameter:
```json
{
  "error": "Sheet name is required for Excel files"
}
```

File size limit exceeded:
```json
{
  "error": "File too large. Maximum file size is 100 MiB."
}
```

Authentication errors will return a standard HTTP 401 Unauthorized response.

> **Note**: Authentication tokens can be obtained through Hue's authentication API. See the [Authentication API](/developer/api/rest/#authentication) documentation for details.

## Complete Workflow Example

Here's an example workflow that combines all the APIs to import a CSV file into a Hive table:

### 1: Upload the file

```javascript
// Upload the CSV file
const formData = new FormData();
formData.append('file', fileInputElement.files[0]);

const uploadResponse = await fetch('https://demo.gethue.com/api/v1/importer/upload/file/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
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

const metadataResponse = await fetch(`https://demo.gethue.com/api/v1/importer/file/guess_metadata/?${metadataParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
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

const headerResponse = await fetch(`https://demo.gethue.com/api/v1/importer/file/guess_header/?${headerParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
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

const previewResponse = await fetch(`https://demo.gethue.com/api/v1/importer/file/preview/?${previewParams.toString()}`, {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <YOUR_JWT_TOKEN>'
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

## Best Practices

1. **Error Handling**: Always implement proper error handling for API responses, especially for file uploads which may fail due to size limitations or network issues.

2. **Progress Feedback**: For large file uploads, consider implementing progress indicators using XHR instead of fetch to track upload progress.

3. **Type Checking**: When parsing and validating file data, always check that the inferred types match what you expect for your business data.

4. **Sequential Processing**: Process API calls in the proper sequence as shown in the workflow example to ensure each step has the required data.

5. **User Confirmation**: Allow users to review and modify the automatic type detection before creating tables, especially for large datasets.

6. **Access Control**: Ensure file permissions are properly set for any uploaded files, especially in multi-user environments.

7. **Cleanup**: Consider implementing cleanup mechanisms for temporary uploaded files that are no longer needed. Files uploaded via the `/api/v1/importer/upload/file/` endpoint are stored in temporary locations (typically `/tmp/`) and should be cleaned up after processing.
