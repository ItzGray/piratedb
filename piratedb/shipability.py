from enum import IntFlag
from katsuba.utils import djb2 # type: ignore

from .state import State
from .utils import STATS, MODIFIER_OPERATORS, MANIFEST
from .tid_find import find_tid_path

def is_ship_ability_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adjectives = obj["m_adjectiveList"]
    except KeyError:
        return False
    
    return (obj.type_hash == djb2("class BroadsidePowerTemplate"))

class ShipAbility:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.vdf = obj["m_sIcon"][0].decode("utf-8")
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        self.description = state.make_desc_lang_key(obj)
        self.close_accuracy = obj["m_nCloseAccuracy"]
        self.long_accuracy = obj["m_nLongAccuracy"]
        self.cooldown = obj["m_cooldown"] / 1000
        impacts = obj["m_impacts"]