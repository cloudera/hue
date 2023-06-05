import abc
from .base import HueLlmApi, Task

_GENERATE = """Act as a {dialect} SQL expert.
Table details: {metadata}
Q: Generate SQL query to answer the input.
Input: {input}
A:"""

_EDIT = """Act as a {dialect} SQL expert.
Table details: {metadata}
Q: Modify the SQL query based on the input.
SQL query: {sql}
Input: {input}
A:"""

_SUMMARIZE = """Act as a {dialect} SQL expert.
SQL query: {sql}
Q: Summarize the above SQL query.
A:"""

_OPTIMIZE = """Act as a {dialect} SQL expert.
Table details: {metadata}
SQL query: {sql}
Q: Optimize the SQL query.
A:"""

_FIX = """Act as a {dialect} SQL expert.
Table details: {metadata}
SQL query: {sql}
Q: Fix the SQL query.
A:"""

TASK_TEMPLATES = {
    Task.GENERATE: _GENERATE,
    Task.EDIT: _EDIT,
    Task.SUMMARIZE: _SUMMARIZE,
    Task.OPTIMIZE: _OPTIMIZE,
    Task.FIX: _FIX
}

class HueLlamaApi(HueLlmApi):
    def __init__(self):
        super().__init__(TASK_TEMPLATES, 'llama')

    def parse_inference(self, task, inference):
        if task == Task.SUMMARIZE:
            return {
                'summary': inference
            }
        else:
            return {
                'sql': inference
            }
