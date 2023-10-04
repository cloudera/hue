from enum import Enum
from typing import Callable, Dict
from dataclasses import dataclass

from pyformatting import optional_format

from ..types import SQLResponse

import logging
LOG = logging.getLogger()

class TaskType(str, Enum):
    GENERATE = 'generate',
    EDIT = 'edit',
    SUMMARIZE = 'summarize',
    OPTIMIZE = 'optimize',
    FIX = 'fix',
    FILTER_TABLES = 'filter_tables'

@dataclass
class TaskParams:
    dialect: str
    input: str
    sql: str
    metadata: str

class Task:
    def __init__(self, template: str, parser: Callable[[str], SQLResponse]):
      self.template = template
      self.parser = parser

    def build_prompt(self, params: TaskParams) -> str:
        prompt = optional_format(self.template,
                                 input=params.input,
                                 sql=params.sql,
                                 dialect=params.dialect,
                                 metadata=params.metadata)
        return prompt

def get_task(tasks: Dict[TaskType, Task], type: TaskType) -> Task:
    task = tasks[type]
    if task is None:
        exp = f'Unsupported task - {type}'
        LOG.error(exp)
        raise Exception(exp)
    return task
