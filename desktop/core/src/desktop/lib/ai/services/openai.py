from .base_service import BaseService

from desktop.conf import LLM

_api_key = LLM.OPENAI.TOKEN.get()
_model_name = LLM.OPENAI.MODEL.get()

class OpenAiService(BaseService):
    def __init__(self):
        import openai
        openai.api_key = _api_key

        self.openai = openai

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

