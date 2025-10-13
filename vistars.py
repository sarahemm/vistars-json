from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import ClassVar
import httpx
from PIL import Image, UnidentifiedImageError


class VistarsException(Exception):
    """Generic exception class"""


class VistarsDownloadError(VistarsException):
    """Exception for lhc download errors"""


class VistarsValidationError(VistarsException):
    """Exception for errors in data validation"""


class Vistars:
    """Setup State"""

    _session: ClassVar[httpx.Client] = httpx.Client(http2=True, timeout=12.1)
    _url_path: ClassVar[str] = ""
    last_modified: datetime

    def __init__(self) -> None:
        url: str
        response: httpx.Response
        line: str
        if Vistars._url_path:
            return None
        url = "https://op-webtools.web.cern.ch/vistar/"
        response = httpx.get(url, headers={"Connection": "close"}, timeout=12.1)
        if "text/html" in response.headers["Content-Type"]:
            for line in response.text.split('"'):
                if "lhc1.png" in line:
                    Vistars._url_path = line.replace("\\", "").removesuffix("lhc1.png")
                    return None
        return None

    def download(self, page: str) -> Image.Image:
        """Download State"""
        response: httpx.Response
        lm_header: str
        lm_format: str
        lm_time: datetime
        img: Image.Image
        if page not in ("1", "2", "3", "config"):
            raise ValueError(f"lhc{page}.png is not a valid page")
        try:
            response = Vistars._session.get(f"{self._url_path}lhc{page}.png")
        except httpx.RequestError as err:
            raise VistarsDownloadError(f"Unable to download lhc{page}.png") from err
        if response.is_success:
            lm_header = response.headers["Last-Modified"]
            lm_format = "%a, %d %b %Y %H:%M:%S %Z"
            try:
                lm_time = datetime.strptime(lm_header, lm_format)
            except ValueError as err:
                raise VistarsDownloadError("HTTP header time parsing failed") from err
            self.last_modified = lm_time.replace(tzinfo=ZoneInfo("GMT"))
            if (
                response.headers["Content-Type"] == "image/png"
                and int(response.headers["Content-Length"]) > 256
            ):
                try:
                    img = Image.open(BytesIO(response.content))
                except UnidentifiedImageError as err:
                    raise VistarsDownloadError("Pillow could not read image.") from err
                if img.size == (1024, 768):
                    return img
                raise VistarsDownloadError(f"Unexpected size for lhc{page}.png")
            raise VistarsDownloadError("Bad download: Server sent unusable data.")
        raise VistarsDownloadError(
            f"HTTP error. Got status code: {response.status_code}"
        )
