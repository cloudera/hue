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

import pdb
from desktop.conf import LLM
import openai


def openai_completion_api(prompt, metadata=None, type=None):
    if LLM.OPENAI.ENABLE.get():
        prompt_data = ""
        if type:
            prompt_data = prompt_type(type)
        if metadata:
            prompt_data = prompt_data + str(metadata)

        prompt_data = prompt_data + prompt
        try:
            openai_token = LLM.OPENAI.TOKEN.get()
            openai.api_key = openai_token
            model = LLM.OPENAI.MODEL.get()
            response = openai.Completion.create(
                engine=model,
                prompt=prompt_data,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5
            )
            choices = response.choices[0]
            text = choices.text.strip()
            return text
        except:
            return "Error Encountered While Callling OpenAI API"
    else:
        return "Open AI Not Enabled"

def prompt_type(type):
    if type=="generate_sql":
        return "Act as SQL Generator, and generate a sql query for the following SQL with metadata:"
    elif type=="explain":
        return "Act as SQL Expert, and explain the following query:"
    elif type=="auto_correct":
        return "Act as SQL Expert, and Correct the following query:"
    elif type=="correctandexplain":
        return "Act as SQL Expert, and Correct and explain the following query and Wrap the corrected code in a <code> tag and the explaination in an <explain> tag:"
    elif type=="nql":
        return "Act as SQL Expert,Translate the NQL statement into SQL and wrap it a sql-tag.List the assumptions made about the DB data model and wrap it in an assumptions-tag.List missing DB data model information and wrap it in a missing-tag.:"
    else:
        return ""