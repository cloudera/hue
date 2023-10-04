from ..lib.base_service import BaseService

from ..lib.base_model import BaseModel
from ..models.gpt import GPTModel

from desktop.conf import AI_INTERFACE, get_ai_service_token

_api_key = get_ai_service_token()

class OpenAiService(BaseService):
    def __init__(self, model_name: str):
        import openai
        openai.api_key = _api_key # type: ignore
        self.openai = openai

        super().__init__(self.get_model(model_name))

    def get_model(self, model_name: str) -> BaseModel:
        return GPTModel()

    def call_model(self, data: dict) -> str:
        model_name = AI_INTERFACE.MODEL_NAME.get() or self.model.get_default_name()
        response = self.openai.ChatCompletion.create(
            model=model_name,
            temperature=0,
            messages=[data]
        )
        choices = response.choices[0]
        return choices.message.content.strip()
