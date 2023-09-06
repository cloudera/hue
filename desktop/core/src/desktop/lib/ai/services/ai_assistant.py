import json

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from .base_service import BaseService

from desktop.conf import LLM

_base_url = LLM.HUE_LLM.BASE_URL.get()
_path = "/api/infer"

def _get_client():
    client = HttpClient(_base_url)
    client.set_verify(False)
    client.set_headers({
      'Content-Type': 'application/json'
    })
    return client

class OpenAiService(BaseService):
    def __init__(self):
        self.client = _get_client()

    def process(self, prompt: str) -> str:
        resource = Resource(self.client)
        data = json.dumps({
            'prompt': prompt,
            'stopping_text': '</code>' # TODO: make this an argument
        }).encode('utf8')
        response = resource.post(relpath=_path, data=data)
        return response['inference']
