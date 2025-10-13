"""Mapping for the colours used in Vistars"""

from typing import ClassVar

class Color:
    """Simple colour mapping"""

    BLACK: ClassVar[tuple[int, int, int]] = (0, 0, 0)
    RED: ClassVar[tuple[int, int, int]] = (255, 0, 0)
    GREEN: ClassVar[tuple[int, int, int]] = (0, 255, 0)
    BLUE: ClassVar[tuple[int, int, int]] = (0, 0, 255)
    ORANGE: ClassVar[tuple[int, int, int]] = (255, 202, 0)
    YELLOW: ClassVar[tuple[int, int, int]] = (255, 255, 0)
    D_GREY: ClassVar[tuple[int, int, int]] = (49, 48, 49)
    L_GREY: ClassVar[tuple[int, int, int]] = (238, 238, 238)
    WHITE: ClassVar[tuple[int, int, int]] = (255, 255, 255)
