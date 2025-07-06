from katsuba.op import LazyObject # type: ignore

from .state import State
from .tid_find import find_school_tid
from .utils import STATS, MANIFEST

ITEM_TYPE_ADJECTIVES = [
    b"EQUIP_Weapon",
    b"EQUIP_Accessory",
    b"EQUIP_Body",
    b"EQUIP_Boots",
    b"EQUIP_Hat",
    b"EQUIP_Token",
    b"EQUIP_Neck",
    b"EQUIP_Ring",
    b"EQUIP_Mount"
]
WEAPON_TYPE_ADJECTIVES = [
    b"TALENT_SHOOTY",
    b"TALENT_STABBY",
    b"TALENT_SMASHY",
    b"TALENT_SLASHY",
    b"TALENT_STAFF"
]

def is_item_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adjectives = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except KeyError:
        return False
    
    is_item = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"ItemBehavior":
            for adjective in adjectives:
                if adjective in ITEM_TYPE_ADJECTIVES:
                    is_item = True
            break
    return is_item

def _is_school_req(req: LazyObject) -> bool:
    try:
        school = req["m_classTemplateId"]
    except KeyError:
        return False
    return len(req) == 5

def _is_level_req(req: LazyObject) -> bool:
    return len(req) == 6

def _is_talent_req(req: LazyObject) -> bool:
    try:
        talent = req["m_nTalentId"]
    except KeyError:
        return False
    return len(req) == 5

def _is_stat_effect(effect: LazyObject) -> bool:
    return len(effect) == 7

def _is_talent_effect(effect: LazyObject) -> bool:
    try:
        talent = effect["m_nTalentID"]
    except KeyError:
        return False
    return len(effect) == 4

def _is_power_effect(effect: LazyObject) -> bool:
    try:
        power = effect["m_nPowerID"]
    except KeyError:
        return False
    return len(effect) == 4

def _is_weapon_effect(effect: LazyObject) -> bool:
    return len(effect) == 6

def _is_speed_effect(effect: LazyObject) -> bool:
    try:
        speed = effect["m_speedMultiplier"]
    except KeyError:
        return False
    return len(effect) == 4

class Item:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        if self.name.id == 5966405564772825542:
            self.name = state.make_lang_key({"m_displayName": b""})
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        adj_list = obj["m_adjectiveList"]

        behaviors = obj["m_behaviors"]
        item_behavior = None
        equippable_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'ItemBehavior':
                    item_behavior = behavior
                
                case b'EquippableBehavior':
                    equippable_behavior = behavior
        
        self.item_flags = item_behavior["m_itemFlags"]
        self.item_type = None
        self.weapon_type = ""
        for adj in adj_list:
            adjsplit = adj.split(b"_")
            if adjsplit[0] == b"TALENT":
                if adj in WEAPON_TYPE_ADJECTIVES:
                    if adj == b"TALENT_SHOOTY":
                        self.weapon_type += "Shooty"
                    elif adj == b"TALENT_SLASHY":
                        self.weapon_type += "Slashy"
                    elif adj == b"TALENT_STAFF":
                        self.weapon_type += "Staffy"
                    elif adj == b"TALENT_STABBY":
                        self.weapon_type += "Stabby"
                    elif adj == b"TALENT_SMASHY":
                        self.weapon_type += "Smashy"
                    self.weapon_type += "/"
            elif adjsplit[0] == b"EQUIP":
                if adj in ITEM_TYPE_ADJECTIVES:
                    self.item_type = adjsplit[-1].decode("utf-8")
                    if self.item_type == "Body":
                        self.item_type = "Outfit"
                    elif self.item_type == "Token":
                        self.item_type = "Totem"
                    elif self.item_type == "Neck":
                        self.item_type = "Charm"
        if self.weapon_type == "":
            self.weapon_type = None
        if self.weapon_type != None:
            self.weapon_type = self.weapon_type[:-1]
        if equippable_behavior != None:
            equipReqs = None
            equipReqs = equippable_behavior["m_equipRequirements"]
            equipEffects = equippable_behavior["m_equipEffects"]
            self.level_req = 1
            self.school_req = None
            self.talent_req = None
            self.talent_req_rank = None
            if equipReqs != None:
                if "m_requirements" in equipReqs:
                    for req in equipReqs["m_requirements"]:
                        if _is_school_req(req):
                            self.school_req = find_school_tid(MANIFEST, req["m_classTemplateId"])
                        elif _is_level_req(req):
                            self.level_req = req["m_nMinLevel"]
                        elif _is_talent_req(req):
                            self.talent_req = req["m_nTalentId"]
                            self.talent_req_rank = req["m_nMinimumRank"]
            self.stat_effects = []
            self.stat_effect_nums = []
            self.talent_effects = []
            self.power_effects = []
            self.weapon_damage_type = None
            self.weapon_primary_stat = None
            for effect in equipEffects:
                if _is_stat_effect(effect):
                    self.stat_effects.append(STATS[effect["m_sStatName"]])
                    self.stat_effect_nums.append(effect["m_fAmount"])
                elif _is_talent_effect(effect):
                    self.talent_effects.append(effect["m_nTalentID"])
                elif _is_power_effect(effect):
                    self.power_effects.append(effect["m_nPowerID"])
                elif _is_weapon_effect(effect):
                    self.weapon_damage_type = STATS[effect["m_nDamageType"]]
                    self.weapon_primary_stat = effect["m_nPrimaryStat"]
                elif _is_speed_effect(effect):
                    self.stat_effects.append("Speed")
                    self.stat_effect_nums.append(round(effect["m_speedMultiplier"] - 1, 2))