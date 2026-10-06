from pathlib import Path
import os
import sqlite3
import sys
import time

from .db import build_db
from .curve import Curve, is_curve_template
from .roster import Roster, is_roster_template
from .faction import Faction, is_faction_template
from .item import Item, is_item_template
from .unit import Unit, is_unit_template
from .pet import Pet, is_pet_template
from .talent import Talent, is_talent_template
from .power import Power, is_power_template
from .pet_talents import PetTalent, is_pet_talent_template
from .pet_powers import PetPower, is_pet_power_template
from .shipitem import ShipItem, is_ship_item_template
from .ship import Ship, is_ship_template
from .shipability import ShipAbility, is_ship_ability_template
from .state import State
from .utils import ROOT, ROOT_WAD, TYPES

ITEMS_DB = ROOT / "items.db"
LOCALE = "Locale/English"


def deserialize_files(state: State):
    curves = []
    rosters = []
    factions = []
    items = []
    units = []
    pets = []
    talents = []
    powers = []
    pet_talents = []
    pet_powers = []
    ships = []
    ship_items = []
    ship_abilities = []
    vdfs = []

    for file in state.de.archive.iter_glob("ObjectData/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if obj == None:
            continue

        if is_curve_template(obj):
            curve = Curve(state, obj)
            curves.append(curve)
    
    for file in state.de.archive.iter_glob("Factions/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if obj == None:
            continue

        if is_faction_template(obj):
            faction = Faction(state, obj)
            factions.append(faction)
                
    for file in state.de.archive.iter_glob("ObjectData/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if obj == None:
            continue

        if is_roster_template(obj):
            roster = Roster(state, obj)
            rosters.append(roster)
        
        if is_item_template(obj):
            item = Item(state, obj)
            if item.vdf != "" and (item.vdf_type, item.vdf, item.fallback_icon) not in vdfs:
                vdfs.append((item.vdf_type, item.vdf, item.fallback_icon))
            items.append(item)

        if is_unit_template(obj):
            unit = Unit(state, obj, curves)
            if unit.vdf != "" and (unit.vdf_type, unit.vdf, unit.fallback_icon) not in vdfs:
                vdfs.append((unit.vdf_type, unit.vdf, unit.fallback_icon))
            units.append(unit)

        if is_pet_template(obj):
            pet = Pet(state, obj)
            if pet.vdf != "" and (pet.vdf_type, pet.vdf, pet.fallback_icon) not in vdfs:
                vdfs.append((pet.vdf_type, pet.vdf, pet.fallback_icon))
            pets.append(pet)

        if is_pet_talent_template(obj):
            pet_talent = PetTalent(state, obj)
            pet_talents.append(pet_talent)
        
        if is_pet_power_template(obj):
            pet_power = PetPower(state, obj)
            pet_powers.append(pet_power)
        
        if is_ship_template(obj):
            ship = Ship(state, obj)
            if ship.vdf != "" and (ship.vdf_type, ship.vdf, ship.fallback_icon) not in vdfs:
                vdfs.append((ship.vdf_type, ship.vdf, ship.fallback_icon))
            ships.append(ship)
        
        if is_ship_item_template(obj):
            ship_item = ShipItem(state, obj)
            if ship_item.vdf != "" and (ship_item.vdf_type, ship_item.vdf, ship_item.fallback_icon) not in vdfs:
                vdfs.append((ship_item.vdf_type, ship_item.vdf, ship_item.fallback_icon))
            ship_items.append(ship_item)
    
    for file in state.de.archive.iter_glob("BroadsidePowers/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_ship_ability_template(obj):
            ship_ability = ShipAbility(state, obj)
            if ship_ability.image != "" and ("Image", ship_ability.vdf, "") not in vdfs:
                vdfs.append(("Image", ship_ability.vdf, ""))
            ship_abilities.append(ship_ability)

    for file in state.de.archive.iter_glob("Talents/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_talent_template(obj):
            talent = Talent(state, obj)
            if talent.image != "" and ("Image", talent.vdf, "") not in vdfs:
                vdfs.append(("Image", talent.vdf, ""))
            talents.append(talent)
    
    for file in state.de.archive.iter_glob("Abilities/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_power_template(obj):
            power = Power(state, obj)
            if power.image != "" and ("Image", power.vdf, "") not in vdfs:
                vdfs.append(("Image", power.vdf, ""))
            powers.append(power)

    return curves, rosters, factions, items, units, pets, talents, powers, pet_talents, pet_powers, ships, ship_items, ship_abilities, vdfs

def main():
    start = time.time()
    
    state = State(ROOT_WAD, TYPES)
    curves, rosters, factions, items, units, pets, talents, powers, pet_talents, pet_powers, ships, ship_items, ship_abilities, vdfs = deserialize_files(state)

    if ITEMS_DB.exists():
        ITEMS_DB.unlink()

    db = sqlite3.connect(str(ITEMS_DB))
    build_db(state, curves, rosters, factions, items, units, pets, talents, powers, pet_talents, pet_powers, ships, ship_items, ship_abilities, vdfs, db)
    db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()} in {round(time.time() - start, 2)} seconds")


if __name__ == "__main__":
    main()
