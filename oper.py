from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from PIL import Image
from vistars import Vistars, VistarsException, VistarsValidationError
from ocr import ocr
from header import Header
from color import Color
from utils import img_differs


@dataclass(frozen=True)
class Experiment:
    """Holds lumi data and flag status for the 4 main experiments"""

    status: str = ""
    inst_lumi: Decimal | None = None
    bran_lumi: Decimal | None = None
    fill_lumi: Decimal | None = None
    b1_bkgd: Decimal | None = None
    b2_bkgd: Decimal | None = None


class Velo:
    """Status of the LHCb VErtex LOcator and SMOG"""

    pos: str
    gap: Decimal
    smog: str

    def __init__(self) -> None:
        self.pos = ""
        self.gap = Decimal("NaN")
        self.smog = ""

    def load(self, image: Image.Image) -> None:
        """Get LHCb VELO Position"""
        if(image.getpixel((144, 312)) == Color.BLUE):
            # VELO/SMOG is not in service, no data is available about it beyond that
            self.pos = "N/A"
            self.smog = "N/A"
            return

        box: tuple[int, int, int, int] = (219, 318, 307, 330)
        gap_str: str
        gap_str = ocr(image.crop(box))
        if not gap_str.isascii():
            image.save("velogap-error.png")
            raise VistarsException("Velo gap OCR error")
        if not (gap_str[-2:] == "mm"):
            raise VistarsException(f"VELO gap unit not as expected: {gap_str}")
        try:
            self.gap = Decimal(gap_str[:-2])
        except InvalidOperation as err:
            self.gap = Decimal("NaN")
            raise VistarsException(f"VELO gap not a number: {gap_str}") from err
        match image.getpixel((144, 312)):
            case Color.RED:
                self.pos = "OUT"
            case Color.GREEN:
                self.pos = "IN"
            case _:
                image.save("veloflag-error.png")
                raise VistarsException("Unexpected VELO Flag colour")
        match image.getpixel((424, 312)):
            case Color.WHITE:
                self.smog = "OFF"
            case Color.YELLOW:
                self.smog = "ON"
            case _:
                self.image.save("smogflag-error.png")
                raise VistarsException("Unknown SMOG Flag colour")


class Oper(Vistars):
    """Test"""

    image: Image.Image
    old_img: Image.Image
    header: Header
    atlas: Experiment
    alice: Experiment
    cms: Experiment
    lhcb: Experiment
    totem: str
    bcm: str
    velo: Velo

    def __init__(self) -> None:
        super().__init__()
        self.image = Image.new("RGB", (1024, 768))
        self.old_img = self.image
        self.header = Header()
        self.atlas = Experiment()
        self.alice = Experiment()
        self.cms = Experiment()
        self.lhcb = Experiment()
        self.totem = ""
        self.bcm = ""
        self.velo = Velo()

    def load(self) -> None:
        """Retrieve data from lhc3.png"""
        exp: str
        self.old_img = self.image
        self.image = super().download("3")
        self.header.load(self.image)
        if self.exp_data_changed():
            for exp in ("ATLAS", "ALICE", "CMS", "LHCb"):
                setattr(
                    self,
                    exp.lower(),
                    Experiment(self.read_status(exp), *self.extract_lumi(exp)),
                )
        if self.velo_totem_changed():
            self.velo.load(self.image)
            self.bcm = self.read_status("BCM")
            self.totem = self.read_status("TOTEM")

    def exp_data_changed(self) -> bool:
        """Check data box for changes"""
        box: tuple[int, int, int, int] = (323, 56, 995, 248)
        return img_differs(self.image.crop(box), self.old_img.crop(box))

    def velo_totem_changed(self) -> bool:
        """Check velo & totem line for changes"""
        box: tuple[int, int, int, int] = (4, 309, 980, 341)
        return img_differs(self.image.crop(box), self.old_img.crop(box))

    def read_status(self, exp: str) -> str:
        """Read status flag of any of the 4 main experiments or TOTEM.
        Some flags are 99px wide, others are 100. TOTEM has 85px width.
        Check full width to be able to parse when the text moves around.
        """
        exp_pixel: dict[str, int] = {
            "ATLAS": 335,
            "ALICE": 518,
            "CMS": 700,
            "LHCb": 883,
            "BCM": 593,
            "TOTEM": 882,
        }
        y: int
        x: int
        flag: Image.Image
        c_count: tuple[int, ...]
        colors: tuple[tuple[int, int, int], ...]
        y = 61
        x = exp_pixel[exp]
        if exp in ("BCM", "TOTEM"):
            y = 310
        flag = self.image.crop((x, y, x + 128, y + 28))
        flag = flag.crop(flag.getbbox())
        try:
            c_count, colors = zip(
                *flag.getcolors(maxcolors=2)
            )
        except TypeError as err:
            raise VistarsException("Unexpected Exp Flag colours") from err
        if colors[0] in (Color.BLACK, Color.D_GREY):
            c_count = c_count[::-1]
            colors = colors[::-1]
        match colors[0]:
            case Color.GREEN:
                match c_count[1]:
                    case 180:
                        # Text is STAN...
                        return "STANDBY"
                    case 249:
                        return "PHYSICS"
                    case 289:
                        return "STANDBY"
                    case 410:
                        # For BCM only
                        return "OPERATIONAL"
                    case _:
                        self.image.save(f"greenflag-{exp}.png")
                        raise VistarsException(f"Unknown green Exp Flag text {c_count[1]}")
            case Color.RED:
                # Only seen for BCM
                match c_count[1]:
                    case 267:
                        return "MASKED"
                    case _:
                        self.image.save(f"redflag-{exp}.png")
                        raise VistarsException(f"Unknown red Exp Flag text {c_count[1]}")
            case Color.L_GREY:
                match c_count[1]:
                    case 269:
                        return "COSMICS"
                    case 300:
                        return "Updating"
                    case 329:
                        return "NOT_READY"
                    case _:
                        self.image.save(f"greyflag-{exp}.png")
                        raise VistarsException("Unknown light grey Exp Flag")
            case Color.YELLOW:
                return "CALIBRATION"
            case Color.BLUE:
                return "No Info"
            case _:
                self.image.save(f"unknownflag-{exp}.png")
                raise VistarsException(f"Unknown Exp Flag colour {colors}")

    def extract_lumi(self, exp: str) -> list[Decimal | None]:
        """Parse and validate the 5 float data from lhc3
        Beta* and crossing angle are available from lhcconfig
        """
        x: int
        y: int
        exp_x: dict[str, int] = {
            "ATLAS": 315,
            "ALICE": 498,
            "CMS": 680,
            "LHCb": 863,
        }
        text: str
        data: list[Decimal | None]
        x = exp_x[exp]
        data = []
        for y in range(99, 224, 31):
            text = ocr(self.image.crop((x, y, x + 140, y + 12)))
            if not text.isascii():
                self.image.save("lumi-ocr.png")
                raise VistarsException("OCR Error while reading lumi")
            try:
                data.append(Decimal(text))
            except InvalidOperation as err:
                if text in ("", "-", ".") or "..." in text or "  " in text:
                    data.append(None)
                else:
                    self.image.save("badfloat.png")
                    raise VistarsValidationError("Lhc3: failed to convert to float")
        return data
