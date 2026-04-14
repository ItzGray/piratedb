from katsuba.op import LazyObject # type: ignore
from katsuba.utils import djb2 # type: ignore

from .state import State
from .lang_files import LangCache, LangKey, OtherLangKey
from .tid_find import find_tid_path
from .utils import STATS, MANIFEST, CHARACTER_NAMES

def is_faction_template(obj: dict) -> bool:
    return (obj.type_hash == djb2("class FactionTemplate"))

class Faction:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.faction_key = obj["m_factionKey"]
        ship_name_flags = obj["m_shipNames"]
        unit_name_flags = obj["m_unitNames"]
        self.gender_check = unit_name_flags["m_firstNameHasGender"]
        self.ship_gender_check = ship_name_flags["m_firstNameHasGender"]
        self.unit_articles_check = unit_name_flags["m_useArticles"]
        self.ship_articles_check = ship_name_flags["m_useArticles"]
        self.unit_first_names_check = unit_name_flags["m_useFirstNames"]
        self.ship_first_names_check = ship_name_flags["m_useFirstNames"]
        self.unit_last_names_check = unit_name_flags["m_useLastNames"]
        self.ship_last_names_check = ship_name_flags["m_useLastNames"]
        self.no_names = False

        if not self.unit_first_names_check and not self.unit_last_names_check and not self.unit_articles_check:
            self.no_names = True

        self.unit_names = {"FirstNames": [], "LastNames": [], "Articles": []}
        name_table = CHARACTER_NAMES["m_table"]["m_serialValues"]
        if self.unit_first_names_check:
            key_search_1 = f"{self.faction_key.decode("utf-8")}_Unit_FirstNames"
            key_search_2 = key_search_1
            if self.gender_check:
                key_search_1 += "_Male"
                key_search_2 += "_Female"
            key_search_1 = key_search_1.encode("utf-8")
            key_search_2 = key_search_2.encode("utf-8")
            for name_list in name_table:
                if name_list["first"] == key_search_1 or name_list["first"] == key_search_2:
                    second = name_list["second"]
                    lang_section = second["m_langSection"]
                    for name in second["m_names"]:
                        self.unit_names["FirstNames"].append(state.make_other_lang_key((lang_section + b"_" + name)))
                    break
        
        if self.unit_last_names_check:
            key_search = f"{self.faction_key.decode("utf-8")}_Unit_LastNames".encode("utf-8")
            for name_list in name_table:
                if name_list["first"] == key_search:
                    second = name_list["second"]
                    lang_section = second["m_langSection"]
                    for name in second["m_names"]:
                        self.unit_names["LastNames"].append(state.make_other_lang_key((lang_section + b"_" + name)))
                    break

        if self.unit_articles_check:
            key_search = f"{self.faction_key.decode("utf-8")}_Unit_Articles".encode("utf-8")
            for name_list in name_table:
                if name_list["first"] == key_search:
                    second = name_list["second"]
                    lang_section = second["m_langSection"]
                    for name in second["m_names"]:
                        self.unit_names["Articles"].append(state.make_other_lang_key((lang_section + b"_" + name)))
                    break
        
        if not self.unit_names["FirstNames"] and not self.unit_names["LastNames"] and not self.unit_names["Articles"]:
            self.no_names = True