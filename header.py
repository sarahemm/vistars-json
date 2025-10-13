"""Class for data in the lhc3 and lhcconfig headers"""

from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
from vistars import VistarsValidationError
from ocr import ocr
from utils import fold_check, bad_time


class Header:
    """Data from the lhc3 and lhcconfig headers"""

    time: datetime
    fill_nr: int
    energy: int
    ions: bool
    intensity: tuple[str, str]

    def __init__(self) -> None:
        self.time = bad_time
        self.fill_nr = -1
        self.energy = -1
        self.ions = False
        self.intensity = ("0.00e-00", "0.00e-00")

    def load(self, image: Image.Image) -> None:
        box: tuple[int, int, int, int] = (4, 10, 1020, 30)
        header_img: Image.Image = image.crop(box)
        self._header_fetcher(header_img)

    def _header_fetcher(self, img: Image.Image) -> None:
        """Parse and validate header data for lhc3 and lhcconfig"""
        header_img: Image.Image
        text: list[str]
        header_dt: datetime
        lut: list[int] = [0] * 32 + [255] * 224
        header_img = img.convert(mode="L", dither=Image.Dither.NONE).point(lut, mode="1")
        text = ocr(header_img).split()
        if not "".join(text).isascii() or len(text) < 12:
            raise VistarsValidationError(f"Header ocr failure: {text}")
        if text[7] == 'Z':
            self.ions = True
            del text[7]
        else:
            self.ions = False
        try:
            header_dt = datetime.strptime(f"{text[0]} {text[1]}", "%d-%b-%Y %H:%M:%S")
        except ValueError as err:
            raise VistarsValidationError(f"Header datetime failure: {text}") from err
        header_dt = fold_check(header_dt.replace(tzinfo=ZoneInfo("Europe/Paris")))
        if text[4].isdecimal() and text[6].isdecimal():
            self.time = header_dt
            self.fill_nr = int(text[4])
            self.energy = int(text[6])
            self.intensity = (text[9], text[11])
        else:
            raise VistarsValidationError(f"Header fill/energy error: {text}")
