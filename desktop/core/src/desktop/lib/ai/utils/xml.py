import re
from typing import List, Dict

def extract_tag_content(tag: str, text: str) -> str:
    matches = re.findall(f'<{tag}>(.*?)</{tag}>', text, flags=re.DOTALL)
    return matches[0] if len(matches) > 0 else ''
