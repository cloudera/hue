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
    elif service_name == "bedrock":
        return BedrockService()
    else:
        LOG.error("Service configured is invalid")
        raise Exception(f"Invalid service name - {service_name}")

def format_metadata(metadata: dict) -> str:
    formatted_metadata = []

    for table in metadata["tables"]:
        table_name = table["name"]
        column_names = ', '.join(map(lambda col: f'{col["name"]} {col["type"]}', table["columns"]))
        formatted_metadata.append(f'create table {table_name} ({column_names})')

    return ';\n\n'.join(formatted_metadata)

def perform_sql_task(task: TaskType, input: str, sql: str, dialect: str, metadata: dict) -> SQLResponse:
    service = _service_factory(AI_INTERFACE.SERVICE.get())
    model = _model_factory(AI_INTERFACE.MODEL.get() or service.get_default_model(), task)

    metadata_str = format_metadata(metadata) if metadata else ""
    prompt = model.build_prompt(input, sql, dialect, metadata_str)
    response_str = service.process(prompt)
    response = model.parse_response(response_str)

    return response
