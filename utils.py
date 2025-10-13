import time
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from PIL import Image, ImageChops


bad_time = datetime(2008, 9, 19, 11, 18, 37, tzinfo=ZoneInfo("Europe/Paris"))

def now() -> datetime:
    """Return current time in the LHC timezone."""
    return datetime.now(tz=ZoneInfo("Europe/Paris"))


def fold_check(dt: datetime) -> datetime:
    """Transitioning from summer to winter time creates ambiguity in
    vistar's mostly naive times. Applying the Europe/Paris timezone to
    such times will assume summer time, which could be incorrect.
    Time can only be disambiguated during the repeated interval, by
    checking if it appears to be ahead of current time with fold=1.
    """
    if datetime.strftime(dt, "%w%m%H") == "01002" and int(datetime.strftime(dt, "%d")) > 24:
        if time.time() - dt.replace(fold=1).timestamp() >= 0:
            return dt.replace(fold=1)
    return dt


def img_differs(im1: Image.Image, im2: Image.Image) -> bool:
    """Returns True if there is a difference between two images."""
    return ImageChops.difference(im1, im2).getbbox() is not None


def save(img: Image.Image, name: str) -> None:
    """Save a timestamped copy in case of errors"""
    when: str = datetime.strftime(now(), "%m%d%H%M")
    img.save(f"{name}_error{when}.png")
