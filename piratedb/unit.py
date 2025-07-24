from .state import State
from .utils import STATS, MANIFEST
from .tid_find import find_school_tid

ATTACK_TYPES = {208075: "Melee", 208076: "Ranged", 732086: "Staff"}

def is_unit_template(obj: dict) -> bool:
    try:
        suffix = obj["m_displayName"]
        image = obj["m_sIcon"][0]
        adj_list = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except:
        return False
    
    if b"EQUIP_Pet" in adj_list:
        return False
    
    is_unit = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"AdvancedPetBehavior":
            is_unit = False
            break

        if behavior["m_behaviorName"] == b"UnitBehavior":
            is_unit = True

    return is_unit

sources = {0: "Unknown", 1: "Template", 2: "Trained"}
MODIFIER_OPERATORS = {0: "Set", 1: "Set Add", 2: "Multiply Add", 3: "Multiply", 4: "Add"}
valid_flags = [b"WB_Beast", b"WB_Undead", b"WB_Fowl", b"ADJ_AmberHorde", b"ADJ_Armada", b"ADJ_Cutthroat", b"ADJ_InoshishiBandit", b"ADJ_InoshishiWarlord", b"ADJ_NinjPig", b"ADJ_WharfRat", b"ADJ_Troggy", b"ADJ_TroggyArcher", b"ADJ_TroggyChief", b"ADJ_TroggyShaman", b"ADJ_TroggyWarrior", b"ADJ_Undead", b"ADJ_WaterMole", b"ADJ_WaterMole_Rebel", b"ADJ_Waponi", b"ADJ_Ophidian", b"ADJ_Vulture", b"ADJ_GNT_MR_Mob", b"ADJ_GNT_MR_Brute", b"ADJ_GNT_MR_Wailer", b"KTArmada", b"ADJ_Event_Boss", b"ADJ_Event_Base", b"ADJ_Event_Elite"]

class Unit:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_unit_lang_key(obj)
        self.suffix = state.make_lang_key(obj)
        if self.name.id == None:
            self.name = self.suffix
        self.real_name = obj["m_objectName"]
        self.image = ""
        adj_list = obj["m_adjectiveList"]
        self.flag_list = []
        for adj in adj_list:
            if adj in valid_flags:
                self.flag_list.append(adj)

        behaviors = obj["m_behaviors"]
        unit_behavior = None
        talent_behavior = None
        power_behavior = None
        mob_army_behavior = None
        visual_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue
            
            match behavior["m_behaviorName"]:
                case b'UnitBehavior':
                    unit_behavior = behavior
                
                case b'TalentBehavior':
                    talent_behavior = behavior
                
                case b'TalentBehaviorServer':
                    talent_behavior = behavior
                
                case b'PowerBehavior':
                    power_behavior = behavior
                
                case b'PowerBehaviorServer':
                    power_behavior = behavior

                case b'MobArmyBehavior':
                    mob_army_behavior = behavior

                case b'VisualBehavior':
                    visual_behavior = behavior
        
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
        self.curve = unit_behavior["m_classId"]
        self.school = find_school_tid(MANIFEST, unit_behavior["m_classId"])
        self.damage_type = STATS[unit_behavior["m_nDamageType"]]
        self.primary_stat = unit_behavior["m_nPrimaryStat"]
        self.stat_modifiers = []
        self.stat_modifier_values = []
        self.stat_modifier_operators = []
        stat_modifier_data = unit_behavior["m_statModifiers"]
        for stat_modifier in stat_modifier_data:
            self.stat_modifiers.append(STATS[stat_modifier["m_sStatName"]])
            self.stat_modifier_values.append(round(stat_modifier["m_fAmount"], 2))
            self.stat_modifier_operators.append(MODIFIER_OPERATORS[stat_modifier["m_eOperator"]])
        self.unit_type = None
        if mob_army_behavior != None:
            self.unit_type = "Enemy"
        else:
            self.unit_type = "Ally"
        self.powers = []
        self.power_sources = []
        self.talents = []
        self.talent_ranks = []
        self.talent_sources = []
        if power_behavior != None:
            power_data = power_behavior["m_powerData"]
            for power in power_data:
                self.powers.append(power["m_powerID"])
                self.power_sources.append(sources[power["m_source"]])
                
        if talent_behavior != None:
            talent_data = talent_behavior["m_talents"]
            for talent in talent_data:
                self.talents.append(talent["m_talentID"])
                self.talent_ranks.append(talent["m_rank"])
                self.talent_sources.append(sources[talent["m_source"]])
