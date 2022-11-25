from dataclasses import dataclass
from typing import List

@dataclass
class HSVRange:
    lower: List[int]
    upper: List[int]

@dataclass
class iVec2:
    x: int
    y: int