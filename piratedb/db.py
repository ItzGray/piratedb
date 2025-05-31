import sqlite3
from sqlite3 import Cursor

from .lang_files import LangCache

INIT_QUERIES = """CREATE TABLE locale_en (
    id   integer not null primary key,
    data text not null
);

CREATE INDEX en_name_lookup ON locale_en(data);

CREATE TABLE items (
    id                 integer not null primary key,
    name               integer,
    real_name          text,
    image              text,

    item_type          text,
    item_flags         integer,
    equip_school       integer,
    equip_level        integer,
    equip_talent       integer,
    equip_talent_rank  integer,

    foreign key(name)   references locale_en(id)
);

CREATE TABLE item_stats (
    id       integer not null primary key,
    item     integer not null,

    type     text,
    stat     integer,
    amount   integer,

    foreign key(item)   references items(id)
);

CREATE INDEX item_stat_lookup ON item_stats(item);

CREATE TABLE powers (
    id              integer not null primary key,
    name            integer,
    real_name       text,
    image           text,
    description     integer,
    pvp_tag         integer,
    target_type     integer,

    foreign key(name)   references locale_en(id)
    foreign key(description)    references locale_en(id)
);


CREATE TABLE talents (
    id              integer not null primary key,
    name            integer,
    real_name       text,
    image           text,
    ranks           integer,

    foreign key(name)   references locale_en(id)
);


CREATE TABLE talent_ranks (
    id              integer not null primary key,
    talent          integer not null,

    rank            integer,
    description     integer,
    level_req_unit  integer,

    foreign key(talent) references talents(id)
    foreign key(description)    references locale_en(id)
);

CREATE INDEX talent_rank_lookup ON talent_ranks(talent);


CREATE TABLE units (
    id                  integer not null primary key,
    name                integer,
    real_name           text,
    image               text,
    title               integer,
    school              text,
    attack_type         text,
    dmg_type            text,
    primary_stat        text,
    beast_flag          integer,
    undead_flag         integer,
    bird_flag           integer,

    foreign key(name)   references locale_en(id)
    foreign key(title)  references locale_en(id)
);


CREATE TABLE unit_talents (
    id         integer not null primary key,
    unit       integer not null,

    type       text,
    talent     integer,
    rank       integer,
    source     integer,

    foreign key(unit)   references units(id)
);

CREATE INDEX unit_talent_lookup ON unit_talents(unit);


CREATE TABLE unit_stats (
    id       integer not null primary key,
    unit     integer not null,

    stat     integer,
    operator integer,
    modifier integer,

    foreign key(unit)   references units(id)
);

CREATE INDEX unit_stats_lookup ON unit_stats(unit);


CREATE TABLE pets (
    id              integer not null primary key,
    name            integer,
    real_name       text,
    image           text,

    strength        integer,
    agility         integer,
    will            integer,
    power           integer,
    guts            integer,
    guile           integer,
    grit            integer,
    hp              integer,
    item_flags      integer,

    foreign key(name)   references locale_en(id)
);


CREATE TABLE pet_talents (
    id              integer not null primary key,
    pet             integer not null,

    talent          integer not null,

    foreign key(pet)    references pets(id)
);

CREATE INDEX pet_talent_lookup ON pet_talents(pet);


CREATE TABLE pet_powers (
    id              integer not null primary key,
    pet             integer not null,

    power           integer not null,

    foreign key(pet)    references pets(id)
);

CREATE INDEX pet_power_lookup ON pet_powers(pet);

"""


def _progress(_status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')


def build_db(state, items, units, pets, talents, powers, out):
    mem = sqlite3.connect(":memory:")
    cursor = mem.cursor()

    initialize(cursor)
    insert_locale_data(cursor, state.cache)
    insert_items(cursor, items)
    insert_units(cursor, units)
    insert_pets(cursor, pets)
    insert_talents(cursor, talents)
    insert_powers(cursor, powers)
    mem.commit()

    with out:
        mem.backup(out, pages=1)

    mem.close()


def initialize(cursor):
    cursor.executescript(INIT_QUERIES)


def insert_locale_data(cursor, cache: LangCache):
    cursor.executemany(
        "INSERT INTO locale_en(id, data) VALUES (?, ?)",
        cache.lookup.items()
    )


def insert_items(cursor, items):
    values = []
    stats = []

    for item in items:
        values.append((
            item.template_id,
            item.name.id,
            item.real_name,
            item.image,
            item.item_type,
            item.item_flags,
            item.school_req,
            item.level_req,
            item.talent_req,
            item.talent_req_rank
        ))

        for stat in range(len(item.stat_effects)):
            stats.append((
                item.template_id,
                "Stat",
                item.stat_effects[stat],
                item.stat_effect_nums[stat]
            ))
        
        for talent in range(len(item.talent_effects)):
            stats.append((
                item.template_id,
                "Talent",
                item.talent_effects[talent],
                1
            ))
        
        for power in range(len(item.power_effects)):
            stats.append((
                item.template_id,
                "Power",
                item.power_effects[power],
                1
            ))
        
        if item.weapon_type != None:
            stats.append((
                item.template_id,
                "Weapon Type",
                item.weapon_type,
                1
            ))
            stats.append((
                item.template_id,
                "Weapon Type",
                item.weapon_damage_type,
                1
            ))
            stats.append((
                item.template_id,
                "Weapon Type",
                item.weapon_primary_stat,
                1
            ))
    
    cursor.executemany(
        """INSERT INTO items(id,name,real_name,image,item_type,item_flags,equip_school,equip_level,equip_talent,equip_talent_rank) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        values
    )
    cursor.executemany(
        """INSERT INTO item_stats(item,type,stat,amount) VALUES (?,?,?,?)""",
        stats
    )

def insert_units(cursor, units):
    values = []
    stats = []
    talents = []

    for unit in units:
        values.append((
            unit.template_id,
            unit.name.id,
            unit.real_name,
            unit.image,
            unit.suffix.id,
            unit.school,
            unit.attack_type,
            unit.damage_type,
            unit.primary_stat,
            unit.beast,
            unit.undead,
            unit.bird
        ))

        for stat in range(len(unit.stat_modifiers)):
            stats.append((
                unit.template_id,
                unit.stat_modifiers[stat],
                unit.stat_modifier_operators[stat],
                unit.stat_modifier_values[stat]
            ))

        for talent in range(len(unit.talents)):
            talents.append((
                unit.template_id,
                "Talent",
                unit.talents[talent],
                unit.talent_ranks[talent],
                unit.talent_sources[talent]
            ))
        
        for power in range(len(unit.powers)):
            talents.append((
                unit.template_id,
                "Power",
                unit.powers[power],
                1,
                unit.power_sources[power]
            ))

    cursor.executemany(
        "INSERT INTO units(id,name,real_name,image,title,school,attack_type,dmg_type,primary_stat,beast_flag,undead_flag,bird_flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO unit_stats(unit,stat,operator,modifier) VALUES (?,?,?,?)""",
        stats
    )
    cursor.executemany(
        """INSERT INTO unit_talents(unit,type,talent,rank,source) VALUES (?,?,?,?,?)""",
        talents
    )


def insert_pets(cursor, pets):
    values = []
    talents = []
    powers = []

    for pet in pets:
        values.append((
            pet.template_id,
            pet.name.id,
            pet.real_name,
            pet.image,
            pet.max_strength,
            pet.max_agility,
            pet.max_will,
            pet.max_power,
            pet.max_guts,
            pet.max_guile,
            pet.max_grit,
            pet.max_hp,
            pet.item_flags
        ))

        for talent in pet.base_talents:
            talents.append((
                pet.template_id,
                talent
            ))

        for power in pet.base_powers:
            powers.append((
                pet.template_id,
                power
            ))
    
    cursor.executemany(
        "INSERT INTO pets(id,name,real_name,image,strength,agility,will,power,guts,guile,grit,hp,item_flags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO pet_talents(pet,talent) VALUES (?,?)""",
        talents
    )
    cursor.executemany(
        """INSERT INTO pet_powers(pet,power) VALUES (?,?)""",
        powers
    )


def insert_talents(cursor, talents):
    values = []
    descriptions = []

    for talent in talents:
        values.append((
            talent.template_id,
            talent.name.id,
            talent.real_name,
            talent.image,
            talent.rank_count
        ))

        for description in range(len(talent.descriptions)):
            descriptions.append((
                talent.template_id,
                talent.ranks[description],
                talent.descriptions[description].id,
                talent.unit_levels[description]
            ))
    
    cursor.executemany(
        "INSERT INTO talents(id,name,real_name,image,ranks) VALUES (?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO talent_ranks(talent,rank,description,level_req_unit) VALUES (?,?,?,?)""",
        descriptions
    )


def insert_powers(cursor, powers):
    values = []

    for power in powers:
        values.append((
            power.template_id,
            power.name.id,
            power.real_name,
            power.image,
            power.description.id,
            power.pvp_tag,
            power.target_type
        ))
    
    cursor.executemany(
        "INSERT INTO powers(id,name,real_name,image,description,pvp_tag,target_type) VALUES (?,?,?,?,?,?,?)",
        values
    )
