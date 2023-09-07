from .base_service import BaseService

from desktop.conf import AI_INTERFACE, get_ai_service_token

_default_model = "gpt"
_model_name = AI_INTERFACE.MODEL_NAME.get() or "gpt-3.5-turbo-16k"
_api_key = get_ai_service_token()

class OpenAiService(BaseService):
    def __init__(self):
        import openai
        openai.api_key = _api_key

        self.openai = openai

    def get_default_model(self) -> str:
        return _default_model

    def process(self, prompt: str) -> str:
        response = self.openai.ChatCompletion.create(
            model=_model_name,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        choices = response.choices[0]
        return choices.message.content.strip()
