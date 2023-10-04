from ..lib.task import Task, TaskType, get_task
from ..lib.base_model import BaseModel
from ..utils.xml import extract_tag_content
from ..types import SQLResponse

_GENERATE = """
YOUR MAIN GOAL:
Act as an {dialect} SQL expert and Translate the NQL statement into SQL. Return the SQL wrapped in a <code> tag.
Use lower() and LIKE '%%' unless you are sure about how to match the data.

YOUR ADDITIONAL GOALS:
List any assumptions not covered by the supplied metadata wrapped in an <assumptions> tag.
Always inlcude a warning in a <warning> tag if the generated SQL modifies or deletes data or risk being very resource-intensive. The warning should inform why the SQL could be dangeroues to execute.
Return an error message wrapped in a <semanticerror> tag if the NQL can't be interpreted.

NQL: {input}

METADATA: {metadata}
"""

# NOTE: Can't get the approach of using a semanticerror tag to work with this template. Likely too much noice.
# If the EDIT_INSTRUCTION is non-sensical then the LLM will often return the SQL as is which is then handled as a non diff in the UI.
_EDIT= """
YOUR MAIN GOAL:
Act as an {dialect} SQL expert and modify the SQL based on the INPUT. Return the SQL wrapped in a <code> tag.
Use lower() and LIKE '%%' unless you are sure about how to match the data.

YOUR ADDITIONAL GOALS:
List any assumptions not covered by the supplied metadata wrapped in an <assumptions> tag.
Always include a warning in a <warning> tag if the generated SQL modifies or deletes data or risk being very resource-intensive. The warning should inform why the SQL could be dangeroues to execute.

SQL: {sql}

INPUT: {input}

METADATA: {metadata}
"""

_SUMMARIZE = """
SQL: {sql}

METADATA: {metadata}

Act as an {dialect} SQL expert. Explain in detail what the provided SQL query does and wrap the explation in an <explain> tag with closing </explain>.
Provide a short summary in natural language of the expected result. Wrap the summary in a <summary> tag tag with closing </summary>.

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
        summary=extract_tag_content('summary', response),
        explain=extract_tag_content('explain', response),
    )


_TASKS = {
    TaskType.GENERATE: Task(_GENERATE, _code_assumptions_parser),
    TaskType.EDIT: Task(_EDIT, _code_assumptions_parser),
    TaskType.SUMMARIZE: Task(_SUMMARIZE, _summary_parser),
    TaskType.OPTIMIZE: Task(_OPTIMIZE, _code_explain_parser),
    TaskType.FIX: Task(_FIX, _code_explain_parser)
}

class TitanModel(BaseModel):
    def get_default_name(self) -> str:
        return "amazon.titan-tg1-large"

    def get_task(self, task_type: TaskType) -> Task:
        return get_task(_TASKS, task_type)

    def build_data(self, prompt: str) -> dict:
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "stopSequences": [],
                "temperature": 0,
                "topP": 0.9
            }
        }
