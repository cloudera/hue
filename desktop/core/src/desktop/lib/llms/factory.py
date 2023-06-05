from .base import LlmApi
from .llama import HueLlamaApi
from .openai import OpenAiApi

from desktop.conf import LLM

import logging
LOG = logging.getLogger()

def llm_api_factory() -> LlmApi:
    sql_llm = LLM.SQL_LLM.get()

    if sql_llm == "hue_llm":
        return HueLlamaApi()
    elif sql_llm == "openai":
        return OpenAiApi()
    else:
        LOG.error("Invalid sql_llm configuration")
