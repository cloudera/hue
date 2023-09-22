from dataclasses import dataclass
from typing import Optional

@dataclass
class SQLResponse:
    sql: Optional[str] = None
    assumptions: Optional[str] = None
    explain: Optional[str] = None
    summary: Optional[str] = None
    warning: Optional[str] = None
    semanticerror: Optional[str] = None
    sqlerror: Optional[str] = None
