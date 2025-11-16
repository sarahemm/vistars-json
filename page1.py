"""Data extraction for Vistars Page 1 (lhc1.png) page."""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import ClassVar
from dataclasses import dataclass
import logging
from PIL import Image
from vistars import Vistars, VistarsValidationError, VistarsException
from ocr import ocr
from ocr_pm import ocr_pm
from color import Color
from utils import fold_check, img_differs, bad_time


class Comments:
    """Page 1 comments, datetime and text content"""

    _error_file: ClassVar[Image.Image] = Image.open("error_comments.png")
    image: Image.Image
    time: datetime
    text: str

    def __init__(self) -> None:
        self.image = Image.new("RGB", (509, 173))
        self.time = bad_time
        self.text = ""

    def read(self, img: Image.Image) -> None:
        """Read and validate comments. Ignore error:comments"""
        error_crop: Image.Image
        txt: str
        error_crop = img.crop((170, 31, 340, 46))
        if not img_differs(Comments._error_file, error_crop):
            logging.warning("Page1: Error: Comments")
            return None
        txt = ocr(rgb_to_bw(img))
        if txt[32:] == "Error: Comments":
            return None
        self.image = img
        if len(txt) > 31 and txt[9] == "(" and txt[30] == ")":
            self._dt_parse(txt[10:30])
            self.text = txt[32:]
        else:
            raise VistarsValidationError("Failed to parse comments")
        return None

    def _dt_parse(self, time_str: str) -> None:
        dt: datetime
        try:
            dt = datetime.strptime(time_str, "%d-%b-%Y %H:%M:%S")
        except ValueError as err:
            raise VistarsValidationError("Comments time conversion failed") from err
        self.time = fold_check(dt.replace(tzinfo=ZoneInfo("Europe/Paris")))


@dataclass(frozen=True)
class Flags:
    """BIS status and SMP flags"""

    link_status: tuple[bool, bool] = (False, False)
    global_beam_permit: tuple[bool, bool] = (False, False)
    setup_beam: tuple[bool, bool] = (False, False)
    beam_presence: tuple[bool, bool] = (False, False)
    moveable_devices: tuple[bool, bool] = (False, False)
    stable_beams: tuple[bool, bool] = (False, False)


class Postmortem:
    """Page 1 Post Mortem information"""

    _rows_file: ClassVar[Image.Image] = Image.open("pm_rows.png")
    image: Image.Image
    id: datetime
    category: str | None
    classification: str | None
    analysis: str | None
    comment: str | None

    def __init__(self) -> None:
        self.image = Image.new("RGB", (1000, 118))
        self.id = bad_time
        self.category = None
        self.classification = None
        self.analysis = None
        self.comment = None

    def read(self, img: Image.Image) -> None:
        """The last row jumps down a pixel if there's a comment"""
        text: list[str]
        if img_differs(self._rows_file, img.crop((0, 0, 224, 96))):
            raise VistarsValidationError("Unexpected postmortem box")
        text = ocr_pm(img.crop((224, 0, img.width, img.height))).split("\n")
        if len(text) not in (4, 5):
            raise VistarsValidationError("Postmortem unexpected line count")
        self._dt_parse(text[0])
        self.category = text[1]
        self.classification = text[2]
        self.analysis = text[3]
        if len(text) == 5:
            self.comment = text[4]
        else:
            self.comment = None
        self.image = img

    def _dt_parse(self, time_str: str) -> None:
        dt: datetime
        try:
            dt = datetime.strptime(time_str[4:].replace('CEST', '+0200').replace('CET', '+0100'), "%b %d %H:%M:%S %z %Y")
        except ValueError as err:
            raise VistarsValidationError(time_str) from err
        self.id = dt.astimezone(ZoneInfo("Europe/Paris"))


class Page1(Vistars):
    """Page 1 State"""

    image: Image.Image
    old_img: Image.Image
    fill_nr: int
    energy: int
    time: datetime
    comments: Comments
    flags: Flags
    tsb: str
    postmortem: Postmortem

    def __init__(self) -> None:
        super().__init__()
        self.image = Image.new("RGB", (1024, 768))
        self.old_img = self.image
        self.fill_nr = -1
        self.energy = -1
        self.time = bad_time
        self.comments = Comments()
        self.flags = Flags()
        self.tsb = "PT0S"
        self.postmortem = Postmortem()

    def load(self) -> None:
        """Download and extract Page 1 data"""
        self.old_img = self.image
        self.image = super().download("1")
        self.extract_fill_nr()
        self.extract_energy()
        self.extract_time()
        self.extract_comments()
        self.extract_flags()
        if self.flags.beam_presence[0] and self.flags.beam_presence[1]:
            if self.flags.stable_beams[0] and self.flags.stable_beams[1]:
                self.extract_tsb()
            elif self.flags.setup_beam[0] and self.tsb != "PT0S":
                self.tsb = "PT0S"
        elif self.image.getpixel((15, 170)) == Color.YELLOW:
            self.extract_pm()

    def extract_fill_nr(self) -> None:
        """Read fill number from the header"""
        box: tuple[int, int, int, int] = (248, 11, 320, 21)
        self.fill_nr = self._extract_int(box, min_length=4)

    def extract_energy(self) -> None:
        """Read machine energy from the header"""
        box: tuple[int, int, int, int] = (432, 11, 572, 21)
        self.energy = self._extract_int(box, max_length=4)

    def extract_time(self) -> None:
        """Read, validate and convert time from the header"""
        box: tuple[int, int, int, int] = (820, 11, 1020, 21)
        time_str: str
        dt: datetime
        time_str = ocr(self.image.crop(box))
        if not time_str.isascii():
            raise VistarsValidationError("Page1: Time ocr failed.")
        if len(time_str) == 16 and time_str[8] != " ":
            time_str = f"{time_str[:8]} {time_str[8:]}"
        try:
            dt = datetime.strptime(time_str, "%d-%m-%y %H:%M:%S")
        except ValueError as err:
            raise VistarsValidationError("Page1: Time parsing failed.") from err
        self.time = fold_check(dt.replace(tzinfo=ZoneInfo("Europe/Paris")))

    def extract_comments(self) -> None:
        """Get comments if they have changed"""
        new_comments: Image.Image
        box: tuple[int, int, int, int] = (2, 553, 511, 726)
        new_comments = self.image.crop(box)
        if img_differs(new_comments, self.old_img.crop(box)):
            self.comments.read(new_comments)

    def extract_flags(self) -> None:
        """Parse flags if they have changed"""
        new_flags: Image.Image
        box: tuple[int, int, int, int] = (865, 554, 1004, 724)
        new_flags = self.image.crop(box)
        if img_differs(new_flags, self.old_img.crop(box)):
            self._flags_fetcher(new_flags)

    def extract_tsb(self) -> None:
        """Read stable beam duration from the header"""
        box: tuple[int, int, int, int] = (676, 11, 776, 21)
        tsb_str: str
        hrs: int
        mins: int
        secs: int
        # during the 2025 ion season t(SB) gained a blue background
        # we convert to 1-bit to eliminate this and make the OCR work
        tsb_str = ocr(self.image.crop(box).convert(mode="1", dither=Image.Dither.NONE))
        if len(tsb_str) == 8 and tsb_str.isascii():
            try:
                hrs = int(tsb_str[0:2])
                mins = int(tsb_str[3:5])
                secs = int(tsb_str[6:8])
            except ValueError as err:
                raise VistarsValidationError(
                    f"Failed conversion of tsb: {tsb_str}."
                ) from err
            self.tsb = f"PT{hrs}H{mins}M{secs}S"
        else:
            raise VistarsValidationError(f"Failed parsing of tsb: {tsb_str}.")

    def extract_pm(self) -> None:
        """Run OCR on Post Mortem text block if it has changed"""
        box: tuple[int, int, int, int] = (12, 180, 1012, 298)
        pm_img: Image.Image = self.image.crop(box)
        if img_differs(pm_img, self.old_img.crop(box)):
            self.postmortem.read(pm_img)

    def _extract_int(
        self, box: tuple[int, int, int, int], min_length: int = 1, max_length: int = 5
    ) -> int:
        """Read, validate and convert a number from the header"""
        number_str: str
        number_str = ocr(self.image.crop(box)).rstrip()
        if not len(number_str) in range(min_length, max_length + 1):
            raise VistarsValidationError(
                f"Page1: Header contains number of unexpected length: {number_str}"
            )
        if number_str.isascii() and number_str.isdecimal():
            try:
                return int(number_str)
            except ValueError:
                raise VistarsValidationError(
                    f"Page1: Integer conversion failed from str: {number_str}"
                ) from ValueError
        else:
            raise VistarsValidationError(
                f"Page1: Integer parsing failed from str: {number_str}"
            )

    def _flags_fetcher(self, img: Image.Image) -> None:
        """Parse BIS status and SMP flags"""
        y: int
        b1_color: tuple[int, int, int]
        b2_color: tuple[int, int, int]
        flag_tmp: list[tuple[bool, bool]]
        flag_tmp = []
        for y in range(14, img.height, 29):
            b1_color = img.getpixel((35, y))
            b2_color = img.getpixel((107, y))
            for color in (b1_color, b2_color):
                if color not in (Color.RED, Color.GREEN):
                    raise VistarsException("Unexpected beam flag colour.")
            flag_tmp.append(((b1_color == Color.GREEN), (b2_color == Color.GREEN)))
        if len(flag_tmp) == 6:
            self.flags = Flags(*flag_tmp)


def rgb_to_bw(image: Image.Image) -> Image.Image:
    """Pillow's convert to mode='1' (one bit b&w) loses all red and blue.
    Convert to mode='L' (grayscale) (Image.point() can't map from RGB to BW)
    and then map all but the darkest greys to white.
    """
    lut: list[int] = [0] * 16 + [255] * 240
    return image.convert(mode="L", dither=Image.Dither.NONE).point(lut, mode="1")
