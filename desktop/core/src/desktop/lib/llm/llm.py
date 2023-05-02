#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from desktop.conf import LLM
import logging as LOG

import json
import pdb

from desktop.lib.llm.open_ai import openai_completion_api
# from open_ai import generate_openai_response

def is_llm_sql_enabled():
    llm_enabled = LLM.ENABLE.get()
    return llm_enabled

def generate_sql(prompt, parsed_data):
    query_to_send = "### Postgres SQL tables, with their properties:" 
    query_to_send += "#"
    output_str = ""
    for key, value in parsed_data.items():
      if isinstance(value, list):
        output_str += f"{key}({', '.join(map(str, value))})\n"
    query_to_send += output_str    
    query_to_send += "###\n"
    query_to_send += prompt
    query_to_send += "\n"
    response = {}
    prompt = f"{prompt}\nmetadata:{query_to_send}\nSQL:"
    if LLM.OPENAI.ENABLE.get():
        open_ai_response = openai_completion_api(prompt)
        response['open_ai'] = text

    return response;  

def chat(prompt, metadata=None, type="generate_sql", conversation_id=None):
   response = {}

   if LLM.OPENAI.ENABLE.get():
      response['open_ai'] = openai_completion_api(prompt, metadata, type)
   return response



  