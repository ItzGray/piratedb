import sqlite3
from sqlite3 import Cursor

from .lang_files import LangCache

INIT_QUERIES = """CREATE TABLE locale_en (
    id   integer not null primary key,
    data text not null
);

CREATE INDEX en_name_lookup ON locale_en(data);

CREATE TABLE curves (
    id                 integer not null primary key,
    real_name          text
);

CREATE TABLE curve_points (
    id                 integer not null primary key,
    curve              integer not null,
    stat               text,

    type               text,
    level              integer,
    value              integer
);

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

CREATE TABLE power_adjustments (
    id              integer not null primary key,
    power           integer,

    type            text,
    operator        text,
    stat            text,
    amount          integer,

    foreign key(power)  references powers(id)
);

CREATE TABLE power_info (
    id              integer not null primary key,
    power           integer,

    type            text,
    dmg_type        text,
    duration        integer,
    stat            text,
    summoned        integer,
    percent         integer,

    foreign key(power)  references powers(id)
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
    dmg_type            text,
    primary_stat        integer,
    beast_flag          integer,
    undead_flag         integer,
    bird_flag           integer,
    curve               integer,
    kind                text,

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

    stat     text,
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
    name            integer,
    real_name       text,
    image           text,

    is_grant        integer,
    rarity          integer,
    
    foreign key(name)   references locale_en(id)
);

CREATE TABLE pet_powers (
    id              integer not null primary key,
    name            integer,
    real_name       text,
    image           text,

    is_grant        integer,
    rarity          integer,
    power           integer,
    
    foreign key(name)   references locale_en(id)
);


CREATE TABLE indiv_pet_talents (
    id              integer not null primary key,
    pet             integer not null,

    talent          integer not null,

    foreign key(pet)    references pets(id)
);

CREATE INDEX indiv_pet_talent_lookup ON indiv_pet_talents(pet);


CREATE TABLE indiv_pet_powers (
    id              integer not null primary key,
    pet             integer not null,

    power           integer not null,

    foreign key(pet)    references pets(id)
);

CREATE INDEX indiv_pet_power_lookup ON indiv_pet_powers(pet);

"""


def _progress(_status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')


def build_db(state, curves, items, units, pets, talents, powers, pet_talents, pet_powers, out):
    mem = sqlite3.connect(":memory:")
    cursor = mem.cursor()

    initialize(cursor)
    insert_locale_data(cursor, state.cache)
    insert_curves(cursor, curves)
    insert_items(cursor, items)
    insert_units(cursor, units)
    insert_pets(cursor, pets)
    insert_talents(cursor, talents)
    insert_powers(cursor, powers)
    insert_pet_talents(cursor, pet_talents)
    insert_pet_powers(cursor, pet_powers)
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

def insert_curves(cursor, curves):
    values = []
    points = []

    for curve in curves:
        values.append((
            curve.template_id,
            curve.real_name
        ))

        for point in range(len(curve.curve_points)):
            points.append((
                curve.template_id,
                curve.curve_stats[point],
                "Regular",
                curve.curve_points[point][0],
                curve.curve_points[point][1]
            ))
        
        for bonus in range(len(curve.curve_bonus_points)):
            points.append((
                curve.template_id,
                curve.curve_bonus_stats[bonus],
                "Bonus",
                curve.curve_bonus_points[bonus][0],
                curve.curve_bonus_points[bonus][1]
            ))
        
    cursor.executemany(
        """INSERT INTO curves(id,real_name) VALUES (?,?)""",
        values
    )

    cursor.executemany(
        """INSERT INTO curve_points(curve,stat,type,level,value) VALUES (?,?,?,?,?)""",
        points
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
            unit.damage_type,
            unit.primary_stat,
            unit.beast,
            unit.undead,
            unit.bird,
            unit.curve,
            unit.unit_type
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
        "INSERT INTO units(id,name,real_name,image,title,school,dmg_type,primary_stat,beast_flag,undead_flag,bird_flag,curve,kind) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
        """INSERT INTO indiv_pet_talents(pet,talent) VALUES (?,?)""",
        talents
    )
    cursor.executemany(
        """INSERT INTO indiv_pet_powers(pet,power) VALUES (?,?)""",
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
    adjustments = []
    info = []

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

        if len(power.dmg_adjustment_stats) > 0:
            for stat in range(len(power.dmg_adjustment_stats)):
                adjustments.append((
                    power.template_id,
                    "Damage",
                    power.dmg_adjustment_operators[stat],
                    power.dmg_adjustment_stats[stat],
                    power.dmg_adjustment_values[stat]
                ))
            info.append((
                power.template_id,
                "Damage",
                power.power_dmg_type,
                -1,
                "",
                -1,
                -1
            ))

        if power.dot_duration != -1:
            for stat in range(len(power.dot_dmg_adjustment_stats)):
                adjustments.append((
                    power.template_id,
                    "DoT",
                    power.dot_dmg_adjustment_operators[stat],
                    power.dot_dmg_adjustment_stats[stat],
                    power.dot_dmg_adjustment_values[stat]
                ))
            info.append((
                power.template_id,
                "DoT",
                "",
                power.dot_duration,
                "",
                -1,
                -1
            ))
        
        if power.trap_duration != -1:
            for stat in range(len(power.trap_dmg_adjustment_stats)):
                adjustments.append((
                    power.template_id,
                    "Trap",
                    power.trap_dmg_adjustment_operators[stat],
                    power.trap_dmg_adjustment_stats[stat],
                    power.trap_dmg_adjustment_values[stat]
                ))
            info.append((
                power.template_id,
                "Trap",
                "",
                power.trap_duration,
                power.stat_icon,
                power.trap_summoned,
                -1
            ))

        if power.summon_id != -1:
            info.append((
                power.template_id,
                "Summon",
                "",
                -1,
                "",
                power.summon_id,
                -1
            ))
        
        if power.buff_duration != -1:
            for stat in range(len(power.buff_adjustment_stats)):
                adjustments.append((
                    power.template_id,
                    power.buff_type,
                    power.buff_adjustment_operators[stat],
                    power.buff_adjustment_stats[stat],
                    power.buff_adjustment_values[stat]
                ))
            for buff in power.buff_stats:
                info.append((
                    power.template_id,
                    power.buff_type,
                    "",
                    power.buff_duration,
                    buff,
                    -1,
                    power.buff_percent
                ))
    
    cursor.executemany(
        "INSERT INTO powers(id,name,real_name,image,description,pvp_tag,target_type) VALUES (?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        "INSERT INTO power_adjustments(power,type,operator,stat,amount) VALUES (?,?,?,?,?)",
        adjustments
    )
    cursor.executemany(
        "INSERT INTO power_info(power,type,dmg_type,duration,stat,summoned,percent) VALUES (?,?,?,?,?,?,?)",
        info
    )

def insert_pet_talents(cursor, pet_talents):
    values = []
    
    for pet_talent in pet_talents:
        values.append((
            pet_talent.template_id,
            pet_talent.name.id,
            pet_talent.real_name,
            pet_talent.image,
            pet_talent.grant,
            pet_talent.rarity
        ))

    cursor.executemany(
        "INSERT INTO pet_talents(id,name,real_name,image,is_grant,rarity) VALUES (?,?,?,?,?,?)",
        values
    )

def insert_pet_powers(cursor, pet_powers):
    values = []
    
    for pet_power in pet_powers:
        values.append((
            pet_power.template_id,
            pet_power.name.id,
            pet_power.real_name,
            pet_power.image,
            pet_power.grant,
            pet_power.rarity,
            pet_power.power
        ))

    cursor.executemany(
        "INSERT INTO pet_powers(id,name,real_name,image,is_grant,rarity,power) VALUES (?,?,?,?,?,?,?)",
        values
    )
