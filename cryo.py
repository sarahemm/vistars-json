"""Data extraction for Vistars Cryogenics (lhc2.png) page."""

from typing import ClassVar
from decimal import Decimal, InvalidOperation
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
from vistars import (
    Vistars,
    VistarsException,
    VistarsValidationError,
)
from ocr import ocr
from color import Color
from utils import img_differs, fold_check, bad_time


class Cryo(Vistars):
    """Cryo status from lhc2.png"""

    image: Image.Image
    old_img: Image.Image
    time: datetime
    max_temps: list[Decimal]
    lost_count: int
    state: list[list[int]]
    _modules: ClassVar[list[int]] = [10, 6, 4, 8, 8, 4, 6, 10, 8, 8, 3]

    def __init__(self) -> None:
        super().__init__()
        self.image = Image.new("RGB", (1024, 768))
        self.old_img = self.image
        self.time = bad_time
        self.max_temps = []
        self.lost_count = -1
        self.state = []

    def load(self) -> None:
        """Update cryo data"""
        self.old_img = self.image
        self.image = super().download("2")
        self.time = self.read_time()
        self.check_state()
        self.check_temps()

    def read_time(self) -> datetime:
        """Parse time from the header. The space after the year is too narrow
        during 2024 for ocr() to see, because of the 10px wide 4.
        """
        box: tuple[int, int, int, int] = (848, 8, 1020, 19)
        time_str: str = ocr(self.image.crop(box))
        time_fmt: str = "%d-%m-%Y %H:%M:%S"
        if len(time_str) == 18:
            time_fmt = "%d-%m-%Y%H:%M:%S"
        try:
            dt: datetime = datetime.strptime(time_str, time_fmt)
        except ValueError as err:
            self.image.save("cryo-time-error.png")
            raise VistarsValidationError("Cryo: Time parsing failed.") from err
        return fold_check(dt.replace(tzinfo=ZoneInfo("Europe/Paris")))

    def check_state(self) -> None:
        """Run state scan if the cryo conditions have changed."""
        box: tuple[int, int, int, int] = (65, 86, 1017, 486)
        state_img: Image.Image = self.image.crop(box)
        if img_differs(state_img, self.old_img.crop(box)):
            self._scan_state(state_img)

    def _scan_state(self, state_img: Image.Image) -> None:
        """Check whether cryo state is all green/red.
        If not, proceed to scan per sector.
        """
        colors: tuple[tuple[int, int, int], ...]
        try:
            colors = tuple(zip(*state_img.getcolors(maxcolors=5)))[1]
        except TypeError as err:
            raise VistarsException from err
        if len(colors) == 1:
            raise VistarsException("Unexpected cryo state")
        if len(colors) == 2:
            if colors[0] == Color.GREEN:
                self.lost_count = 0
                self.state = []
                for i in self._modules:
                    self.state.append([0] * i)
            elif colors[0] == Color.RED:
                self.lost_count = 75
                self.state = []
                for i in self._modules:
                    self.state.append([1] * i)
            else:
                raise VistarsException(
                    f"Unexpected colour during cryo state check: {colors}"
                )
        else:
            self.lost_count = 0
            self._scan_sector(state_img)
        return None

    def _scan_sector(self, state_img: Image.Image) -> None:
        """Scan each sector line and 60A, RF, EXP for lost cryo conditions.
        If they're not full green or red, scan individual cryomodules.
        """
        y: int
        s: list[list[int]] = []
        i: int = -1
        sector_img: Image.Image
        colors: tuple[tuple[int, int, int], ...]
        for y in range(3, 354, 35):
            s.append([])
            i += 1
            if i >= 8:
                y += 15
            sector_img = state_img.crop((0, y, 952, y + 30))
            sector_img = sector_img.crop(sector_img.getbbox())
            try:
                colors = tuple(zip(*sector_img.getcolors(maxcolors=4)))[1]
            except TypeError as err:
                raise VistarsException("Too many colors!") from err
            if len(colors) == 2:
                if colors[0] == Color.BLACK:
                    colors = colors[::-1]
                if colors[0] == Color.GREEN:
                    s[-1] = [0] * self._modules[i]
                    continue
                if colors[0] == Color.RED:
                    self.lost_count += self._modules[i]
                    s[-1] = [1] * self._modules[i]
                    continue
            s[-1] = self._scan_module(sector_img)
        self.state = s

    def _scan_module(self, sector_img: Image.Image) -> list[int]:
        """Scan individual modules for lost cryo conditions."""
        x: int
        mod_width: int
        cryomodule: Image.Image
        colors: tuple[tuple[int, int, int], ...]
        m: list[int] = []
        lost: int
        mod_width = 95
        lost = 0
        if sector_img.width % 160 == 0:
            mod_width = 160
        for x in range(0, sector_img.width, mod_width):
            cryomodule = sector_img.crop((x, 0, x + mod_width, 30))
            try:
                colors = tuple(zip(*cryomodule.getcolors(maxcolors=2)))[1]
            except TypeError as err:
                raise VistarsException from err
            if len(colors) == 1:
                print("Cryomodule colour not as expected.")
                break
            if colors[0] == Color.BLACK:
                colors = colors[::-1]
            if colors[0] not in (Color.GREEN, Color.ORANGE, Color.RED, Color.BLUE):
                print("Cryomodule unexpected colour.")
            if colors[0] == Color.GREEN:
                m.append(0)
            elif colors[0] == Color.ORANGE:
                m.append(2)
                lost += 1
            elif colors[0] == Color.RED:
                m.append(1)
                lost += 1
            elif colors[0] == Color.BLUE:
                m.append(3)
                lost += 1
        self.lost_count += lost
        return m

    def check_temps(self) -> None:
        """Read temperature data if they have changed."""
        box: tuple[int, int, int, int] = (840, 534, 968, 710)
        temp_img: Image.Image = self.image.crop(box)
        if img_differs(temp_img, self.old_img.crop(box)):
            self.extract_temps(temp_img)

    def extract_temps(self, temp_img: Image.Image) -> None:
        """Cryo max temperatures per sector in Kelvin"""
        temps: list[Decimal]
        i: int
        temp_line: str
        sector: str
        temp_k: str
        temp_img = temp_img.convert(mode="1", dither=Image.Dither.NONE)
        temps = []
        for i in range(10, temp_img.height, 22):
            temp_line = ocr(temp_img.crop((0, i, 128, i + 12)))
            if temp_line == '':
                raise VistarsValidationError("Cryo temperatures could not be read")
            if temp_line[0] == "S" and temp_line[1:2].isdecimal():
                sector, temp_k = temp_line.split()
                sector = sector.lower()
                try:
                    temps.append(Decimal(temp_k))
                except InvalidOperation as err:
                    raise VistarsValidationError("Temperature not a decimal") from err
        if len(temps) == 8:
            self.max_temps = temps
