import json
from decimal import Decimal
from page1 import Flags, Comments, Postmortem
from config import Config
from oper import Experiment, Velo


class Encoder(json.JSONEncoder):
    def default(self, o):
        time_fmt: str = "%Y-%m-%dT%H:%M:%S%z"
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, Flags):
            return {
                    "link_status": o.link_status,
                    "global_beam_permit": o.global_beam_permit,
                    "setup_beam": o.setup_beam,
                    "beam_presence": o.beam_presence,
                    "moveable_devices": o.moveable_devices,
                    "stable_beams": o.stable_beams,
            }
        elif isinstance(o, Comments):
            return {"time": o.time.strftime(time_fmt), "text": o.text}
        elif isinstance(o, Postmortem):
            if o.id.year == 2008:
                return None
            return {
                    "id": o.id.strftime(time_fmt),
                    "category": o.category,
                    "classification": o.classification,
                    "analysis": o.analysis,
                    "comment": o.comment,
            }
        elif isinstance(o, Experiment):
            return {
                    "status": o.status,
                    "inst_lumi": o.inst_lumi,
                    "bran_lumi": o.bran_lumi,
                    "fill_lumi": o.fill_lumi,
                    "b1_bkgd": o.b1_bkgd,
                    "b2_bkgd": o.b2_bkgd,
            }
        elif isinstance(o, Velo):
            return {
                    "position": o.pos,
                    "gap": None if o.gap.is_nan() else o.gap,
                    "smog": o.smog,
            }
        else:
            return super().default(o)
