from enum import Enum, IntFlag
from typing import Iterator
from pathlib import Path

from .deserializer import BinDeserializer

from katsuba.op import * # type: ignore

STATS = [
    "Will",
    "Strength",
    "Agility",
    "Accuracy",
    "Armor",
    "Max Health",
    "Current Health",
    "Dodge",
    "Attack Range",
    "Movement Range",
    "Armor Penetration",
    "Command Radius",
    "Threat Generation",
    "Crit Rating",
    "Crit Damage",
    "Weapon Power",
    "Physical Damage",
    "Magical Damage",
    "Magic Resist",
    "Current Mana",
    "Max Mana",
    "Max Energy",
    "Current Energy",
    "Spell Power",
    "Practice Points",
    "Training Points",
    "XP Boost",
    "Nautical XP Boost",
    "Gold Boost",
    None,
    "Power Slot Chance",
    "Nautical XP",
    "Experience",
    "XP Value",
    "Talent Slots",
    "Epic Talent Slots",
    "Knockout Duration",
    "Task Duration",
    "Ship Acceleration",
    "Ship Minimum Speed",
    "Ship Maximum Speed",
    "Ship Turning Speed",
    "Ship Fuel Rate",
    "Ship Boost Speed",
    "Ship Boost Turn Speed",
    "Ship Max Health",
    "Ship Current Health",
    "Ship Repair Rate",
    "Ship Firing Rate",
    "Ship Damage",
    "Ship Armor",
    "Ship Accuracy",
    "Ship Maneuver",
    "Ship Max Fuel",
    "Ship Current Fuel",
    "Pet Guts",
    "Pet Guile",
    "Pet Grit",
    "Pet Power",
    "Pet PvE Spawn Chance",
    "Strength",
    "Agility",
    "Will",
    "Pet Guts",
    "Pet Guile",
    "Pet Grit",
    "Pet Power",
    "Max Health",
    "Pet Max Action",
    "Pet Current Action",
    "Pet Current Power",
    "Pet Cheer Cost",
    "Pet Task Speed",
    "Unit Task Aptitude Gold",
    "Unit Task Aptitude Loot",
    "Unit Task Aptitude Nautical XP",
    "Unit Task Aptitude Tomes",
    "Unit Task Aptitude Bed Rest",
    "Unit Task Rate Gold",
    "Unit Task Rate Loot",
    "Unit Task Rate XP",
    "Unit Task Rate Bed Rest",
    "Unit Task Rate Pet Loot"
]

MODIFIER_OPERATORS = {0: "Set", 1: "Set Add", 2: "Power", 3: "Multiply Add", 4: "Multiply", 5: "Add"}

ROOT = Path(__file__).parent.parent
ROOT_WAD = ROOT / "Root.wad"
TYPES = ROOT / "types.json"

de = BinDeserializer(ROOT_WAD, TYPES)
MANIFEST = de.deserialize_from_path("TemplateManifest.xml")

def op_to_dict(type_list: TypeList, v):
    if isinstance(v, LazyObject):
        lazy_dict = {k: op_to_dict(type_list, e) for k, e in v.items(type_list)}
        lazy_dict["$__type"] = type_list.name_for(v.type_hash)
        return lazy_dict
    
    elif isinstance(v, LazyList):
        return [op_to_dict(type_list, e) for e in v]
    
    elif isinstance(v, Vec3):
        return f"(x={v.x}, y={v.y}, z={v.z})"
    
    elif isinstance(v, Quaternion):
        return f"(z={v.x}, y={v.y=}, z={v.z}, w={v.w})"
    
    elif isinstance(v, Matrix):
        return f"[{v.i}, {v.j}, {v.k}]"
    
    elif isinstance(v, Euler):
        return f"(pitch={v.pitch}, yaw={v.yaw}, roll={v.roll})"
    
    elif isinstance(v, PointInt) or isinstance(v, PointFloat):
        return f"(x={v.x}, y={v.y})"
    
    elif isinstance(v, SizeInt):
        return f"({v.width}, {v.height})"
    
    elif isinstance(v, RectInt) or isinstance(v, RectFloat):
        return f"(left={v.left}, top={v.top}, right={v.right}, bottom={v.bottom})"
    
    elif isinstance(v, Color):
        return f"(r={v.r}, g={v.g}, b={v.b}, a={v.a})"
    
    return v

def convert_rarity(obj: dict) -> int:
    rarity = obj.get("m_rarity", "r::RT_UNKNOWN").split("::")[1]
    if rarity == "RT_COMMON":
        return 0
    elif rarity == "RT_UNCOMMON":
        return 1
    elif rarity == "RT_RARE":
        return 2
    elif rarity == "RT_ULTRARARE":
        return 3
    elif rarity == "RT_EPIC":
        return 4
    else:
        return -1


def fnv_1a(data) -> int:
    if isinstance(data, str):
        data = data.encode()

    state = 0xCBF2_9CE4_8422_2325
    for b in data:
        state ^= b
        state *= 0x0000_0100_0000_01B3
        state &= 0xFFFF_FFFF_FFFF_FFFF
    return state >> 1

def iter_lazyobject_keys(types: TypeList, obj: LazyObject):
    iterd_lazyobject = []
    for item in obj.items(types):
        iterd_lazyobject.append(item[0])
    
    return iterd_lazyobject
