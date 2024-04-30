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

import logging
LOG = logging.getLogger()

import json

from desktop.lib.ai.types import SQLResponse

from desktop.lib.ai.lib.base_model import BaseModel
from desktop.lib.ai.models.gpt import GPTModel
from desktop.lib.ai.models.titan import TitanModel
from desktop.lib.ai.lib.task import TaskType, TaskParams

from desktop.lib.ai.lib.base_service import BaseService
from desktop.lib.ai.services.openai import OpenAiService
from desktop.lib.ai.services.bedrock import BedrockService
from desktop.lib.ai.services.azure import AzureService
from desktop.lib.ai.services.ai_assistant import AiService
from desktop.lib.utils.cache import LRUCache

from notebook.api import TableReader

from desktop.conf import AI_INTERFACE

# Following best practices sugested in https://arxiv.org/abs/2204.00498
SAMPLE_ROWS = 3
MAX_VALUE_LENGTH = 20
DATA_DELIMITER = ","

table_meta_cache = LRUCache(AI_INTERFACE.TABLE_DATA_CACHE_SIZE.get())
ADD_TABLE_DATA = AI_INTERFACE.ADD_TABLE_DATA.get()

def _get_service() -> BaseService:
  service_name = AI_INTERFACE.SERVICE.get()
  model_key: str = AI_INTERFACE.MODEL.get()

  if service_name == "openai":
    return OpenAiService(model_key)
  elif service_name == "azure":
    return AzureService(model_key)
  elif service_name == "bedrock":
    return BedrockService(model_key)
  elif service_name == "ai_assistant":
    return AiService(model_key)
  else:
    LOG.error("Service configured is invalid")
    raise Exception(f"Invalid service name - {service_name}")

def build_create_table_ddl(table: dict) -> str:
  table_name = table["name"]

  details = []

  for col in table["columns"]:
    column_str = f'{col["name"]} {col["type"]}'
    if col.get("comment"):
      column_str += f' COMMENT "{col["comment"]}"'
    if col.get("primaryKey"):
      column_str += ' PRIMARY KEY'
    if col.get("partitionKey"):
      column_str += ' PARTITIONED BY'
    details.append(column_str)

  for key in table.get("foreignKeys", []):
    details.append(f"FOREIGN KEY ({key['fromColumn']}) REFERENCES {key['toTable']} ({key['toColumn']})")

  details_str = ', '.join(details)
  ddl = f'CREATE TABLE {table_name} ({details_str})'

  table_comment = table.get("comment")
  if table_comment != None:
    ddl = f"{ddl} COMMENT '{table_comment}'"

  return ddl + ';'

def get_val_str(value) -> str:
  value = str(value).strip()
  if len(value) > MAX_VALUE_LENGTH:
    value = value[:MAX_VALUE_LENGTH].strip() + "..."
  return value

NOT_AVAILABLE_MSG = "/*\nExample rows not available.\n*/"
def build_sample_data(reader: TableReader, table) -> str:
  table_name = table["name"]
  db_name = table.get("dbName", "")
  col_names = list(map(lambda col: col["name"], table["columns"]))

  if "type" in table and table["type"].lower() == "view":
    return NOT_AVAILABLE_MSG

  try:
    rows = reader.fetch(db_name, table["name"], col_names, SAMPLE_ROWS)

    col_str = DATA_DELIMITER.join(col_names)
    rows_str = "\n".join(map(lambda row: DATA_DELIMITER.join(get_val_str(v) for v in row), rows))

    row_count = len(rows)
    if row_count > 0:
      return f"/*\n{row_count} example rows of table {table_name}:\n{col_str}\n{rows_str}\n*/"
  except Exception as exc:
    LOG.error(f"Error fetching sample data for table {table_name} - {exc}")

  return NOT_AVAILABLE_MSG

def get_table_key(table) -> str:
  return json.dumps(table)

def format_metadata(metadata, reader) -> str:
  table_metadatas = []

  for table in metadata["tables"]:
    table_key = get_table_key(table)
    table_meta = table_meta_cache.get(table_key)
    if table_meta == None:
      table_meta = build_create_table_ddl(table)
      if ADD_TABLE_DATA:
        sample_data = build_sample_data(reader, table)
        table_meta = f"{table_meta}\n{sample_data}"
      table_meta_cache.put(table_key, table_meta)
    table_metadatas.append(table_meta)

  return '\n\n'.join(table_metadatas)

def perform_sql_task(request, task: TaskType, input: str, sql: str, dialect: str, metadata: dict) -> SQLResponse:
  reader = TableReader(request, dialect)
  metadata_str = format_metadata(metadata, reader) if metadata else ""

  task_params = TaskParams(dialect, input, sql, metadata_str)

  service = _get_service()
  response = service.process(task, task_params)

  return response
