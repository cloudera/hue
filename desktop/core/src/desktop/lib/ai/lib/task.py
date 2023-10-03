from enum import Enum
from typing import Callable, Dict
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

class Task:
    def __init__(self, template: str, parser: Callable[[str], SQLResponse]):
      self.template = template
      self.parser = parser

def get_task(tasks: Dict[TaskType, Task], type: TaskType) -> Task:
    task = tasks[type]
    if task is None:
        exp = f'Unsupported task - {type}'
        LOG.error(exp)
        raise Exception(exp)
    return task
