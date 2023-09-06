import abc
from enum import Enum

import logging
LOG = logging.getLogger()

from pyformatting import optional_format

class Task(str, Enum):
    GENERATE = 'generate',
    EDIT = 'edit',
    SUMMARIZE = 'summarize',
    OPTIMIZE = 'optimize',
    FIX = 'fix',
    FILTER_TABLES = 'filter_tables'

class BaseModel(abc.ABC):
    def __init__(self, task_templates):
        self.task_templates = task_templates

    def get_template(self, task_name):
        template = self.task_templates[task_name]
        if template is None:
            LOG.error(f'Unsupported task - {task_name}')
            raise Exception()
        return template

    def build_prompt(self, task: Task, input: str, sql: str, dialect: str, metadata: str):
        template = self.get_template(task)
        prompt = optional_format(template, input=input, sql=sql, dialect=dialect, metadata=metadata)
        return prompt

    @abc.abstractmethod
    def parse_response(self, task, response):
        pass
