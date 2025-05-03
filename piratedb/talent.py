from .state import State

def is_talent_template(obj: dict) -> bool:
    try:
        ranks = obj["m_ranks"]
    except KeyError:
        return False
    
    return True

class Talent:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        ranks = obj["m_ranks"]
        self.rank_count = 0
        self.ranks = []
        self.descriptions = []
        self.unit_levels = []
        for rank in ranks:
            if rank["m_requiredUnitLevel"] > 0:
                self.unit_levels.append(rank["m_requiredUnitLevel"])
            else:
                self.unit_levels.append(None)
            self.rank_count += 1
            self.ranks.append(self.rank_count)
            self.descriptions.append(state.make_desc_lang_key(rank))

