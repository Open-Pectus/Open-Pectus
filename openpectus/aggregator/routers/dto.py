from typing import List

from pydantic import BaseModel


class MethodLine(BaseModel):
    id: str
    content: str

class Method(BaseModel):
    lines: List[MethodLine]
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]
