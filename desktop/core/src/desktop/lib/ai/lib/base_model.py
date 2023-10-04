import abc

from .task import Task, TaskType
from ..types import SQLResponse

class BaseModel(abc.ABC):
    @abc.abstractmethod
    def get_default_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_task(self, task_type: TaskType) -> Task:
        pass

    @abc.abstractmethod
    def build_data(self, prompt: str) -> dict:
        pass

    # Extract the text data from the full model response
    @abc.abstractmethod
    def extract_response(self, response: str) -> str:
        pass
