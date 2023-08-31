import abc
import json
from enum import Enum
from pyformatting import optional_format

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from desktop.conf import LLM

class Task(str, Enum):
    GENERATE = 'generate',
    EDIT = 'edit',
    SUMMARIZE = 'summarize',
    OPTIMIZE = 'optimize',
    FIX = 'fix',
    FILTER_TABLES = 'filter_tables'

class LlmApi(abc.ABC):
    def __init__(self, task_templates):
        self.task_templates = task_templates

    @abc.abstractmethod
    def process(self, task, input, sql, dialect, metadata):
        pass

    def format_metadata(self, metadata):
        formatted_metadata = []

        for table in metadata["tables"]:
            table_name = table["name"]
            column_names = ', '.join(map(lambda col: f'{col["name"]} {col["type"]}', table["columns"]))
            formatted_metadata.append(f'create table {table_name} ({column_names})')

        return ';\n\n'.join(formatted_metadata)

    @abc.abstractmethod
    def infer(self, prompt):
        pass

    def process(self, task, input, sql, dialect, metadata):
        template = self.task_templates[task]
        # metadata_str = self.format_metadata(metadata) if metadata else None
        prompt = optional_format(template, input=input, sql=sql, dialect=dialect, metadata=metadata['ddl'])
        inference = self.infer(prompt)
        return self.parse_inference(task, inference)

    @abc.abstractmethod
    def parse_inference(self, task, inference):
        pass

class HueLlmApi(LlmApi):
    def __init__(self, task_templates, model):
        super().__init__(task_templates)
        self.model = model

    def _get_client(self):
        client = HttpClient(LLM.HUE_LLM.BASE_URL.get())
        client.set_verify(False)
        client.set_headers({
          'Content-Type': 'application/json'
        })
        return client

    def infer(self, prompt):
        client = self._get_client()
        resource = Resource(client)
        data = json.dumps({
            'model': self.model,
            'prompt': prompt
        }).encode('utf8')
        response = resource.post(relpath=LLM.HUE_LLM.PATH.get(), data=data)
        return response['inference']

def is_llm_sql_enabled():
    llm_enabled = LLM.SQL_LLM.get()
    return bool(llm_enabled.strip())


def is_vector_db_enabled():
    RELEVENCY = LLM.RELEVENCY.get()
    return RELEVENCY=="vector_db"
    # return bool(llm_enabled.strip())