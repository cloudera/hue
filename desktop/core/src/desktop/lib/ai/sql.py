import logging
LOG = logging.getLogger()

from .types import SQLResponse

from .models.base_model import BaseModel
from .models.gpt import GPTModel
from .models.titan import TitanModel
from .models.task import TaskType

from .services.base_service import BaseService
from .services.openai import OpenAiService
from .services.bedrock import BedrockService
from .services.azure import AzureService

from notebook.api import TableReader

from desktop.conf import AI_INTERFACE

def _model_factory(model: str, task: TaskType) -> BaseModel:
    if model == "gpt":
        return GPTModel(task)
    elif model == "titan":
        return TitanModel(task)
    else:
        LOG.error("Model configured is invalid")
        raise Exception(f"Invalid model name - {model}")

def _service_factory(service_name: str) -> BaseService:
    if service_name == "openai":
        return OpenAiService()
    elif service_name == "azure":
        return AzureService()
    elif service_name == "bedrock":
        return BedrockService()
    else:
        LOG.error("Service configured is invalid")
        raise Exception(f"Invalid service name - {service_name}")

def build_create_table_ddl(table: dict) -> str:
    table_name = table["name"]

    formatted_columns = []
    for col in table["columns"]:
        column_str = f'{col["name"]} {col["type"]}'
        if col.get("comment"):
            column_str += f' COMMENT "{col["comment"]}"'
        if col.get("primaryKey"):
            column_str += ' PRIMARY KEY'
        if col.get("partitionKey"):
            column_str += ' PARTITIONED BY'
        formatted_columns.append(column_str)
    column_names = ', '.join(formatted_columns)

    return f'CREATE TABLE {table_name} ({column_names});'

SAMPLE_ROWS = 3
# Following best practices sugested in https://arxiv.org/abs/2204.00498
def build_sample_data(reader: TableReader, table) -> str:
    table_name = table["name"]
    db_name = table["dbName"]

    col_names = list(map(lambda col: col["name"], table["columns"]))
    rows = reader.fetch(db_name, table["name"], col_names, SAMPLE_ROWS)

    col_str = ", ".join(col_names)
    rows_str = "\n".join(map(lambda row: ", ".join(str(v) for v in row), rows))

    row_count = len(rows)
    if row_count > 0:
        return f"/*\n{row_count} example rows of table {table_name}:\n{col_str}\n{rows_str}\n*/"
    else:
        return "/*\nTable is empty\n*/"

def perform_sql_task(request, task: TaskType, input: str, sql: str, dialect: str, metadata: dict) -> SQLResponse:
    service = _service_factory(AI_INTERFACE.SERVICE.get())
    model = _model_factory(AI_INTERFACE.MODEL.get() or service.get_default_model(), task)

    reader = TableReader(request, "hive")

    table_metadatas = []
    if metadata:
        for table in metadata["tables"]:
            create_ddl = build_create_table_ddl(table)
            sample_data = build_sample_data(reader, table)
            table_metadatas.append(f"{create_ddl}\n{sample_data}")

    metadata_str = '\n\n'.join(table_metadatas)
    prompt = model.build_prompt(input, sql, dialect, metadata_str)
    response_str = service.process(prompt)
    response = model.parse_response(response_str)

    return response
