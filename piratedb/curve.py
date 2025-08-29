from .state import State
from .utils import STATS

def is_curve_template(obj: dict) -> bool:
    try:
        attributes = obj["m_attributes"]
    except KeyError:
        return False
    else:
        return True
    
CURVE_STATS = [
    "Will",
    "Strength",
    "Agility",
    "Accuracy",
    "Armor",
    "Max Health",
    "Dodge",
    "Attack Range",
    "Movement Range",
    "Weapon Power",
    "Magic Resist",
    "Spell Power",
    "Talent Slots",
    "Epic Talent Slots",
]

CURVE_CLASSES = {
    b"category_cleric": "Privateer",
    b"category_fighter": "Buccaneer",
    b"category_wizard": "Witchdoctor",
    b"category_thief": "Swashbuckler",
    b"category_ranged": "Musketeer",
}

class Curve:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.real_name = obj["m_objectName"]

        adjective_list = obj["m_adjectiveList"]
        self.school = "Universal"
        for adj in adjective_list:
            if adj in CURVE_CLASSES:
                self.school = CURVE_CLASSES[adj]
                break

        attributes = obj["m_attributes"]
        self.curve_points = []
        self.curve_bonus_points = []
        self.curve_stats = []
        self.curve_bonus_stats = []
        for attribute in attributes:
            try:
                stat = STATS[attribute["m_sStatName"]]
            except:
                continue
            if stat not in CURVE_STATS:
                continue
            else:
                point_list = attribute["m_pointList"]
                for point in point_list:
                    self.curve_points.append((point["m_level"], point["m_value"]))
                    self.curve_stats.append(stat)
                bonus_list = attribute["m_bonusList"]
                for bonus in bonus_list:
                    if bonus["m_level"] == 0 or bonus["m_value"] == 0:
                        continue
                    self.curve_bonus_points.append((bonus["m_level"], bonus["m_value"]))
                    self.curve_bonus_stats.append(stat)
        
        behaviors = obj["m_behaviors"]
        talent_behavior = None
        power_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue
            
            match behavior["m_behaviorName"]:
                case b'PowerBehavior':
                    power_behavior = behavior
                
                case b'PowerBehaviorServer':
                    power_behavior = behavior
                
                case b'TalentBehavior':
                    talent_behavior = behavior
                
                case b'TalentBehaviorServer':
                    talent_behavior = behavior
        self.power_list = []
        self.power_sources = []
        if power_behavior != None:
            for power in power_behavior["m_powerData"]:
                self.power_list.append(power["m_powerID"])
                self.power_sources.append(power["m_source"])
        self.talent_list = []
        self.talent_sources = []
        self.talent_ranks = []
        if talent_behavior != None:
            for talent in talent_behavior["m_talents"]:
                self.talent_list.append(talent["m_talentID"])
                self.talent_sources.append(talent["m_source"])
                self.talent_ranks.append(talent["m_rank"])