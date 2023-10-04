from ..lib.base_service import BaseService

from ..lib.base_model import BaseModel
from ..models.gpt import GPTModel

from desktop.conf import AI_INTERFACE, get_ai_service_token

_api_key = get_ai_service_token()

class AzureService(BaseService):
    def __init__(self, model_name: str):
        import openai
        openai.api_type = "azure"
        openai.api_base = AI_INTERFACE.BASE_URL.get()
        openai.api_key = _api_key
        openai.api_version = "2023-07-01-preview" # TODO: This could be a configuration
        self.openai = openai

        super().__init__(self.get_model(model_name))

    def get_model(self, model_name: str) -> BaseModel:
        return GPTModel()

    def call_model(self, data: dict) -> str:
        deployment_name = AI_INTERFACE.MODEL_NAME.get()
        response = self.openai.ChatCompletion.create(
            engine=deployment_name,
            temperature=0,
            messages=[data]
        )
        choices = response.choices[0]
        return choices.message.content.strip()
