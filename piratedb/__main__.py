from pathlib import Path
import os
import sqlite3
import sys
import time

from .db import build_db
from .item import Item, is_item_template
from .unit import Unit, is_unit_template
from .pet import Pet, is_pet_template
from .talent import Talent, is_talent_template
from .power import Power, is_power_template
from .state import State
from .utils import ROOT, ROOT_WAD, TYPES

ITEMS_DB = ROOT / "items.db"
LOCALE = "Locale/English"


def deserialize_files(state: State):
    items = []
    units = []
    pets = []
    talents = []
    powers = []
                
    for file in state.de.archive.iter_glob("ObjectData/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if obj == None:
            continue

        if is_item_template(obj):
            item = Item(state, obj)
            items.append(item)

        if is_unit_template(obj):
            unit = Unit(state, obj)
            units.append(unit)

        if is_pet_template(obj):
            pet = Pet(state, obj)
            pets.append(pet)

    for file in state.de.archive.iter_glob("Talents/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_talent_template(obj):
            talent = Talent(state, obj)
            talents.append(talent)
    
    for file in state.de.archive.iter_glob("Abilities/*.xml"):
        obj = state.de.deserialize_from_path(file)

        if is_power_template(obj):
            power = Power(state, obj)
            powers.append(power)

    return items, units, pets, talents, powers

def main():
    start = time.time()
    
    state = State(ROOT_WAD, TYPES)
    items, units, pets, talents, powers = deserialize_files(state)

    if ITEMS_DB.exists():
        ITEMS_DB.unlink()

    db = sqlite3.connect(str(ITEMS_DB))
    build_db(state, items, units, pets, talents, powers, db)
    db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()} in {round(time.time() - start, 2)} seconds")


if __name__ == "__main__":
    main()
