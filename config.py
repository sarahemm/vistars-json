from collections import namedtuple
from datetime import datetime
from PIL import Image
from vistars import Vistars, VistarsValidationError, VistarsException
from ocr import ocr
from header import Header
from utils import img_differs


class Config(Vistars):
    """Several data points from lhcconfig.png"""

    image: Image.Image
    old_img: Image.Image
    header: Header
    accmode: str
    beammode: str
    fillscheme: str
    hypercycle: str
    atlas: dict[str, str | None]
    alice: dict[str, str | None]
    cms: dict[str, str | None]
    lhcb: dict[str, str | None]

    def __init__(self) -> None:
        super().__init__()
        self.image = Image.new("RGB", (1024, 768))
        self.old_img = self.image
        self.header = Header()
        self.accmode = ""
        self.beammode = ""
        self.fillscheme = ""
        self.hypercycle = ""
        self.atlas = dict(zip([""] * 6, [None] * 6))
        self.alice = dict(zip([""] * 6, [None] * 6))
        self.cms = dict(zip([""] * 6, [None] * 6))
        self.lhcb = dict(zip([""] * 6, [None] * 6))

    def load(self) -> None:
        """Update config data"""
        data: dict[str, str | None]
        lumi: dict[str, str | None]
        self.old_img = self.image
        self.image = super().download("config")
        self.header.load(self.image)
        self.extract_modes()
        if self.data_changed():
            for exp in ("ATLAS", "ALICE", "CMS", "LHCb"):
                setattr(self, exp.lower(), self.extract_data(exp))
        return None

    def extract_modes(self) -> None:
        new_modes: Image.Image
        box: tuple[int, int, int, int] = (212, 47, 1012, 139)
        new_modes = self.image.crop(box)
        if img_differs(new_modes, self.old_img.crop(box)):
            self._modes_fetcher(new_modes)

    def _modes_fetcher(self, img: Image.Image) -> None:
        """Parse, validate and set accelerator mode, beam mode,
        fill scheme and hypercycle.
        """
        modes_img: Image.Image
        modes: list[str]
        mbox: dict[str, tuple[int, int, int, int]] = {
            "accmode": (0, 0, 362, 20),
            "beammode": (400, 0, 800, 20),
            "fillscheme": (100, 36, 800, 56),
            "hypercycle": (100, 72, 800, 92),
        }
        lut: list[int] = [0] * 16 + [255] * 239 + [0]
        modes_img = img.convert(mode="L", dither=Image.Dither.NONE).point(lut, mode="1")
        modes = []
        modes.append(ocr(modes_img.crop(mbox["accmode"])))
        modes.append(ocr(modes_img.crop(mbox["beammode"])))
        modes.append(ocr(modes_img.crop(mbox["fillscheme"])))
        modes.append(ocr(modes_img.crop(mbox["hypercycle"])))
        if not "".join(modes).isascii():
            raise VistarsValidationError(f"OCR Failure to parse modes: {modes}")
        self.accmode = modes[0]
        self.beammode = modes[1]
        self.fillscheme = modes[2]
        self.hypercycle = modes[3]
        return None

    def data_changed(self) -> bool:
        box: tuple[int, int, int, int] = (312, 184, 1024, 593)
        return img_differs(self.old_img.crop(box), self.image.crop(box))

    def extract_data(self, exp: str) -> namedtuple:
        """Parse and validate experiment data from lhcconfig"""
        x: int
        y: int
        exp_x: dict[str, int] = {
            "ATLAS": 312,
            "ALICE": 490,
            "CMS": 669,
            "LHCb": 846,
        }
        row_names: tuple[str, ...] = (
            "beta_star",
            "cross_angle",
            "spectro_angle",
            "separation",
            "coll_per_turn",
            "delta_t",
            "size_xy",
            "size_z",
            "centroid_xy",
            "centroid_z",
            "tilt",
        )
        text: str
        data: list[str | None]
        data = []
        x = exp_x[exp]
        for y in range(184, 329, 36):
            if y == 256 and exp in ("ATLAS", "CMS"):
                data.append(None)
                continue
            text = ocr(self.image.crop((x, y, x + 176, y + 20)))
            if not text.isascii():
                raise VistarsException(text)
            data.append(text)
        for y in range(393, 574, 36):
            text = ocr(self.image.crop((x, y, x + 176, y + 20)))
            if not text.isascii():
                raise VistarsException(text)
            if text == "" and y == 573 and data[-1] == "-1000.0":
                text = "-1000.00,-1000.00"
            data.append(text)
            break # Skip lumi data for now (deformed "6")
        if len(data) != 6:
            raise VistarsValidationError("Non-conforming config data length")
        return dict(zip(row_names, data))
