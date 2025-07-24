from pathlib import Path
import os
import sqlite3
import sys
import time

from .db import build_db
from .curve import Curve, is_curve_template
from .item import Item, is_item_template
from .unit import Unit, is_unit_template
from .pet import Pet, is_pet_template
from .talent import Talent, is_talent_template
from .power import Power, is_power_template
from .pet_talents import PetTalent, is_pet_talent_template
from .pet_powers import PetPower, is_pet_power_template
from .state import State
from .utils import ROOT, ROOT_WAD, TYPES

ITEMS_DB = ROOT / "items.db"
LOCALE = "Locale/English"


def deserialize_files(state: State):
    curves = []
    items = []
    units = []
    pets = []
    talents = []
    powers = []
    pet_talents = []
    pet_powers = []
    vdfs = []
                
    for file in state.de.archive.iter_glob("ObjectData/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if obj == None:
            continue

        if is_curve_template(obj):
            curve = Curve(state, obj)
            curves.append(curve)

        if is_item_template(obj):
            item = Item(state, obj)
            if item.vdf != "" and (item.vdf_type, item.vdf) not in vdfs:
                vdfs.append((item.vdf_type, item.vdf))
            items.append(item)

        if is_unit_template(obj):
            unit = Unit(state, obj)
            if unit.vdf != "" and (unit.vdf_type, unit.vdf) not in vdfs:
                vdfs.append((unit.vdf_type, unit.vdf))
            units.append(unit)

        if is_pet_template(obj):
            pet = Pet(state, obj)
            if pet.vdf != "" and (pet.vdf_type, pet.vdf) not in vdfs:
                vdfs.append((unit.vdf_type, pet.vdf))
            pets.append(pet)

        if is_pet_talent_template(obj):
            pet_talent = PetTalent(state, obj)
            pet_talents.append(pet_talent)
        
        if is_pet_power_template(obj):
            pet_power = PetPower(state, obj)
            pet_powers.append(pet_power)

    for file in state.de.archive.iter_glob("Talents/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_talent_template(obj):
            talent = Talent(state, obj)
            if talent.image != "" and ("Image", talent.vdf) not in vdfs:
                vdfs.append(("Image", talent.vdf))
            talents.append(talent)
    
    for file in state.de.archive.iter_glob("Abilities/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_power_template(obj):
            power = Power(state, obj)
            if power.image != "" and ("Image", power.vdf) not in vdfs:
                vdfs.append(("Image", power.vdf))
            powers.append(power)

    return curves, items, units, pets, talents, powers, pet_talents, pet_powers, vdfs

def main():
    start = time.time()
    
    state = State(ROOT_WAD, TYPES)
    curves, items, units, pets, talents, powers, pet_talents, pet_powers, vdfs = deserialize_files(state)

    if ITEMS_DB.exists():
        ITEMS_DB.unlink()

    db = sqlite3.connect(str(ITEMS_DB))
    build_db(state, curves, items, units, pets, talents, powers, pet_talents, pet_powers, vdfs, db)
    db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()} in {round(time.time() - start, 2)} seconds")


if __name__ == "__main__":
    main()
