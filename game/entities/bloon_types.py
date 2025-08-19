"""
Bloon types and properties
"""
from enum import Enum
from dataclasses import dataclass
from typing import Tuple
from ..constants import RED, BLUE, GREEN, YELLOW


class BloonType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"


@dataclass
class BloonProperties:
    health: int
    speed: float
    reward: int
    color: Tuple[int, int, int]
    size: int


# Bloon type properties
BLOON_PROPERTIES = {
    BloonType.RED: BloonProperties(1, 1.0, 1, RED, 15),
    BloonType.BLUE: BloonProperties(2, 1.2, 2, BLUE, 15),
    BloonType.GREEN: BloonProperties(3, 1.5, 3, GREEN, 15),
    BloonType.YELLOW: BloonProperties(4, 2.0, 4, YELLOW, 15),
}
