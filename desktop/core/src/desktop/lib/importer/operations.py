#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import csv
import uuid
import codecs
import logging
import tempfile
from io import BytesIO
from typing import Any, BinaryIO, Dict, Optional, Union

import polars as pl

from desktop.lib.conf import coerce_bool

LOG = logging.getLogger()

try:
  # Import this at the module level to avoid checking availability in each _detect_file_type method call
  import magic

  is_magic_lib_available = True
except ImportError as e:
  LOG.exception(f'Failed to import python-magic: {str(e)}')
  is_magic_lib_available = False


def local_file_upload(upload_file, username: str) -> Dict[str, str]:
  """Uploads a local file to a temporary directory with a unique filename.

  This function takes an uploaded file and username, generates a unique filename,
  and saves the file to a temporary directory. The filename is created using
  the username, a unique ID, and a sanitized version of the original filename.

  Args:
    upload_file: The uploaded file object from Django's file upload handling.
    username: The username of the user uploading the file.

  Returns:
    Dict[str, str]: A dictionary containing:
      - file_path: The full path where the file was saved

  Raises:
    ValueError: If upload_file or username is None/empty
    Exception: If there are issues with file operations

  Example:
    >>> result = upload_local_file(request.FILES['file'], 'hue_user')
    >>> print(result)
    {'file_path': '/tmp/hue_user_a1b2c3d4_myfile.txt'}
  """
  if not upload_file:
    raise ValueError("Upload file cannot be None or empty")

  if not username:
    raise ValueError("Username cannot be None or empty")

  # Generate a unique filename
  unique_id = uuid.uuid4().hex[:8]
  filename = f"{username}_{unique_id}_{upload_file.name}"

  # Create a temporary file with our generated filename
  temp_dir = tempfile.gettempdir()
  destination_path = os.path.join(temp_dir, filename)

  try:
    # Simply write the file content to temporary location
    with open(destination_path, 'wb') as destination:
      for chunk in upload_file.chunks():
        destination.write(chunk)

    return {'file_path': destination_path}

  except Exception as e:
    # Clean up the file if there was an error
    if os.path.exists(destination_path):
      os.remove(destination_path)
    raise e


def guess_file_metadata(file_path: str, import_type: str, fs=None) -> Dict[str, Any]:
  """
  Guess the metadata of a file based on its content or extension.

  Args:
    file_path: Path to the file to analyze
    import_type: Type of import ('local' or 'remote')
    fs: File system object for remote files (default: None)

  Returns:
    Dict containing the file metadata:
      - type: File type (e.g., excel, csv, tsv)
      - sheet_names: List of sheet names (for Excel files)
      - field_separator: Field separator character (for delimited files)
      - quote_char: Quote character (for delimited files)
      - record_separator: Record separator (for delimited files)

  Raises:
    ValueError: If the file does not exist or parameters are invalid
    Exception: For various file processing errors
  """
  if not file_path:
    raise ValueError("File path cannot be empty")

  if import_type not in ['local', 'remote']:
    raise ValueError(f"Unsupported import type: {import_type}")

  if import_type == 'remote' and fs is None:
    raise ValueError("File system object (fs) is required for remote import type")

  # Check if file exists based on import type
  if import_type == 'local' and not os.path.isfile(file_path):
    raise ValueError(f'Local file does not exist: {file_path}')
  elif import_type == 'remote' and fs and not fs.exists(file_path):
    raise ValueError(f'Remote file does not exist: {file_path}')

  fh = open(file_path, 'rb') if import_type == 'local' else fs.open(file_path, 'rb')

  try:
    sample = fh.read(16 * 1024)  # Read 16 KiB sample

    if not sample:
      raise ValueError("File is empty, cannot detect file format.")

    file_type = _detect_file_type(sample)

    if file_type == 'unknown':
      raise ValueError('Unable to detect file format.')

    if file_type == 'excel':
      metadata = _get_excel_metadata(fh)
    else:
      # CSV, TSV, or other delimited formats
      metadata = _get_delimited_metadata(sample, file_type)

    return metadata

  except Exception as e:
    LOG.error(f"Error guessing file metadata: {str(e)}", exc_info=True)
    raise Exception(f"Failed to guess file metadata.")

  finally:
    # Ensure file handle is closed
    fh.close()


def preview_file(
  file_path: str,
  file_type: str,
  import_type: str,
  sql_dialect: str,
  has_header: Optional[bool] = None,
  sheet_name: Optional[str] = None,
  field_separator: Optional[str] = ',',
  quote_char: Optional[str] = '"',
  record_separator: Optional[str] = '\n',
  fs=None,
  preview_rows: int = 50,
) -> Dict[str, Any]:
  """
  Generate a preview of a file's content with column type mapping.

  This method reads a file and returns a preview of its contents, along with
  column information and metadata for creating tables or further processing.

  Args:
    file_path: Path to the file to preview
    file_type: Type of file ('excel', 'csv', 'tsv', 'delimiter_format')
    import_type: Type of import ('local' or 'remote')
    sql_dialect: SQL dialect for type mapping ('hive', 'impala', etc.)
    has_header: Whether the file has a header row (optional, auto-detected if None)
    sheet_name: Sheet name for Excel files (required for Excel)
    field_separator: Field separator character for delimited files
    quote_char: Quote character for delimited files
    record_separator: Record separator for delimited files
    fs: File system object for remote files (default: None)
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: File type
      - has_header: Whether the file has a header row
      - columns: List of column metadata (name, type)
      - preview_data: Preview of the file data

  Raises:
    ValueError: If the file does not exist or parameters are invalid
    Exception: For various file processing errors
  """
  if not file_path:
    raise ValueError("File path cannot be empty")

  if sql_dialect.lower() not in ['hive', 'impala', 'trino', 'phoenix', 'sparksql']:
    raise ValueError(f"Unsupported SQL dialect: {sql_dialect}")

  if file_type not in ['excel', 'csv', 'tsv', 'delimiter_format']:
    raise ValueError(f"Unsupported file type: {file_type}")

  if import_type not in ['local', 'remote']:
    raise ValueError(f"Unsupported import type: {import_type}")

  if import_type == 'remote' and fs is None:
    raise ValueError("File system object (fs) is required for remote import type")

  # Check if file exists based on import type
  if import_type == 'local' and not os.path.isfile(file_path):
    raise ValueError(f'Local file does not exist: {file_path}')
  elif import_type == 'remote' and fs and not fs.exists(file_path):
    raise ValueError(f'Remote file does not exist: {file_path}')

  fh = open(file_path, 'rb') if import_type == 'local' else fs.open(file_path, 'rb')

  try:
    if file_type == 'excel':
      if not sheet_name:
        raise ValueError("Sheet name is required for Excel files.")

      result = _preview_excel_file(fh, file_type, sheet_name, sql_dialect, has_header, preview_rows)
    elif file_type in ['csv', 'tsv', 'delimiter_format']:
      # Process escapable characters
      try:
        if field_separator:
          field_separator = codecs.decode(field_separator, 'unicode_escape')
        if quote_char:
          quote_char = codecs.decode(quote_char, 'unicode_escape')
        if record_separator:
          record_separator = codecs.decode(record_separator, 'unicode_escape')

      except Exception as e:
        LOG.error(f"Error decoding escape characters: {e}")
        raise ValueError("Invalid escape characters in field_separator, quote_char, or record_separator.")

      result = _preview_delimited_file(fh, file_type, field_separator, quote_char, record_separator, sql_dialect, has_header, preview_rows)
    else:
      raise ValueError(f'Unsupported file type: {file_type}')

    return result

  finally:
    # Ensure file handle is closed
    fh.close()


def _detect_file_type(file_sample: bytes) -> str:
  """
  Detect the file type based on its content.

  Args:
    file_sample: Binary sample of the file content

  Returns:
    String indicating the detected file type ('excel', 'delimiter_format', or 'unknown')

  Raises:
    RuntimeError: If python-magic or libmagic is not available
    Exception: If an error occurs during file type detection
  """
  # Check if magic library is available
  if not is_magic_lib_available:
    error = "Unable to guess file type. python-magic or its dependency libmagic is not installed."
    LOG.error(error)
    raise RuntimeError(error)

  try:
    # Use libmagic to detect MIME type from content
    file_type = magic.from_buffer(file_sample, mime=True)

    # Map MIME type to the simplified type categories
    if any(keyword in file_type for keyword in ['excel', 'spreadsheet', 'officedocument.sheet']):
      return 'excel'
    elif any(keyword in file_type for keyword in ['text', 'csv', 'plain']):
      # For text files, we'll analyze the content later to determine specific format
      return 'delimiter_format'

    LOG.info(f"Detected MIME type: {file_type}, but not recognized as supported format")
    return 'unknown'
  except Exception as e:
    LOG.error(f"Error in file type detection: {e}")
    raise Exception(f"Failed to detect file type.")


def _get_excel_metadata(fh: BinaryIO) -> Dict[str, Any]:
  """
  Extract metadata for Excel files (.xlsx, .xls).

  Args:
    fh: File handle for the Excel file

  Returns:
    Dict containing Excel metadata:
      - type: 'excel'
      - sheet_names: List of sheet names

  Raises:
    Exception: If there's an error processing the Excel file
  """
  try:
    # Reset file position to beginning
    fh.seek(0)

    # Read Excel file and get sheet names
    excel_data = pl.read_excel(BytesIO(fh.read()), sheet_id=0)
    sheet_names = excel_data.keys()

    return {
      'type': 'excel',
      'sheet_names': list(sheet_names),
    }
  except Exception as e:
    LOG.error(f"Error detecting Excel file format: {e}", exc_info=True)
    raise Exception(f"Failed to detect Excel file format: {e}")


def _get_delimited_metadata(file_sample: Union[bytes, str], file_type: str) -> Dict[str, Any]:
  """
  Extract metadata for delimited files (CSV, TSV, etc.).

  Args:
    file_sample: Binary or string sample of the file content
    file_type: Initial file type detection ('delimiter_format')

  Returns:
    Dict containing delimited file metadata:
      - type: Specific file type ('csv', 'tsv', etc.)
      - field_separator: Field separator character
      - quote_char: Quote character
      - record_separator: Record separator character

  Raises:
    Exception: If there's an error processing the delimited file
  """
  try:
    if isinstance(file_sample, bytes):
      file_sample = file_sample.decode('utf-8', errors='replace')

    # Use CSV Sniffer to detect delimiter and other formatting
    try:
      dialect = csv.Sniffer().sniff(file_sample)
    except Exception as sniff_error:
      LOG.warning(f"CSV sniffer failed: {sniff_error}. Using default values.")
      # Fall back to default CSV format if sniffing fails
      return {
        'type': 'csv',
        'field_separator': ',',
        'quote_char': '"',
        'record_separator': '\n',
      }

    # Refine file type based on detected delimiter
    if file_type == 'delimiter_format':
      if dialect.delimiter == ',':
        file_type = 'csv'
      elif dialect.delimiter == '\t':
        file_type = 'tsv'
      # Other delimiters remain as 'delimiter_format'

    return {
      'type': file_type,
      'field_separator': dialect.delimiter,
      'quote_char': dialect.quotechar,
      'record_separator': dialect.lineterminator,
    }
  except Exception as e:
    message = f"Error detecting delimited file format: {e}"
    LOG.error(message, exc_info=True)
    # Provide sensible defaults instead of failing completely
    return {
      'type': 'csv',
      'field_separator': ',',
      'quote_char': '"',
      'record_separator': '\n',
    }


def _preview_excel_file(
  fh: BinaryIO, file_type: str, sheet_name: str, dialect: str, has_header: Optional[bool], preview_rows: int = 50
) -> Dict[str, Any]:
  """Preview an Excel file (.xlsx, .xls)

  Args:
    fh: File handle for the Excel file
    file_type: Type of file ('excel')
    sheet_name: Name of the sheet to preview
    dialect: SQL dialect for type mapping
    has_header: Whether the file has a header row (None means auto-detect)
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: 'excel'
      - has_header: Whether file has headers
      - columns: List of column metadata
      - preview_data: Preview of file data

  Raises:
    Exception: If there's an error processing the Excel file
  """
  try:
    # Auto-detect header if not specified
    if has_header is None:
      fh.seek(0)
      try:
        # Convert excel sample to CSV for header detection
        csv_snippet = pl.read_excel(source=BytesIO(fh.read()), sheet_name=sheet_name).head(20).write_csv(file=None)

        if isinstance(csv_snippet, bytes):
          csv_snippet = csv_snippet.decode('utf-8', errors='replace')

        has_header = csv.Sniffer().has_header(csv_snippet)
        LOG.info(f"Auto-detected header for Excel file: {has_header}")
      except Exception as e:
        LOG.warning(f"Error auto-detecting header in Excel file: {e}")
        # Default to True if detection fails (most Excel files have headers)
        has_header = True
    else:
      has_header = coerce_bool(has_header)

    # Reset file position and read Excel data
    fh.seek(0)
    df = pl.read_excel(BytesIO(fh.read()), sheet_name=sheet_name, has_header=has_header)

    # Return empty result if the df is empty
    if df.height == 0:
      return {'type': file_type, 'has_header': has_header, 'columns': [], 'preview_data': {}}

    schema = df.schema

    # Limit preview to specified number of rows for performance
    preview_data = df.head(preview_rows).to_dict(as_series=False)

    # Create column metadata with SQL type mapping
    columns = []
    for i, col in enumerate(df.columns):
      col_type = str(schema[col])
      sql_type = _map_polars_dtype_to_sql_type(dialect, col_type)

      columns.append(
        {
          'name': col,
          'type': sql_type,
          'index': i,  # Add index for ordering
        }
      )

    result = {'type': file_type, 'has_header': has_header, 'columns': columns, 'preview_data': preview_data}

    return result

  except Exception as e:
    message = f"Error previewing Excel file: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)


def _preview_delimited_file(
  fh: BinaryIO,
  file_type: str,
  field_separator: str,
  quote_char: str,
  record_separator: str,
  dialect: str,
  has_header: Optional[bool],
  preview_rows: int = 50,
) -> Dict[str, Any]:
  """Preview a delimited file (CSV, TSV, etc.)

  Args:
    fh: File handle for the delimited file
    file_type: Type of file ('csv', 'tsv', 'delimiter_format')
    field_separator: Field separator character
    quote_char: Quote character
    record_separator: Record separator character
    dialect: SQL dialect for type mapping
    has_header: Whether the file has a header row (None means auto-detect)
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: File type
      - has_header: Whether file has headers
      - columns: List of column metadata
      - preview_data: Preview of file data

  Raises:
    Exception: If there's an error processing the delimited file
  """
  try:
    # Auto-detect header if not specified
    if has_header is None:
      fh.seek(0)
      try:
        # Read 16 KiB sample
        sample = fh.read(16 * 1024).decode('utf-8', errors='replace')

        has_header = csv.Sniffer().has_header(sample)
        LOG.info(f"Auto-detected header for delimited file: {has_header}")
      except Exception as e:
        LOG.warning(f"Error auto-detecting header in delimited file: {e}")
        # Default based on file type - most CSVs have headers
        has_header = True if file_type in ['csv', 'tsv'] else False
    else:
      has_header = coerce_bool(has_header)

    # Reset file position and read file content
    fh.seek(0)

    df = pl.read_csv(
      BytesIO(fh.read()),
      separator=field_separator,
      quote_char=quote_char,
      eol_char='\n' if record_separator == '\r\n' else record_separator,
      has_header=has_header,
      ignore_errors=True,
    )

    # Return empty result if the df is empty
    if df.height == 0:
      return {'type': file_type, 'has_header': has_header, 'columns': [], 'preview_data': {}}

    # Get schema and preview data
    schema = df.schema

    # Limit preview to specified number of rows for performance
    preview_data = df.head(preview_rows).to_dict(as_series=False)

    # Create detailed column metadata with SQL type mapping
    columns = []
    for i, col in enumerate(df.columns):
      col_type = str(schema[col])
      sql_type = _map_polars_dtype_to_sql_type(dialect, col_type)

      columns.append(
        {
          'name': col,
          'type': sql_type,
          'index': i,  # Add index for ordering
        }
      )

    result = {'type': file_type, 'has_header': has_header, 'columns': columns, 'preview_data': preview_data}

    return result

  except Exception as e:
    message = f"Error previewing delimited file: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)


def _map_polars_dtype_to_sql_type(dialect: str, polars_type: str) -> str:
  """
  Map a Polars dtype to the corresponding SQL type for a given dialect.

  Supports all Polars dtypes as listed in the Polars docs:
  Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64,
  Float32, Float64, Decimal, Boolean, Utf8/String, Categorical, Enum,
  Binary, Date, Time, Datetime, Duration, Array, List, Struct,
  Object, Null, Unknown.

  Args:
    dialect: One of "hive", "impala", "trino", "phoenix", "sparksql".
    polars_type: Polars dtype name as string.

  Returns:
    A string representing the SQL type.

  Raises:
    ValueError: If the dialect or polars_type is not supported.
  """
  # Base mapping for most engines (Hive, Impala, SparkSQL)
  base_map = {
    # signed ints
    "Int8": "TINYINT",
    "Int16": "SMALLINT",
    "Int32": "INT",
    "Int64": "BIGINT",
    # unsigned ints: same size signed by default (Hive/Impala/SparkSQL)
    "UInt8": "TINYINT",
    "UInt16": "SMALLINT",
    "UInt32": "INT",
    "UInt64": "BIGINT",
    # floats & decimal
    "Float32": "FLOAT",
    "Float64": "DOUBLE",
    "Decimal": "DECIMAL",  # Hive/Impala/SparkSQL use DECIMAL(precision,scale)
    # boolean, string, binary
    "Boolean": "BOOLEAN",
    "Utf8": "STRING",  # STRING covers Hive/VARCHAR/CHAR for default
    "String": "STRING",
    "Categorical": "STRING",
    "Enum": "STRING",
    "Binary": "BINARY",
    # temporal
    "Date": "DATE",
    "Time": "TIMESTAMP",  # Hive/Impala/SparkSQL have no pure TIME type
    "Datetime": "TIMESTAMP",
    "Duration": "INTERVAL DAY TO SECOND",
    # nested & other
    "Array": "ARRAY",
    "List": "ARRAY",
    "Struct": "STRUCT",
    "Object": "STRING",
    "Null": "STRING",  # no SQL NULL type—use STRING or handle as special case
    "Unknown": "STRING",
  }

  # Per‑dialect overrides for the few differences
  overrides = {
    "hive": {},
    "impala": {},
    "sparksql": {},
    "trino": {
      "Int32": "INTEGER",
      "UInt32": "INTEGER",
      "Utf8": "VARCHAR",
      "String": "VARCHAR",
      "Binary": "VARBINARY",
      "Float32": "REAL",
      "Struct": "ROW",
      "Object": "JSON",
      "Duration": "INTERVAL DAY TO SECOND",  # explicit SQL syntax
    },
    "phoenix": {
      **{f"UInt{b}": f"UNSIGNED_{t}" for b, t in [(8, "TINYINT"), (16, "SMALLINT"), (32, "INT"), (64, "LONG")]},
      "Utf8": "VARCHAR",
      "String": "VARCHAR",
      "Binary": "VARBINARY",
      "Duration": "STRING",  # Phoenix treats durations as strings
      "Struct": "STRING",  # no native STRUCT type
      "Object": "VARCHAR",
      "Time": "TIME",  # Phoenix has its own TIME type
      "Decimal": "DECIMAL",  # up to precision 38
    },
  }

  dl = dialect.lower()
  if dl not in overrides:
    raise ValueError(f"Unsupported dialect: {dialect}")

  # Merge base_map and overrides[dl] into a new dict, giving precedence to any overlapping keys in overrides[dl]
  mapping = {**base_map, **overrides[dl]}

  if polars_type not in mapping:
    raise ValueError(f"No mapping for Polars dtype {polars_type} in dialect {dialect}")

  return mapping[polars_type]
