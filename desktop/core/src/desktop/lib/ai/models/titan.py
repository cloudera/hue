from .task import Task, TaskType, get_task
from .base_model import BaseModel
from ..utils.xml import extract_tag_content
from ..types import SQLResponse

_GENERATE = """Act as an {dialect} SQL expert. Translate the NQL statement into SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. Use lower() and LIKE '%%' unless you are sure about how to match the data.

NQL: {input}
Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_EDIT = """Act as an {dialect} SQL expert. Based on the input modify the SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. Use lower() and LIKE '%%' unless you are sure about how to match the data.
SQL query: {sql}
Input: {input}
Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_SUMMARIZE = """Act as an {dialect} SQL expert. Based on the input Summarize the SQL using the following metadata: {metadata}.
Explain in natural language using non technical terms, what this query does: {sql}.
"""

_OPTIMIZE = """Act as an {dialect} SQL expert.
Optimize this SQL query and explain the improvement if any. Only optimize in a way so that the result of the query remains the same. If you can't
optimize the query then shortly explain alternative options if any.
Use the following metadata: {metadata}. Wrap the new code in a <code> tag and the explanation in an <explain> tag with a closing </explain>: {sql}
"""

_FIX = """Act as an {dialect} SQL expert.
Fix this syntactically broken sql query and explain the fix using the following metadata: {metadata}. Do not optimize and only make the minimal modifcation needed to create a valid query.
Wrap the corrected code in a <code> tag and the explaination in an <explain> tag with a closing </explain>: {sql}
"""

def _code_assumptions_parser(response: str) -> SQLResponse:
    return SQLResponse(
        sql=extract_tag_content('code', response),
        assumptions=extract_tag_content('assumptions', response),
    )

def _code_explain_parser(response: str) -> SQLResponse:
    return SQLResponse(
        sql=extract_tag_content('code', response),
        explain=extract_tag_content('explain', response),
    )

def _summary_parser(response: str) -> SQLResponse:
    return SQLResponse(
        summary=response,
    )

_TASKS = {
    TaskType.GENERATE: Task(_GENERATE, _code_assumptions_parser),
    TaskType.EDIT: Task(_EDIT, _code_assumptions_parser),
    TaskType.SUMMARIZE: Task(_SUMMARIZE, _summary_parser),
    TaskType.OPTIMIZE: Task(_OPTIMIZE, _code_explain_parser),
    TaskType.FIX: Task(_FIX, _code_explain_parser)
}

class TitanModel(BaseModel):
    def __init__(self, task_type: TaskType):
        super().__init__(get_task(_TASKS, task_type))
