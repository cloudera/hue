import abc
from pyformatting import optional_format

from .task import Task, ResponseDict

class BaseModel(abc.ABC):
    def __init__(self, task: Task):
        self.task = task

    def build_prompt(self, input: str, sql: str, dialect: str, metadata: str) -> str:
        prompt = optional_format(self.task.template, input=input, sql=sql, dialect=dialect, metadata=metadata)
        return prompt

    def parse_response(self, response) -> ResponseDict:
        return self.task.parser(response)
