from dataclasses import dataclass
from typing import List

@dataclass
class HSVRange:
    lower: List[int]
    upper: List[int]


@dataclass
class drumCircle:
    centre: List[int]
    radius: int
    notation: str
    name: str

#TODO make nicer dataclass for locations (centre[0] -> centre.x)



