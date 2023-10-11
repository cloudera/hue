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


def openai_completion_api(prompt, metadata=None, type=None, dialect=None):
    if LLM.OPENAI.ENABLE.get():
        prompt_data = ""
        if type:
            prompt_data = generate_instruction(type, prompt, metadata, dialect)        
        # prompt_data = prompt_data + prompt
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

def generate_instruction(type, userprompt, metadata, dialect):
    if type=="generateSql":
        return f"Act as an {dialect} SQL expert. Translate the NQL statement into SQL using the following metadata {metadata}. \
            List any the assumptions not covered by the supplied metadata.  \
            NQL: {userprompt}. \
            Return the answer in the following format: <code></code><assumptions></assumptions>"
    if type=="editSql":
        return f"Act as an {dialect} SQL expert and modify the SQL using the following metadata {metadata}. \
            List any the assumptions not covered by the supplied metadata.  \
            {userprompt}. \
            Return the answer in the following format: <code></code><assumptions></assumptions>"    
    elif type=="listRelevantTables":
        return f"This is a list of existing tables {metadata}. Assume the names reflect their content. Filter out the names you would need metadata for in order to translate the following NQL to SLQ: {userprompt}. Only return the list of names, separated by comma and wrap it a <tables> tag."        
    elif type=="optimize":
        return f"Act as an {dialect} SQL expert. Optimize this SQL query and explain the improvement if any. Wrap the new code in a <code> tag and the explanation in an <explain> tag: {userprompt}"
    elif type=="correctandexplain":
        return f"Act as an {dialect} SQL expert. Fix this broken sql query and explain the fix. Wrap the corrected code in a <code> tag and the explaination in an <explain> tag: {userprompt}"
    elif type=="explain":
        return f"Act as an {dialect} SQL expert and explain in natural language using non technical terms, what this query does: {userprompt}. "
    else:
        return ""