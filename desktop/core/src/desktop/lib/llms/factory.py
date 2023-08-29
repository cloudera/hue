from .base import LlmApi
from .llama import HueLlamaApi
from .llama2 import LLaMA2Api
from .openai import OpenAiApi
from .bedrock import BedrockApi

from desktop.conf import LLM

import logging
LOG = logging.getLogger()

def llm_api_factory() -> LlmApi:
    sql_llm = LLM.SQL_LLM.get()

    if sql_llm == "hue_llm":
        return HueLlamaApi()
    elif sql_llm == "openai":
        return OpenAiApi()
    elif sql_llm == "openai":
        return OpenAiApi()
    elif sql_llm == "bedrock":
        return BedrockApi()
    else:
        LOG.error("Invalid sql_llm configuration")
