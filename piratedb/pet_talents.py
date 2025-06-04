from .state import State

def is_pet_talent_template(obj: dict) -> bool:
    try:
        equipEffect = obj["m_bEquipEffect"]
    except KeyError:
        return False
    
    try:
        rank = obj["m_nRank"]
    except KeyError:
        return False
    else:
        return True

class PetTalent:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_icon"][0].split(b"/")[-1]
        except:
            self.image = ""
        self.rarity = obj["m_nRarity"]
        self.grant = obj["m_bEquipEffect"]