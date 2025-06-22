from enum import IntFlag
from katsuba.utils import djb2 # type: ignore

from .state import State
from .utils import STATS, MODIFIER_OPERATORS

def is_power_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adj_list = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except KeyError:
        return False
    
    is_power = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"CombatAbilityBehavior":
            is_power = True
            break
    return is_power

DOT_TYPES = {
    487097: "Bleed",
    487099: "Heal",
    490762: "Poison",
    490791: "Bleed",
}

class Power:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        self.description = state.make_desc_lang_key(obj)
        behaviors = obj["m_behaviors"]
        combat_ability_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'CombatAbilityBehavior':
                    combat_ability_behavior = behavior
                     
        self.pvp_tag = combat_ability_behavior["m_allowedIn"]
        self.target_type = combat_ability_behavior["m_targetType"]
        target_results = combat_ability_behavior["m_targetResults"]
        results = target_results["m_results"]

        # Oh dear
        self.result_types = []
        self.power_dmg_types = []
        self.dmg_adjustment_operators = []
        self.dmg_adjustment_stats = []
        self.dmg_adjustment_values = []
        self.dot_durations = []
        self.dot_types = []
        self.dot_dmg_adjustment_stats = []
        self.dot_dmg_adjustment_operators = []
        self.dot_dmg_adjustment_values = []
        self.trap_durations = []
        self.stat_icons = []
        self.trap_summons = []
        self.trap_dmg_adjustment_stats = []
        self.trap_dmg_adjustment_operators = []
        self.trap_dmg_adjustment_values = []
        self.summon_ids = []
        self.protect_durations = []
        self.protect_percents = []
        self.buff_percents = []
        self.buff_durations = []
        self.buff_types = []
        self.buff_stats = []
        self.buff_adjustment_stats = []
        self.buff_adjustment_operators = []
        self.buff_adjustment_values = []
        self.absorb_durations = []
        self.absorb_values = []
        self.absorb_adjustment_stats = []
        self.absorb_adjustment_operators = []
        self.absorb_adjustment_values = []
        self.ability_ids = []
        self.heal_adjustment_stats = []
        self.heal_adjustment_operators = []
        self.heal_adjustment_values = []
        for result in results:
            if result == None:
                continue
            
            adjustment_values = []
            adjustment_operators = []
            adjustment_stats = []

            if result.type_hash == djb2("class ResApplyDamage"):
                self.result_types.append(0)
                if result["m_bInheritDamageType"] == True:
                    self.power_dmg_types.append("Inherit")
                else:
                    self.power_dmg_types.append(STATS[result["m_nDamageType"]])
        
                damage_adjustments = result["m_pDamageAdjustments"]
                adjustments = damage_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        if adjustment.type_hash == djb2("class ValueAdjustment"):
                            try:
                                adjustment_values[-1] = adjustment_values[-1] + adjustment["m_fValue"]
                            except:
                                pass
                        elif adjustment.type_hash == djb2("class DamageTypeAdjustment"):
                            rounded_val = round(adjustment["m_fValue"], 3)
                            if rounded_val != 0:
                                adjustment_stats.append("Weapon Power")
                                adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                                adjustment_values.append(rounded_val)
                        elif adjustment.type_hash == djb2("class PrimaryStatAdjustment"):
                            rounded_val = round(adjustment["m_fValue"], 3)
                            if rounded_val != 0:
                                adjustment_stats.append("Primary Stat")
                                adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                                adjustment_values.append(rounded_val)
                    else:
                        rounded_val = round(adjustment["m_fValue"], 3)
                        if rounded_val != 0:
                            adjustment_stats.append(stat)
                            adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                            adjustment_values.append(rounded_val)
                if len(adjustment_values) > 0:
                    self.dmg_adjustment_stats.append(tuple(adjustment_stats))
                    self.dmg_adjustment_operators.append(tuple(adjustment_operators))
                    self.dmg_adjustment_values.append(tuple(adjustment_values))

            elif result.type_hash == djb2("class ResCombatPulseEffect"):
                self.result_types.append(1)
                self.dot_durations.append(result["m_nDuration"])
                try:
                    self.dot_types.append(DOT_TYPES[result["m_nEffectID"]])
                except:
                    self.dot_types.append("Unknown")
                dot_adjustments = result["m_pAdjustments"]
                adjustments = dot_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        continue
                    else:
                        rounded_val = round(adjustment["m_fValue"], 3)
                        if rounded_val != 0:
                            adjustment_stats.append(stat)
                            adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                            adjustment_values.append(rounded_val)
                if len(adjustment_values) > 0:
                    self.dot_dmg_adjustment_stats.append(tuple(adjustment_stats))
                    self.dot_dmg_adjustment_operators.append(tuple(adjustment_operators))
                    self.dot_dmg_adjustment_values.append(tuple(adjustment_values))

            elif result.type_hash == djb2("class ResSummonProp"):
                self.result_types.append(2)
                self.trap_durations.append(result["m_nDuration"])
                self.trap_summons.append(result["m_nTemplateID"])
                trap_modifiers = result["m_statModifiers"]
                for modifier in trap_modifiers:
                    adjustment_values = []
                    adjustment_operators = []
                    adjustment_stats = []
                    self.stat_icons.append(STATS[modifier["m_nTargetStat"]])
                    trap_adjustments = modifier["m_pAdjustments"]
                    adjustments = trap_adjustments["m_adjustments"]
                    for adjustment in adjustments:
                        try:
                            stat = STATS[adjustment["m_sStatName"]]
                        except:
                            continue
                        else:
                            rounded_val = round(adjustment["m_fValue"], 3)
                            if rounded_val != 0:
                                adjustment_stats.append(stat)
                                adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                                adjustment_values.append(rounded_val)
                if len(adjustment_values) > 0:
                    self.trap_dmg_adjustment_stats.append(tuple(adjustment_stats))
                    self.trap_dmg_adjustment_operators.append(tuple(adjustment_operators))
                    self.trap_dmg_adjustment_values.append(tuple(adjustment_values))

            elif result.type_hash == djb2("class ResSummonHenchman"):
                self.result_types.append(3)
                self.summon_ids.append(result["m_nTemplateID"])

            elif result.type_hash == djb2("class ResCombatDamageModifyEffect"):
                self.result_types.append(4)
                self.protect_durations.append(result["m_nDuration"])
                modify_adjustments = result["m_pModifyAdjustments"]
                adjustments = modify_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    self.protect_percents.append(adjustment["m_fValue"] * 100)

            elif result.type_hash == djb2("class ResCombatEffect") or result.type_hash == djb2("class ResCombatStatusEffect"):
                self.result_types.append(5)
                effect_id = result["m_nEffectID"]
                buff_modifiers = result["m_modifiers"]
                buff_type = "Buff"
                buff_operator = ""
                for modifier in buff_modifiers:
                    self.buff_durations.append(result["m_nDuration"])
                    self.buff_stats.append(STATS[modifier["m_sStatName"]])
                    buff_operator = MODIFIER_OPERATORS[modifier["m_eOperator"]]
                    if buff_operator == "Multiply Add":
                        buff_type = "Debuff"
                    else:
                        buff_type = "Buff"
                    buff_adjustments = modifier["m_pAdjustments"]
                    adjustments = buff_adjustments["m_adjustments"]
                    for adjustment in adjustments:
                        try:
                            stat = STATS[adjustment["m_sStatName"]]
                        except:
                            value = round(adjustment["m_fValue"] * 100, 3)
                            if value < 0:
                                buff_type = "Debuff"
                                value = value * -1
                            elif buff_type == "Debuff":
                                value = 100 - value
                            self.buff_percents.append(value)
                        else:
                            rounded_val = round(adjustment["m_fValue"], 3)
                            if rounded_val != 0:
                                adjustment_stats.append(stat)
                                adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                                adjustment_values.append(rounded_val)
                                self.buff_percents.append(-1)
                    if effect_id == 656655:
                        buff_type = "Curse"
                    self.buff_types.append(buff_type)
                if buff_operator == "":
                    self.buff_stats.append("Unknown")
                    self.buff_percents.append(-1)
                    self.buff_durations.append(result["m_nDuration"])
                    self.buff_types.append(buff_type)
                if len(adjustment_values) > 0:
                    self.buff_adjustment_stats.append(tuple(adjustment_stats))
                    self.buff_adjustment_operators.append(tuple(adjustment_operators))
                    self.buff_adjustment_values.append(tuple(adjustment_values))

            elif result.type_hash == djb2("class ResCombatSpongeEffect"):
                self.result_types.append(6)
                sponge_adjustments = result["m_pSpongeAdjustments"]
                adjustments = sponge_adjustments["m_adjustments"]
                self.absorb_durations.append(result["m_nDuration"])
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        self.absorb_values.append(adjustment["m_fValue"])
                    else:
                        rounded_val = round(adjustment["m_fValue"], 3)
                        if rounded_val != 0:
                            adjustment_stats.append(stat)
                            adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                            adjustment_values.append(rounded_val)
                            self.absorb_values.append(-1)
                if len(adjustment_values) > 0:
                    self.absorb_adjustment_stats.append(tuple(adjustment_stats))
                    self.absorb_adjustment_operators.append(tuple(adjustment_operators))
                    self.absorb_adjustment_values.append(tuple(adjustment_values))

            elif result.type_hash == djb2("class ResActivateAbility"):
                self.result_types.append(7)
                self.ability_ids.append(result["m_nAbilityID"])

            elif result.type_hash == djb2("class ResApplyHeal"):
                self.result_types.append(8)
                heal_adjustments = result["m_pAdjustments"]
                adjustments = heal_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        continue
                    else:
                        if adjustment.type_hash == djb2("class RPSValueAdjustment"):
                            # Handle this later
                            continue
                        rounded_val = round(adjustment["m_fValue"], 3)
                        if rounded_val != 0:
                            adjustment_stats.append(stat)
                            adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                            adjustment_values.append(rounded_val)
                if len(adjustment_values) > 0:
                    self.heal_adjustment_stats.append(tuple(adjustment_stats))
                    self.heal_adjustment_operators.append(tuple(adjustment_operators))
                    self.heal_adjustment_values.append(tuple(adjustment_values))