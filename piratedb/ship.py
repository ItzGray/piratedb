from katsuba.op import LazyObject # type: ignore
from katsuba.utils import djb2 # type: ignore

from .state import State
from .tid_find import find_tid_path
from .utils import STATS, MANIFEST

def is_ship_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adjectives = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except KeyError:
        return False
    
    is_ship = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"AIShipCombatBehavior" or behavior["m_behaviorName"] == b"PlayerShipCombatBehavior":
            is_ship = True
        
    return is_ship

class Ship:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.title = state.make_desc_lang_key(obj)
        self.real_name = obj["m_objectName"]

        behaviors = obj["m_behaviors"]
        self.ship_type = ""
        visual_behavior = None
        ship_combat_behavior = None
        ship_info_behavior = None
        inventory_behavior = None
        broadside_behavior = None
        mob_army_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'ShipInfoBehavior':
                    ship_info_behavior = behavior
                
                case b'VisualBehavior':
                    visual_behavior = behavior

                case b'AIShipCombatBehavior':
                    ship_combat_behavior = behavior
                    self.ship_type = "Enemy"
                
                case b'PlayerShipCombatBehavior':
                    ship_combat_behavior = behavior
                    self.ship_type = "Player"
                
                case b'MobArmyBehavior':
                    mob_army_behavior = behavior
                
                case b'InventoryBehavior':
                    inventory_behavior = behavior
                
                case b'BroadsideCombatBehavior':
                    broadside_behavior = behavior

        self.vdf = ""
        self.vdf_type = ""
        if visual_behavior != None:
            if visual_behavior["m_sVisualDefinitionFile"] != b"":
                self.vdf = visual_behavior["m_sVisualDefinitionFile"].decode("utf-8")
                self.image = visual_behavior["m_sVisualDefinitionFile"].split(b"/")[-1]
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
        
        if ship_info_behavior != None:
            self.ship_class = ship_info_behavior["m_shipCombatClassID"]
            self.name = state.make_custom_lang_key(ship_info_behavior["m_nameOverride"])
            if self.name.id == None:
                self.name = self.title
            tid_path = find_tid_path(MANIFEST, ship_info_behavior["m_factionTemplateID"])
            if tid_path is not None:
                self.faction = state.get_faction_lang(state.de.deserialize_from_path(tid_path))
            else:
                self.faction = ""
            self.unsinkable = ship_info_behavior["m_bUnsinkable"]
            equip_reqs = ship_info_behavior["m_equipRequirements"]
            self.naut_lvl_req = 1
            self.level_req = 1
            if equip_reqs != None:
                if "m_requirements" in equip_reqs:
                        for req in equip_reqs["m_requirements"]:
                            if req.type_hash == djb2("class ReqNauticalLevel"):
                                self.naut_lvl_req = req["m_nMinLevel"]
                            elif req.type_hash == djb2("class ReqPlayerLevel"):
                                self.level_req = req["m_nMinLevel"]
        
        self.default_items = []
        if inventory_behavior != None:
            for item in inventory_behavior["m_defaultEquipment"]:
                self.default_items.append(item)

        self.auto_powers = []
        if broadside_behavior != None:
            for power in broadside_behavior["m_powerEntries"]:
                self.auto_powers.append(power["m_powerID"])
        
        self.rosters = []
        self.extra_units = []
        if mob_army_behavior != None:
            for roster in mob_army_behavior["m_rosters"]:
                self.rosters.append(roster)
            for unit in mob_army_behavior["m_unitTemplates"]:
                self.extra_units.append(unit)