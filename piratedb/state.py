from pathlib import Path

from .lang_files import LangCache, LangKey, UnitLangKey, DescLangKey, RankTooltipLangKey
from .deserializer import BinDeserializer

class State:
    def __init__(self, root_wad: Path, types: Path):
        self.root_wad = root_wad
        self.de = BinDeserializer(root_wad, types)
        self.cache = LangCache(self.de, "Locale/English")

        self.file_to_id = {}
        self.id_to_file = {}

        manifest = self.de.deserialize_from_path("TemplateManifest.xml")
        for entry in manifest["m_serializedTemplates"]:
            filename = entry["m_filename"].decode()
            tid = entry["m_id"]

            self.file_to_id[filename] = tid
            self.id_to_file[tid] = filename

    def make_lang_key(self, obj: dict) -> LangKey:
        return LangKey(self.cache, obj)
    
    def make_unit_lang_key(self, obj: dict) -> UnitLangKey:
        return UnitLangKey(self.cache, obj)
    
    def make_desc_lang_key(self, obj: dict) -> DescLangKey:
        return DescLangKey(self.cache, obj)
    
    def make_rank_tooltip_lang_key(self, obj: dict, text_type: str) -> DescLangKey:
        return RankTooltipLangKey(self.cache, obj, text_type)
    
    def get_lang_str(self, langkey: LangKey) -> str:
        return self.cache.lookup.get(langkey.id)
