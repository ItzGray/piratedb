from katsuba.op import LazyObject # type: ignore
from katsuba.utils import djb2 # type: ignore

from .state import State
from .tid_find import find_tid_path
from .utils import STATS, MANIFEST

ITEM_TYPE_ADJECTIVES = {
    b"EQUIP_SHIP_Armor": "Armor",
    b"EQUIP_SHIP_Anchor": "Anchor",
    b"EQUIP_SHIP_Cannon": "Cannons",
    b"EQUIP_SHIP_Figurehead": "Figurehead",
    b"EQUIP_SHIP_Horn": "Horn",
    b"EQUIP_SHIP_Rudder": "Rudder",
    b"EQUIP_SHIP_Sails": "Sails",
    b"EQUIP_SHIP_Wheel": "Wheel"
}

def is_ship_item_template(obj: dict) -> bool:
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
                if adjective == b"SHIP_EQUIP":
                    is_item = True
            break
    return is_item

class ShipItem:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        if self.name.id == 5966405564772825542:
            self.name = state.make_lang_key({"m_displayName": b""})
        self.real_name = obj["m_objectName"]
        self.image = ""
        adj_list = obj["m_adjectiveList"]

        behaviors = obj["m_behaviors"]
        item_behavior = None
        equippable_behavior = None
        visual_behavior = None
        broadside_power_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'ItemBehavior':
                    item_behavior = behavior
                
                case b'EquippableBehavior':
                    equippable_behavior = behavior

                case b'VisualBehavior':
                    visual_behavior = behavior
                
                case b'BroadsidePowerListBehavior':
                    broadside_power_behavior = behavior
        
        self.item_flags = item_behavior["m_itemFlags"]
        self.vdf = ""
        self.vdf_type = ""
        self.fallback_icon = ""
        if visual_behavior != None:
            if visual_behavior["m_sVisualDefinitionFile"] != b"":
                self.vdf = visual_behavior["m_sVisualDefinitionFile"].decode("utf-8")
                self.image = visual_behavior["m_sVisualDefinitionFile"].split(b"/")[-1]
                try:
                    self.fallback_icon = obj["m_sIcon"][0].decode("utf-8")
                except:
                    pass
                self.vdf_type = "VDF"
            else:
                try:
                    self.vdf = obj["m_sIcon"][0].decode("utf-8")
                    self.image = obj["m_sIcon"][0].split(b"/")[-1]
                    self.vdf_type = "Image"
                except:
                    self.image = ""
        else:
            try:
                self.vdf = obj["m_sIcon"][0].decode("utf-8")
                self.image = obj["m_sIcon"][0].split(b"/")[-1]
                self.vdf_type = "Image"
            except:
                self.image = ""
        self.item_type = None
        for adj in adj_list:
            try:
                self.item_type = ITEM_TYPE_ADJECTIVES[adj]
            except KeyError:
                continue
        
        if equippable_behavior != None:
            equip_reqs = equippable_behavior["m_equipRequirements"]
            equip_effects = equippable_behavior["m_equipEffects"]
            self.level_req = 1
            self.naut_lvl_req = 1
            self.origin_req = "All"
            if equip_reqs != None:
                if "m_requirements" in equip_reqs:
                    for req in equip_reqs["m_requirements"]:
                        if req.type_hash == djb2("class ReqFaction"):
                            tid_path = find_tid_path(MANIFEST, req["m_factionTemplateId"])
                            self.origin_req = state.get_faction_lang(state.de.deserialize_from_path(tid_path))
                        elif req.type_hash == djb2("class ReqNauticalLevel"):
                            self.naut_lvl_req = req["m_nMinLevel"]
                        elif req.type_hash == djb2("class ReqPlayerLevel"):
                            self.level_req = req["m_nMinLevel"]
            self.stat_effects = []
            self.stat_effect_nums = []
            for effect in equip_effects:
                if effect.type_hash == djb2("class StatModifierInfo"):
                    self.stat_effects.append(STATS[effect["m_sStatName"]])
                    self.stat_effect_nums.append(round(effect["m_fAmount"], 3))
        
        self.power_list = []
        if broadside_power_behavior != None:
            for power in broadside_power_behavior["m_powers"]:
                if power == None:
                    continue
                self.power_list.append(power)
            