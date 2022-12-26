from dataclasses import dataclass
from typing import List

@dataclass
class HSVRange:
    lower: List[int]
    upper: List[int]

