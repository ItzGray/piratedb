from enum import IntFlag

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
        apply_dmg_result = None
        dot_dmg_result = None
        trap_dmg_result = None
        summon_result = None
        buff_result = None
        for result in results:
            if result == None:
                continue

            try:
                damage_adjustments = result["m_pDamageAdjustments"]
                inherit_dmg_type = result["m_bInheritDamageType"]
            except:
                pass
            else:
                apply_dmg_result = result

            try:
                adjustments = result["m_pAdjustments"]
                effect_id = result["m_nEffectID"]
            except:
                pass
            else:
                dot_dmg_result = result

            try:
                modifiers = result["m_statModifiers"]
                template_id = result["m_nTemplateID"]
            except:
                pass
            else:
                trap_dmg_result = result

            try:
                link_to_player = result["m_bLinkToPlayer"]
                summon_level = result["m_nLevel"]
            except:
                pass
            else:
                summon_result = result

            try:
                result_target = result["m_resultTarget"]
                modifiers = result["m_modifiers"]
            except:
                pass
            else:
                buff_result = result
        
        self.power_dmg_type = ""
        self.dmg_adjustment_operators = []
        self.dmg_adjustment_stats = []
        self.dmg_adjustment_values = []
        if apply_dmg_result != None:
            if apply_dmg_result["m_bInheritDamageType"] == True:
                self.power_dmg_type = "Inherit"
            else:
                self.power_dmg_type = STATS[apply_dmg_result["m_nDamageType"]]
        
            damage_adjustments = apply_dmg_result["m_pDamageAdjustments"]
            adjustments = damage_adjustments["m_adjustments"]
            for adjustment in adjustments:
                try:
                    stat = STATS[adjustment["m_sStatName"]]
                except:
                    continue
                else:
                    self.dmg_adjustment_stats.append(stat)
                    self.dmg_adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                    self.dmg_adjustment_values.append(round(adjustment["m_fValue"], 2))
        
        self.dot_duration = -1
        self.dot_dmg_adjustment_stats = []
        self.dot_dmg_adjustment_operators = []
        self.dot_dmg_adjustment_values = []
        if dot_dmg_result != None:
            self.dot_duration = dot_dmg_result["m_nDuration"]
            dot_adjustments = dot_dmg_result["m_pAdjustments"]
            adjustments = dot_adjustments["m_adjustments"]
            for adjustment in adjustments:
                try:
                    stat = STATS[adjustment["m_sStatName"]]
                except:
                    continue
                else:
                    self.dot_dmg_adjustment_stats.append(stat)
                    self.dot_dmg_adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                    self.dot_dmg_adjustment_values.append(round(adjustment["m_fValue"], 2))

        self.trap_duration = -1
        self.stat_icon = ""
        self.trap_summoned = -1
        self.trap_dmg_adjustment_stats = []
        self.trap_dmg_adjustment_operators = []
        self.trap_dmg_adjustment_values = []
        if trap_dmg_result != None:
            self.trap_duration = trap_dmg_result["m_nDuration"]
            self.trap_summoned = trap_dmg_result["m_nTemplateID"]
            trap_modifiers = trap_dmg_result["m_statModifiers"]
            for modifier in trap_modifiers:
                self.stat_icon = STATS[modifier["m_nTargetStat"]]
                trap_adjustments = modifier["m_pAdjustments"]
                adjustments = trap_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        continue
                    else:
                        self.trap_dmg_adjustment_stats.append(stat)
                        self.trap_dmg_adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                        self.trap_dmg_adjustment_values.append(round(adjustment["m_fValue"], 2))

        self.summon_id = -1
        if summon_result != None:
            self.summon_id = summon_result["m_nTemplateID"]

        self.buff_percent = -1
        self.buff_duration = -1
        self.buff_type = ""
        self.buff_stats = []
        self.buff_adjustment_stats = []
        self.buff_adjustment_operators = []
        self.buff_adjustment_values = []
        if buff_result != None:
            self.buff_duration = buff_result["m_nDuration"]
            buff_modifiers = buff_result["m_modifiers"]
            for modifier in buff_modifiers:
                self.buff_stats.append(STATS[modifier["m_sStatName"]])
                buff_operator = MODIFIER_OPERATORS[modifier["m_eOperator"]]
                if buff_operator == "Multiply Add":
                    self.buff_type = "Debuff"
                else:
                    self.buff_type = "Buff"
                buff_adjustments = modifier["m_pAdjustments"]
                adjustments = buff_adjustments["m_adjustments"]
                for adjustment in adjustments:
                    try:
                        stat = STATS[adjustment["m_sStatName"]]
                    except:
                        self.buff_percent = adjustment["m_fValue"] * 100
                    else:
                        self.buff_adjustment_stats.append(stat)
                        self.buff_adjustment_operators.append(MODIFIER_OPERATORS[adjustment["m_eOperator"]])
                        self.buff_adjustment_values.append(round(adjustment["m_fValue"], 2))