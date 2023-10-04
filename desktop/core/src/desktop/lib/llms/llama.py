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
Table details: {metadata}
Q: Summarize the SQL query.
SQL query: {sql}
A:"""

_OPTIMIZE = """Act as a {dialect} SQL expert.
Table details: {metadata}
Q: Optimize the SQL query.
SQL query: {sql}
A:"""

_FIX = """Act as a {dialect} SQL expert.
Table details: {metadata}
Q: Fix the SQL query.
SQL query: {sql}
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
        super().__init__('llama', TASK_TEMPLATES)

    def parse_inference(self, inference):
        return {
            'sql': inference,
            'assumptions': ''
        }
