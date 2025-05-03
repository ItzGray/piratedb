from enum import IntFlag

from .state import State
from .utils import STATS, MODIFIER_OPERATORS

def is_power_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adj_list = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except KeyError:
        return False
    
    is_power = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"CombatAbilityBehavior":
            if behavior["m_category"] == 3 or b"ADJ_Epic_Ability" in adj_list:
                is_power = True
                break
    return is_power

class Power:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        self.description = state.make_desc_lang_key(obj)
        behaviors = obj["m_behaviors"]
        combat_ability_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'CombatAbilityBehavior':
                    combat_ability_behavior = behavior
                     
        self.pvp_tag = combat_ability_behavior["m_allowedIn"]
        self.target_type = combat_ability_behavior["m_targetType"]
        