import io
import json

from ..lib.base_service import BaseService

from desktop.conf import AI_INTERFACE

_default_model = "titan"
_model_name = AI_INTERFACE.MODEL_NAME.get() or "amazon.titan-tg1-large"

class BedrockService(BaseService):
    def __init__(self):
        import boto3
        self.bedrock = boto3.client('bedrock')

    def get_default_model(self) -> str:
        return _default_model

    def process(self, prompt: str) -> str:
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "stopSequences": [],
                "temperature": 0,
                "topP": 0.9
            }
        }
        response = self.bedrock.invoke_model(
            modelId=_model_name,
            body=json.dumps(body)
        )

        data = json.loads(io.BytesIO(response['body'].read()).readlines()[0].decode('utf-8'))

        return data["results"][0]["outputText"]
