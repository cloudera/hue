from enum import Enum
from typing import Callable, Dict
from dataclasses import dataclass

from pyformatting import optional_format
from desktop.conf import AI_INTERFACE
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
                                 metadata=params.metadata,
                                 dialect_prompt=build_dialect_prompt(params.dialect))
        return prompt

def get_task(tasks: Dict[TaskType, Task], type: TaskType) -> Task:
    task = tasks[type]
    if task is None:
        exp = f'Unsupported task - {type}'
        LOG.error(exp)
        raise Exception(exp)
    return task


def build_dialect_prompt(dialect: str) -> str:
    ADD_TABLE_DATA = AI_INTERFACE.ADD_TABLE_DATA.get()
    dialect_prompt = ""
    if not ADD_TABLE_DATA:
        if dialect.lower() in ["postgresql", "mysql"]:
            dialect_prompt += "Use lower() and ILIKE '%%' unless you are sure about how to match the data."
        else:
            dialect_prompt += "Use lower() and LIKE '%%' unless you are sure about how to match the data."
    return dialect_prompt
