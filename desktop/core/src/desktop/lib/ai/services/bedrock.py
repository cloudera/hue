import io
import json

from ..lib.base_service import BaseService
from ..lib.base_model import BaseModel
from ..models.titan import TitanModel
from ..models.claude import ClaudeModel

from desktop.conf import AI_INTERFACE

class BedrockService(BaseService):
    def __init__(self, model_name: str):
        import boto3
        self.bedrock = boto3.client('bedrock')

        super().__init__(self.get_model(model_name))

    def get_model(self, model_name: str) -> BaseModel:
        if model_name == "claude":
            return ClaudeModel()
        return TitanModel()

    def call_model(self, data: dict) -> str:
        model_name = AI_INTERFACE.MODEL_NAME.get() or self.model.get_default_name()
        response = self.bedrock.invoke_model(
            modelId=model_name,
            body=json.dumps(data)
        )

        return io.BytesIO(response['body'].read()).readlines()[0].decode('utf-8')
