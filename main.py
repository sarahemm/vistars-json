import logging
from time import sleep
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from vistars import VistarsException, VistarsDownloadError
from page1 import Page1, Comments, Postmortem
from config import Config
from cryo import Cryo
from oper import Oper
from encoder import Encoder

wake_time: datetime
timeout: int = 53
to_adjust: int = 0
time_fmt: str = "%Y-%m-%dT%H:%M:%S%z"
jenc = Encoder()
dl_failed: int = 0

lhc1 = Page1()
config = Config()
lhc3 = Oper()
cryo = Cryo()

old_comment: Comments = lhc1.comments
old_pm = Postmortem = lhc1.postmortem


while True:
    try:
        lhc1.load()
        cryo.load()
        lhc3.load()
        config.load()
    except VistarsDownloadError as err:
        logging.exception("Download failed.")
        sleep(timeout + timeout * dl_failed)
        dl_failed += 1
        continue
    except VistarsException as err:
        logging.warning(err, exc_info=True)

    if "SHUTDOWN" in config.accmode:
        to_adjust = 300
    elif "NO BEAM" in config.beammode:
        to_adjust = 60
    elif "PHYSICS" in config.accmode:
        if int(config.header.intensity[0][-2:]) > 12:
            to_adjust = -24
        elif int(config.header.intensity[0][-2:]) > 10:
            to_adjust = -12

    wake_time = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        seconds=(timeout + to_adjust + 1)
    )
    dict_state = {
        "fill": lhc1.fill_nr,
        "energy": lhc1.energy,
        "ions": config.header.ions,
        "time": {
            "page1": lhc1.time.strftime(time_fmt),
            "cryo": cryo.time.strftime(time_fmt),
            "lhc3": lhc3.header.time.strftime(time_fmt),
            "config": config.header.time.strftime(time_fmt),
        },
        "comments": lhc1.comments,
        "flags": lhc1.flags,
        "tsb": lhc1.tsb,
        "postmortem": lhc1.postmortem,
        "intensity": config.header.intensity,
        "accmode": config.accmode,
        "beammode": config.beammode,
        "fillscheme": config.fillscheme,
        "hypercycle": config.hypercycle,
        "experiment": [
            {"name": "ATLAS", "operation": lhc3.atlas, "config": config.atlas},
            {"name": "ALICE", "operation": lhc3.alice, "config": config.alice},
            {"name": "CMS", "operation": lhc3.cms, "config": config.cms},
            {"name": "LHCb", "operation": lhc3.lhcb, "config": config.lhcb},
        ],
        "velo": lhc3.velo,
        "bcm": lhc3.bcm,
        "totem": lhc3.totem,
        "cryo": {
            "max_t": cryo.max_temps,
            "lost_count": cryo.lost_count,
            "state": cryo.state,
        },
        "next": wake_time.strftime(time_fmt),
    }
    json_state = jenc.encode(dict_state)
    with open("vistars.json", "w") as json_file:
        json_file.write(json_state)
    dl_failed = 0
    sleep(timeout + to_adjust)
