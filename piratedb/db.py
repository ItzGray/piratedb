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

    adjustment_num  integer,
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
    subtype         text,
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

    bottom_left_icon text,
    bottom_right_icon text,
    upper_left_icon text,
    bottom_left_text integer,
    bottom_right_text integer,
    upper_left_text integer,

    foreign key(talent) references talents(id)
    foreign key(description)    references locale_en(id)
);

CREATE INDEX talent_rank_lookup ON talent_ranks(talent);

CREATE TABLE talent_stats (
    id              integer not null primary key,
    talent          integer not null,
    rank            integer,

    operator        text,
    stat            text,
    amount          integer,

    foreign key(talent) references talents(id)
);

CREATE TABLE units (
    id                  integer not null primary key,
    name                integer,
    real_name           text,
    image               text,

    title               integer,
    school              text,
    dmg_type            text,
    primary_stat        integer,
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


CREATE TABLE unit_tags (
    id       integer not null primary key,
    unit     integer not null,

    tag      text,

    foreign key(unit)   references units(id)
);


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
    for num in cache.lookup:
        if "<BR>" in cache.lookup[num]:
            cache.lookup[num] = cache.lookup[num].replace("<BR>", "")
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
    tags = []

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
        
        for tag in unit.flag_list:
            tags.append((
                unit.template_id,
                tag
            ))

    cursor.executemany(
        "INSERT INTO units(id,name,real_name,image,title,school,dmg_type,primary_stat,curve,kind) VALUES (?,?,?,?,?,?,?,?,?,?)",
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
    cursor.executemany(
        """INSERT INTO unit_tags(unit,tag) VALUES (?,?)""",
        tags
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
    stats = []

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
                talent.unit_levels[description],
                talent.rank_images[description][0],
                talent.rank_images[description][1],
                talent.rank_images[description][2],
                talent.rank_tooltips[description][0].id,
                talent.rank_tooltips[description][1].id,
                talent.rank_tooltips[description][2].id
            ))
            stats.append((
                talent.template_id,
                talent.ranks[description],
                talent.rank_operators[description],
                talent.rank_stats[description],
                talent.rank_values[description]
            ))
    
    cursor.executemany(
        "INSERT INTO talents(id,name,real_name,image,ranks) VALUES (?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO talent_ranks(talent,rank,description,level_req_unit,bottom_left_icon,bottom_right_icon,upper_left_icon,bottom_left_text,bottom_right_text,upper_left_text) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        descriptions
    )
    cursor.executemany(
        """INSERT INTO talent_stats(talent,rank,operator,stat,amount) VALUES (?,?,?,?,?)""",
        stats
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

        counts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        adjustment_count = 0
        for type in power.result_types:
            if type == 0:
                try:
                    for value in range(len(power.dmg_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "Damage",
                            power.dmg_adjustment_operators[counts[type]][value],
                            power.dmg_adjustment_stats[counts[type]][value],
                            power.dmg_adjustment_values[counts[type]][value]
                        ))
                    adjustment_count += 1
                except:
                    pass
                info.append((
                    power.template_id,
                    "Damage",
                    power.power_dmg_types[counts[type]],
                    -1,
                    "",
                    -1,
                    -1
                ))
            elif type == 1:
                try:
                    for value in range(len(power.dot_dmg_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "DoT",
                            power.dot_dmg_adjustment_operators[counts[type]][value],
                            power.dot_dmg_adjustment_stats[counts[type]][value],
                            power.dot_dmg_adjustment_values[counts[type]][value]
                        ))
                    adjustment_count += 1
                except:
                    pass
                info.append((
                    power.template_id,
                    "DoT",
                    power.dot_types[counts[type]],
                    power.dot_durations[counts[type]],
                    "",
                    -1,
                    -1
                ))
            elif type == 2:
                try:
                    for value in range(len(power.trap_dmg_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "Trap",
                            power.trap_dmg_adjustment_operators[counts[type]][value],
                            power.trap_dmg_adjustment_stats[counts[type]][value],
                            power.trap_dmg_adjustment_values[counts[type]][value]
                        ))
                    adjustment_count += 1
                except:
                    pass
                try:
                    info.append((
                        power.template_id,
                        "Trap",
                        "",
                        power.trap_durations[counts[type]],
                        power.stat_icons[counts[type]],
                        power.trap_summons[counts[type]].id,
                        -1
                    ))
                except:
                    pass
            elif type == 3:
                info.append((
                    power.template_id,
                    "Summon",
                    "",
                    -1,
                    "",
                    power.summon_ids[counts[type]],
                    -1
                ))
            elif type == 4:
                info.append((
                    power.template_id,
                    "Protect",
                    "",
                    power.protect_durations[counts[type]],
                    "",
                    -1,
                    power.protect_percents[counts[type]]
                ))
            elif type == 5:
                try:
                    for value in range(len(power.buff_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "Buff",
                            power.buff_adjustment_operators[counts[type]][value],
                            power.buff_adjustment_stats[counts[type]][value],
                            power.buff_adjustment_values[counts[type]][value]
                        ))
                        info.append((
                            power.template_id,
                            "Buff",
                            power.buff_types[value],
                            power.buff_durations[value],
                            power.buff_stats[value],
                            -1,
                            -1
                        ))
                        adjustment_count += 1
                except:
                    try:
                        for amount in range(power.buff_adjustment_count):
                            info.append((
                                power.template_id,
                                "Buff",
                                power.buff_types[counts[type] + amount],
                                power.buff_durations[counts[type] + amount],
                                power.buff_stats[counts[type] + amount],
                                -1,
                                power.buff_percents[counts[type] + amount]
                            ))
                    except:
                        pass
            elif type == 6:
                try:
                    for value in range(len(power.absorb_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "Absorb",
                            power.absorb_adjustment_operators[counts[type]][value],
                            power.absorb_adjustment_stats[counts[type]][value],
                            power.absorb_adjustment_values[counts[type]][value]
                        ))
                    adjustment_count += 1
                except:
                    pass
                info.append((
                    power.template_id,
                    "Absorb",
                    "",
                    power.absorb_durations[counts[type]],
                    power.absorb_values[counts[type]],
                    -1,
                    -1
                ))
            elif type == 7:
                info.append((
                    power.template_id,
                    "Ability",
                    "",
                    -1,
                    "",
                    power.ability_ids[counts[type]],
                    -1
                ))
            elif type == 8:
                try:
                    for value in range(len(power.heal_adjustment_values[counts[type]])):
                        adjustments.append((
                            power.template_id,
                            adjustment_count,
                            "Heal",
                            power.heal_adjustment_operators[counts[type]][value],
                            power.heal_adjustment_stats[counts[type]][value],
                            power.heal_adjustment_values[counts[type]][value]
                        ))
                    adjustment_count += 1
                    info.append((
                        power.template_id,
                        "Heal",
                        "",
                        -1,
                        "",
                        -1,
                        -1,
                    ))
                except:
                    pass
            
            counts[type] += 1
    
    cursor.executemany(
        "INSERT INTO powers(id,name,real_name,image,description,pvp_tag,target_type) VALUES (?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        "INSERT INTO power_adjustments(power,adjustment_num,type,operator,stat,amount) VALUES (?,?,?,?,?,?)",
        adjustments
    )
    cursor.executemany(
        "INSERT INTO power_info(power,type,subtype,duration,stat,summoned,percent) VALUES (?,?,?,?,?,?,?)",
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
