from .state import State
from .unit import MODIFIER_OPERATORS
from .utils import STATS
from katsuba.utils import djb2 # type: ignore

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
            self.vdf = obj["m_sIcon"][0].decode("utf-8")
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        ranks = obj["m_ranks"]
        self.rank_count = 0
        self.ranks = []
        self.rank_operators = []
        self.rank_stats = []
        self.rank_values = []
        self.rank_images = []
        self.rank_tooltips = []
        self.descriptions = []
        self.unit_levels = []
        for rank in ranks:
            rank_img_lst = []
            if rank["m_requiredUnitLevel"] > 0:
                self.unit_levels.append(rank["m_requiredUnitLevel"])
            else:
                self.unit_levels.append(None)
            self.rank_count += 1
            self.ranks.append(self.rank_count)
            self.descriptions.append(state.make_desc_lang_key(rank))
            try:
                rank_img_lst.append(rank["m_sBottomLeftIcon"].split(b"/")[-1])
            except:
                rank_img_lst.append("")
            try:
                rank_img_lst.append(rank["m_sBottomRightIcon"].split(b"/")[-1])
            except:
                rank_img_lst.append("")
            try:
                rank_img_lst.append(rank["m_sUpperLeftIcon"].split(b"/")[-1])
            except:
                rank_img_lst.append("")
            self.rank_images.append(tuple(rank_img_lst))
            rank_tooltip_lst = []
            rank_tooltip_lst.append(state.make_rank_tooltip_lang_key(rank, "m_sBottomLeftText"))
            rank_tooltip_lst.append(state.make_rank_tooltip_lang_key(rank, "m_sBottomRightText"))
            rank_tooltip_lst.append(state.make_rank_tooltip_lang_key(rank, "m_sUpperLeftText"))
            self.rank_tooltips.append(tuple(rank_tooltip_lst))
            effects = rank["m_effects"]
            for effect in effects:
                if effect.type_hash == djb2("class StatModifierInfo"):
                    try:
                        self.rank_operators.append(MODIFIER_OPERATORS[effect["m_eOperator"]])
                        self.rank_stats.append(STATS[effect["m_sStatName"]])
                        self.rank_values.append(round(effect["m_fAmount"], 2))
                    except:
                        self.rank_operators.append(-1)
                        self.rank_stats.append("")
                        self.rank_values.append(-1)
                else:
                    self.rank_operators.append(-1)
                    self.rank_stats.append("")
                    self.rank_values.append(-1)
                break
            if len(effects) == 0:
                self.rank_operators.append(-1)
                self.rank_stats.append("")
                self.rank_values.append(-1)


