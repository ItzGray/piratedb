from katsuba.op import LazyObject # type: ignore
from katsuba.utils import djb2 # type: ignore

from .state import State
from .tid_find import find_tid_path
from .utils import STATS, MANIFEST

def is_roster_template(obj: dict) -> bool:
    return (obj.type_hash == djb2("class MobArmyRosterTemplate"))

class Roster:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.real_name = obj["m_sDebugName"]
        self.units = []
        for unit in obj["m_entries"]:
            self.units.append(unit["m_nUnitID"])