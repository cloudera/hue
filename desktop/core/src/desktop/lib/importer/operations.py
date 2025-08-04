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
import csv
import logging
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from typing import Any, BinaryIO, Dict, List, Union

import polars as pl

from desktop.lib.importer.schemas import (
  GuessFileHeaderSchema,
  GuessFileMetadataSchema,
  LocalFileUploadSchema,
  PreviewFileSchema,
  SqlTypeMapperSchema,
)
from filebrowser.utils import get_user_fs

LOG = logging.getLogger()

try:
  # Import this at the module level to avoid checking availability in each _detect_file_type method call
  import magic

  is_magic_lib_available = True
except ImportError as e:
  LOG.warning(f"Failed to import python-magic: {e}")
  is_magic_lib_available = False


# Base mapping for most SQL engines (Hive, Impala, SparkSQL)
SQL_TYPE_BASE_MAP = {
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
SQL_TYPE_DIALECT_OVERRIDES = {
  "hive": {},
  "impala": {
    "Duration": "STRING",  # Impala doesn't support INTERVAL types
  },
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


def local_file_upload(data: LocalFileUploadSchema, username: str) -> Dict[str, str]:
  """Uploads a local file to a temporary directory with a unique filename.

  This function takes an uploaded file and username, generates a unique filename,
  and saves the file to a temporary directory. The filename is created using
  the username, a unique ID, and a sanitized version of the original filename.

  Args:
    data: A Pydantic schema containing the file to upload.
    username: The username of the user uploading the file.

  Returns:
    Dict[str, str]: A dictionary containing:
      - file_path: The full path where the file was saved

  Raises:
    ValueError: If username is None/empty
    Exception: If there are issues with file operations

  Example:
    >>> result = upload_local_file(data, "hue_user")
    >>> print(result)
    {'file_path': '/tmp/hue_user_a1b2c3d4_myfile.txt'}
  """
  if not username:
    raise ValueError("Username cannot be None or empty.")

  upload_file = data.file
  sanitized_filename = os.path.basename(data.filename)

  destination_file = tempfile.NamedTemporaryFile(
    mode="wb",
    delete=False,
    prefix=f"{username}_",
    suffix=f"_{sanitized_filename}",
    dir=tempfile.gettempdir(),
  )
  destination_path = destination_file.name

  try:
    with destination_file:
      shutil.copyfileobj(upload_file, destination_file)

    return {"file_path": destination_path}

  except Exception as e:
    if os.path.exists(destination_path):
      LOG.debug(f"Error during local file upload, cleaning up temporary file: {destination_path}")
      os.remove(destination_path)
    raise e


def guess_file_metadata(data: GuessFileMetadataSchema, username: str) -> Dict[str, Any]:
  """Guess the metadata of a file based on its content or extension.

  Args:
    data: A Pydantic schema containing file_path and import_type.
    username: The name of the user to impersonate for filesystem operations.

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
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username) if data.import_type == "remote" else None

  # Check if file exists based on import type
  if data.import_type == "local" and not os.path.exists(data.file_path):
    raise ValueError(f"Local file does not exist: {data.file_path}")
  elif data.import_type == "remote" and not fs.exists(data.file_path):
    raise ValueError(f"Remote file does not exist: {data.file_path}")

  should_cleanup = False
  fh = open(data.file_path, "rb") if data.import_type == "local" else fs.open(data.file_path, "r")

  try:
    sample = fh.read(16 * 1024)  # Read 16 KiB sample

    if not sample:
      raise ValueError("File is empty, cannot detect file format.")

    file_type = _detect_file_type(sample)

    if file_type == "unknown":
      raise ValueError("Unable to detect file format.")

    if file_type == "excel":
      metadata = _get_excel_metadata(fh)
    else:
      # CSV, TSV, or other delimited formats
      metadata = _get_delimited_metadata(sample, file_type)

    return metadata

  except Exception as e:
    should_cleanup = True
    LOG.exception(f"Error guessing file metadata: {e}", exc_info=True)
    raise e

  finally:
    fh.close()
    if data.import_type == "local" and should_cleanup and os.path.exists(data.file_path):
      LOG.debug(f"Due to error in guess_file_metadata, cleaning up uploaded local file: {data.file_path}")
      os.remove(data.file_path)


def preview_file(data: PreviewFileSchema, username: str, preview_rows: int = 50) -> Dict[str, Any]:
  """Generate a preview of a file's content with column type mapping.

  This method reads a file and returns a preview of its contents, along with
  column information and metadata for creating tables or further processing.

  Args:
    data: A Pydantic schema with all the required parameters.
    username: The name of the user to impersonate for filesystem operations.
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: File type
      - columns: List of column metadata (name, type)
      - preview_data: Preview of the file data

  Raises:
    ValueError: If the file does not exist or parameters are invalid
    Exception: For various file processing errors
  """
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username) if data.import_type == "remote" else None

  # Check if file exists based on import type
  if data.import_type == "local" and not os.path.exists(data.file_path):
    raise ValueError(f"Local file does not exist: {data.file_path}")
  elif data.import_type == "remote" and not fs.exists(data.file_path):
    raise ValueError(f"Remote file does not exist: {data.file_path}")

  should_cleanup = False
  fh = open(data.file_path, "rb") if data.import_type == "local" else fs.open(data.file_path, "r")

  try:
    if data.file_type == "excel":
      preview = _preview_excel_file(fh, data, preview_rows)
    elif data.file_type in ["csv", "tsv", "delimiter_format"]:
      preview = _preview_delimited_file(fh, data)
    else:
      raise ValueError(f"Unsupported file type: {data.file_type}")

    return preview
  except Exception as e:
    should_cleanup = True
    LOG.exception(f"Error previewing file: {e}", exc_info=True)
    raise e

  finally:
    fh.close()
    if data.import_type == "local" and should_cleanup and os.path.exists(data.file_path):
      LOG.debug(f"Due to error in preview_file, cleaning up uploaded local file: {data.file_path}")
      os.remove(data.file_path)


def _detect_file_type(file_sample: bytes) -> str:
  """Detect the file type based on its content.

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
    if any(keyword in file_type for keyword in ["excel", "spreadsheet", "officedocument.sheet"]):
      return "excel"
    elif any(keyword in file_type for keyword in ["text", "csv", "plain"]):
      # For text files, analyze the content later to determine specific format
      return "delimiter_format"

    LOG.info(f"Detected MIME type: {file_type}, but not recognized as supported format")
    return "unknown"
  except Exception as e:
    message = f"Error detecting file type: {e}"
    LOG.exception(message, exc_info=True)

    raise Exception(message)


def _get_excel_metadata(fh: BinaryIO) -> Dict[str, Any]:
  """Extract metadata for Excel files (.xlsx, .xls).

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
    fh.seek(0)
    try:
      sheet_names = _get_sheet_names_xlsx(BytesIO(fh.read()))
    except Exception:
      LOG.warning("Failed to read Excel file for sheet names with Zip + XML parsing approach, trying next with Polars.")

      # Possibly some other format instead of .xlsx
      fh.seek(0)

      sheet_names = pl.read_excel(
        BytesIO(fh.read()), sheet_id=0, infer_schema_length=10000, read_options={"n_rows": 0}
      ).keys()  # No need to read rows for detecting sheet names

    return {
      "type": "excel",
      "sheet_names": list(sheet_names),
    }
  except Exception as e:
    message = f"Error extracting Excel file metadata: {e}"
    LOG.error(message, exc_info=True)

    raise Exception(message)


def _get_sheet_names_xlsx(fh: BinaryIO) -> List[str]:
  """Quickly list sheet names from an .xlsx file handle.

  - Uses only the stdlib (zipfile + xml.etree).
  - Parses only the small `xl/workbook.xml` metadata (~10-20KB).
  - No full worksheet data is loaded into memory.

  Args:
    fh: Binary file-like object of the workbook.

  Returns:
    A list of worksheet names.
  """
  with zipfile.ZipFile(fh, "r") as z, z.open("xl/workbook.xml") as f:
    tree = ET.parse(f)

  # XML namespace for SpreadsheetML
  ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
  sheets = tree.getroot().find("x:sheets", ns)

  return [s.get("name") for s in sheets]


def _get_delimited_metadata(file_sample: Union[bytes, str], file_type: str) -> Dict[str, Any]:
  """Extract metadata for delimited files (CSV, TSV, etc.).

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
  if isinstance(file_sample, bytes):
    file_sample = file_sample.decode("utf-8", errors="replace")

  # Use CSV Sniffer to detect delimiter and other formatting
  try:
    dialect = csv.Sniffer().sniff(file_sample)
  except Exception as sniff_error:
    message = f"Failed to sniff delimited file: {sniff_error}"
    LOG.exception(message)

    raise Exception(message)

  # Refine file type based on detected delimiter
  if file_type == "delimiter_format":
    if dialect.delimiter == ",":
      file_type = "csv"
    elif dialect.delimiter == "\t":
      file_type = "tsv"
    # Other delimiters remain as 'delimiter_format'

  return {
    "type": file_type,
    "field_separator": dialect.delimiter,
    "quote_char": dialect.quotechar,
    "record_separator": dialect.lineterminator,
  }


def _preview_excel_file(fh: BinaryIO, data: PreviewFileSchema, preview_rows: int = 50) -> Dict[str, Any]:
  """Preview an Excel file (.xlsx, .xls)

  Args:
    fh: File handle for the Excel file
    data: A Pydantic schema with all the required parameters.
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: 'excel'
      - columns: List of column metadata
      - preview_data: Preview of file data

  Raises:
    Exception: If there's an error processing the Excel file
  """
  try:
    fh.seek(0)

    df = pl.read_excel(
      BytesIO(fh.read()),
      sheet_name=data.sheet_name,
      has_header=data.has_header,
      read_options={"n_rows": preview_rows},
      infer_schema_length=10000,
    )

    # Return empty result if the df is empty
    if df.height == 0:
      return {"type": data.file_type, "columns": [], "preview_data": {}}

    schema = df.schema
    preview_data = df.to_dict(as_series=False)

    # Create column metadata with SQL type mapping
    columns = []
    for col in df.columns:
      col_type = str(schema[col])
      sql_type = _map_polars_dtype_to_sql_type(data.sql_dialect, col_type)

      columns.append({"name": col, "type": sql_type})

    result = {"type": data.file_type, "columns": columns, "preview_data": preview_data}

    return result

  except Exception as e:
    message = f"Error previewing Excel file: {e}"
    LOG.error(message, exc_info=True)

    raise Exception(message)


def _preview_delimited_file(
  fh: BinaryIO,
  data: PreviewFileSchema,
  preview_rows: int = 50,
) -> Dict[str, Any]:
  """Preview a delimited file (CSV, TSV, etc.)

  Args:
    fh: File handle for the delimited file
    data: A Pydantic schema with all the required parameters.
    preview_rows: Number of rows to include in preview (default: 50)

  Returns:
    Dict containing:
      - type: File type
      - columns: List of column metadata
      - preview_data: Preview of file data

  Raises:
    Exception: If there's an error processing the delimited file
  """
  try:
    fh.seek(0)

    df = pl.read_csv(
      BytesIO(fh.read()),
      separator=data.field_separator,
      quote_char=data.quote_char,
      eol_char=data.record_separator,
      has_header=data.has_header,
      infer_schema_length=10000,
      n_rows=preview_rows,
      ignore_errors=True,
    )

    # Return empty result if the df is empty
    if df.height == 0:
      return {"type": data.file_type, "columns": [], "preview_data": {}}

    schema = df.schema
    preview_data = df.to_dict(as_series=False)

    # Create detailed column metadata with SQL type mapping
    columns = []
    for col in df.columns:
      col_type = str(schema[col])
      sql_type = _map_polars_dtype_to_sql_type(data.sql_dialect, col_type)

      columns.append({"name": col, "type": sql_type})

    result = {"type": data.file_type, "columns": columns, "preview_data": preview_data}

    return result

  except Exception as e:
    message = f"Error previewing delimited file: {e}"

    LOG.error(message, exc_info=True)
    raise Exception(message)


def guess_file_header(data: GuessFileHeaderSchema, username: str) -> bool:
  """Guess whether a file has a header row.

  This function analyzes a file to determine if it contains a header row based on the
  content pattern. It works for both Excel files and delimited text files (CSV, TSV, etc.).

  Args:
    data: A Pydantic schema with all the required parameters.
    username: The name of the user to impersonate for filesystem operations.

  Returns:
    has_header: Boolean indicating whether the file has a header row

  Raises:
    ValueError: If the file does not exist or parameters are invalid
    Exception: For various file processing errors
  """
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username) if data.import_type == "remote" else None

  # Check if file exists based on import type
  if data.import_type == "local" and not os.path.exists(data.file_path):
    raise ValueError(f"Local file does not exist: {data.file_path}")
  elif data.import_type == "remote" and not fs.exists(data.file_path):
    raise ValueError(f"Remote file does not exist: {data.file_path}")

  fh = open(data.file_path, "rb") if data.import_type == "local" else fs.open(data.file_path, "r")

  has_header = False

  try:
    if data.file_type == "excel":
      # Convert excel sample to CSV for header detection
      try:
        fh.seek(0)

        csv_snippet = pl.read_excel(
          source=BytesIO(fh.read()),
          sheet_name=data.sheet_name,
          infer_schema_length=10000,
          read_options={"n_rows": 20},
        ).write_csv(file=None)

        if isinstance(csv_snippet, bytes):
          csv_snippet = csv_snippet.decode("utf-8", errors="replace")

        has_header = csv.Sniffer().has_header(csv_snippet)
        LOG.info(f"Detected header for Excel file: {has_header}")

      except Exception as e:
        message = f"Error detecting header in Excel file: {e}"
        LOG.exception(message, exc_info=True)

        raise Exception(message)

    elif data.file_type in ["csv", "tsv", "delimiter_format"]:
      try:
        # Reset file position
        fh.seek(0)

        # Read 16 KiB sample
        sample = fh.read(16 * 1024).decode("utf-8", errors="replace")

        has_header = csv.Sniffer().has_header(sample)
        LOG.info(f"Detected header for delimited file: {has_header}")

      except Exception as e:
        message = f"Error detecting header in delimited file: {e}"
        LOG.exception(message, exc_info=True)

        raise Exception(message)

    return has_header

  finally:
    fh.close()


def _get_polars_to_sql_mapping(dialect: str) -> Dict[str, str]:
  """Get full mapping from Polars dtypes to SQL types for a given SQL dialect.

  Internal function that returns the complete mapping dictionary.

  Args:
    dialect: One of "hive", "impala", "trino", "phoenix", "sparksql".

  Returns:
    A dict mapping Polars dtype names to SQL type names.

  Raises:
    ValueError: If the dialect is not supported.
  """
  dl = dialect.lower()
  if dl not in SQL_TYPE_DIALECT_OVERRIDES:
    raise ValueError(f"Unsupported dialect: {dialect}")

  # Merge base_map and overrides[dl] into a new dict, giving precedence to any overlapping keys in overrides[dl]
  return {**SQL_TYPE_BASE_MAP, **SQL_TYPE_DIALECT_OVERRIDES[dl]}


def get_sql_type_mapping(data: SqlTypeMapperSchema) -> List[str]:
  """Get all unique SQL types supported by a given SQL dialect.

  This function returns a sorted list of unique SQL types that are supported
  by the specified SQL dialect based on the Polars to SQL type mappings.

  Args:
    data: A Pydantic schema with the SQL dialect.

  Returns:
    A sorted list of unique SQL type names for the dialect.

  Raises:
    ValueError: If the dialect is not supported.
  """
  # Get the full mapping
  mapping = _get_polars_to_sql_mapping(data.sql_dialect)

  # Extract unique SQL types and return as sorted list
  unique_sql_types = sorted(set(mapping.values()))
  return unique_sql_types


def _map_polars_dtype_to_sql_type(dialect: str, polars_type: str) -> str:
  """Map a Polars dtype to the corresponding SQL type for a given dialect.

  Args:
    dialect: One of "hive", "impala", "trino", "phoenix", "sparksql".
    polars_type: Polars dtype name as string.

  Returns:
    A string representing the SQL type.

  Raises:
    ValueError: If the dialect or polars_type is not supported.
  """
  mapping = _get_polars_to_sql_mapping(dialect)

  if polars_type not in mapping:
    raise ValueError(f"No mapping for Polars dtype {polars_type} in dialect {dialect}")

  return mapping[polars_type]
