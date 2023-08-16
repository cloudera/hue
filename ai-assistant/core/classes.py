from dataclasses import dataclass
from typing import Optional

@dataclass
class Input:
    prompt: str
    stopping_text: Optional[str] = None

@dataclass
class Output:
    inference: str
