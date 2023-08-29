import abc
import re
import io
import json

import boto3

from .base import LlmApi, Task

_GENERATE = """Act as an {dialect} SQL expert. Translate the NQL statement into SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. Use lower() and LIKE '%%' unless you are sure about how to match the data.

NQL: {input}
Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_EDIT = """Act as an {dialect} SQL expert. Based on the input modify the SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. Use lower() and LIKE '%%' unless you are sure about how to match the data.
SQL query: {sql}
Input: {input}
Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_SUMMARIZE = """Act as an {dialect} SQL expert.
Explain in natural language using non technical terms, what this query does: {sql}.
"""

_OPTIMIZE = """Act as an {dialect} SQL expert.
Optimize this SQL query and explain the improvement if any.
Wrap the new code in a <code> tag and the explanation in an <explain> tag with a closing </explain>: {sql}
"""

_FIX = """Act as an {dialect} SQL expert.
Fix this broken sql query and explain the fix.
Wrap the corrected code in a <code> tag and the explaination in an <explain> tag with a closing </explain>: {sql}
"""

TASK_TEMPLATES = {
    Task.GENERATE: _GENERATE,
    Task.EDIT: _EDIT,
    Task.SUMMARIZE: _SUMMARIZE,
    Task.OPTIMIZE: _OPTIMIZE,
    Task.FIX: _FIX
}

_model_name = "amazon.titan-tg1-large"

bedrock = boto3.client('bedrock')

def extractTagContent(tag, text):
    matches = re.findall(f'<{tag}>(.*?)</{tag}>', text, flags=re.DOTALL)
    return matches[0] if len(matches) > 0 else None

class BedrockApi(LlmApi):
    def __init__(self):
        super().__init__(TASK_TEMPLATES)

    def infer(self, prompt):
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "stopSequences": [],
                "temperature": 0,
                "topP": 0.9
            }
        }
        response = bedrock.invoke_model(
            modelId=_model_name,
            body=json.dumps(body)
        )

        data = json.loads(io.BytesIO(response['body'].read()).readlines()[0].decode('utf-8'))

        return data["results"][0]["outputText"]

    def parse_inference(self, task, inference):
        if task == Task.SUMMARIZE:
            return {
                'summary': inference
            }
        else:
            return {
                'sql': extractTagContent('code', inference),
                'assumptions': extractTagContent('assumptions', inference),
                'explain': extractTagContent('explain', inference),
            }
