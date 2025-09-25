from katsuba.op import LazyObject # type: ignore
from katsuba.utils import djb2 # type: ignore

from .state import State
from .tid_find import find_tid_path
from .utils import STATS, MANIFEST

def is_faction_template(obj: dict) -> bool:
    return (obj.type_hash == djb2("class FactionTemplate"))

class Faction:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.faction_key = obj["m_factionKey"]
        ship_name_flags = obj["m_shipNames"]
        unit_name_flags = obj["m_unitNames"]
        self.gender_check = unit_name_flags["m_firstNameHasGender"]