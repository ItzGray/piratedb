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