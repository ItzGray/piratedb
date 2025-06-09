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

class Curve:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.real_name = obj["m_objectName"]

        attributes = obj["m_attributes"]
        self.curve_levels = []
        self.curve_values = []
        self.curve_bonus_levels = []
        self.curve_bonus_values = []
        self.curve_stats = []
        for attribute in attributes:
            stat = STATS[attribute["m_sStatName"]]
            if stat not in CURVE_STATS:
                continue
            else:
                point_list = attribute["m_pointList"]
                for point in point_list:
                    self.curve_levels.append(point["m_level"])
                    self.curve_values.append(point["m_value"])
                bonus_list = attribute["m_bonusList"]
                for bonus in bonus_list:
                    self.curve_bonus_levels.append(bonus["m_level"])
                    self.curve_bonus_values.append(bonus["m_value"])
                self.curve_stats.append(stat)