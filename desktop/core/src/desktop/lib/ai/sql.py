from .models.base_model import BaseModel
from .models.gpt import GPTModel
from .models.titan import TitanModel

from .services.base_service import BaseService
from .services.openai import OpenAiService
from .services.bedrock import BedrockService

import logging
LOG = logging.getLogger()

from desktop.conf import LLM

def _model_factory(model_name) -> BaseModel:
    if model_name == "openai":
        return GPTModel()
    elif model_name == "bedrock":
        return TitanModel()
    else:
        LOG.error("Model configured is invalid")
        raise Exception(f"Invalid model name - {model_name}")

def _service_factory(service_name) -> BaseService:
    if service_name == "openai":
        return OpenAiService()
    elif service_name == "bedrock":
        return BedrockService()
    else:
        LOG.error("Service configured is invalid")
        raise Exception(f"Invalid service name - {service_name}")

def format_metadata(metadata) -> str:
    formatted_metadata = []

    for table in metadata["tables"]:
        table_name = table["name"]
        column_names = ', '.join(map(lambda col: f'{col["name"]} {col["type"]}', table["columns"]))
        formatted_metadata.append(f'create table {table_name} ({column_names})')

    return ';\n\n'.join(formatted_metadata)

def perform_sql_task(task, input, sql, dialect, metadata):
    model = _model_factory(LLM.SQL_LLM.get())
    service = _service_factory(LLM.SQL_LLM.get())

    metadata_str = format_metadata(metadata) if metadata else ""
    prompt = model.build_prompt(task, input, sql, dialect, metadata_str)
    response_str = service.process(prompt)
    response = model.parse_response(task, response_str)

    return response
