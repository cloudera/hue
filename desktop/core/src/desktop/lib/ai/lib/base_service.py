import abc

from ..types import SQLResponse
from .task import TaskParams, TaskType
from .base_model import BaseModel

class BaseService(abc.ABC):
    model: BaseModel

    def __init__(self, model: BaseModel):
        self.model = model

    @abc.abstractmethod
    def call_model(self, data:dict) -> str:
        pass

    def process(self, task_type: TaskType, params: TaskParams) -> SQLResponse:
        task = self.model.get_task(task_type)

        # Step 1 - Build request
        prompt = task.build_prompt(params)
        data = self.model.build_data(prompt)

        # Step 2 - Send request to the model
        response_str = self.call_model(data)

        # Step 3 - Parse response
        response = task.parser(response_str)

        return response
