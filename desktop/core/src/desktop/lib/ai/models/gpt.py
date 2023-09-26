from .task import Task, TaskType, get_task
from .base_model import BaseModel
from ..utils.xml import extract_tag_content
from ..types import SQLResponse

_GENERATE = """Act as an {dialect} SQL expert. Translate the NQL statement into SQL using the following metadata: {metadata}.
Use lower() and LIKE '%%' unless you are sure about how to match the data.

Always list any assumptions not covered by the supplied metadata.
Always warn if the generated SQL modifies or deletes data or risk being very resource-intensive. The warning should inform why the SQL could be dangeroues to execute.
If the NQL can't be interpreted then there is a semantic error and you should explain the reason for it.
If the SQL can be generated is should be placed in the code tag.

NQL: {input}

Return the result in the following format:
<code></code>
<semanticerror></semanticerror>
<assumptions></assumptions>
<warning></warning>
"""


# NOTE: Can't get the approach of using a semanticerror tag to work with this template. Likely too much noice. 
# If the EDIT_INSTRUCTION is non-sensical then the LLM will often return the SQL as is which is then handled as a non diff in the UI. 
_EDIT = """Act as an {dialect} SQL expert. Use the EDIT_INSTRUCTION below and modify the SQL using the following metadata: {metadata}.
Use lower() and LIKE '%%' unless you are sure about how to match the data.

SQL: {sql}
EDIT_INSTRUCTION: {input}

Always list any assumptions not covered by the supplied metadata.
Always warn if the generated SQL modifies or deletes data. The warning should inform why the SQL could be dangeroues to execute.
Only return any SQL if you have modified it based on the EDIT_INSTRUCTION in wrapped in <code>.

Return the result in the following format:
<code></code>
<assumptions></assumptions>
<warning></warning>
"""

_SUMMARIZE = """Act as an {dialect} SQL expert. Based on the input Summarize the SQL using the following metadata: {metadata}.
Explain in natural language using non technical terms, what this query does: {sql}.
"""

_OPTIMIZE = """Act as an {dialect} SQL expert.
Optimize this SQL query and explain the improvement if any. Only optimize in a way so that the result of the query remains the same.
Use the following metadata: {metadata}.

SQL: {sql}

Always explain the optimization or suggest alternative options if any. The explanation should be wrapped in an <explain> tag but should not contain SQL.
If the SQL can't be interpreted then there is a sqlerror and you should explain the reason for it.
If the SQL can't be optimized then shortly explain alternative options if any.
If the SQL can be optimized is should be placed in the code tag. 

Return the result in the following format:
<code></code>
<sqlerror></sqlerror>
<explain></explain>
"""

_FIX = """Act as an {dialect} SQL expert.
Try to fix this syntactically broken sql query using the following metadata: {metadata}. 

SQL: {sql}

Do not optimize and only make the minimal modifcation needed to create a valid query.

If the provided SQL is nonsensical then return an appropriate message in a <sqlerror> tag.
If you you can identify and fix the problematic syntax then wrap the corrected code in a <code> tag and add a 
short explaination in an <explain> tag with a closing </explain>.

Return the result in the following format:
<code></code>
<sqlerror></sqlerror>
<explain></explain>
"""


def _code_assumptions_parser(response: str) -> SQLResponse:
    return SQLResponse(
        sql=extract_tag_content('code', response),
        assumptions=extract_tag_content('assumptions', response),
        warning=extract_tag_content('warning', response),
        semanticerror=extract_tag_content('semanticerror', response),
    )


def _code_explain_parser(response: str) -> SQLResponse:
    return SQLResponse(
        sql=extract_tag_content('code', response),
        explain=extract_tag_content('explain', response),
        warning=extract_tag_content('warning', response),
        sqlerror=extract_tag_content('sqlerror', response),
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


class GPTModel(BaseModel):
    def __init__(self, task_type: TaskType):
        super().__init__(get_task(_TASKS, task_type))
