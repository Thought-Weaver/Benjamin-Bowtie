from __future__ import annotations

import re

from features.shared.attributes import Attributes
from features.shared.enums import ClassTag, Summons
from features.shared.statuseffect import StatusEffectKey
from types import MappingProxyType
from enum import StrEnum

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.item import Item
    from features.npcs.npc import NPC
    from features.player import Player

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class EffectType(StrEnum):
    Unknown = "Unknown"

    CleanseStatusEffects = "CleanseStatusEffects"

    ConMod = "ConMod"
    StrMod = "StrMod"
    DexMod = "DexMod"
    IntMod = "IntMod"
    LckMod = "LckMod"
    MemMod = "MemMod"

    # Everything in this group is associated with percent effect values
    DmgReflect = "DmgReflect"
    DmgResist = "DmgResist"
    DmgVulnerability = "DmgVulnerability"
    DmgBuff = "DmgBuff"
    DmgBuffSelfMaxHealth = "DmgBuffSelfMaxHealth"
    DmgBuffSelfRemainingHealth = "DmgBuffSelfRemainingHealth"
    DmgBuffOtherMaxHealth = "DmgBuffOtherMaxHealth"
    DmgBuffOtherRemainingHealth = "DmgBuffOtherRemainingHealth"
    DmgBuffLegends = "DmgBuffLegends"
    DmgBuffPoisoned = "DmgBuffPoisoned"
    DmgBuffBleeding = "DmgBuffBleeding"

    DmgBuffFromStr = "DmgBuffFromStr"
    DmgBuffFromDex = "DmgBuffFromDex"
    DmgBuffFromInt = "DmgBuffFromInt"
    DmgBuffFromLck = "DmgBuffFromLck"

    RestoreArmor = "RestoreArmor"
    RestorePercentArmor = "RestorePercentArmor"

    PiercingDmg = "PiercingDmg"
    PiercingPercentDmg = "PiercingPercentDmg"
    SplashDmg = "SplashDmg"
    SplashPercentMaxDmg = "SplashPercentMaxDmg"

    # Everything in this group is associated with percent effect values
    CritDmgBuff = "CritDmgBuff"
    CritDmgReduction = "CritDmgReduction"
    HealthSteal = "HealthSteal"
    ManaSteal = "ManaSteal"

    AdjustedCDs = "AdjustedCDs"

    # Everything in this group is associated with percent effect values
    ChanceStatusEffect = "ChanceStatusEffect"
    ResistStatusEffect = "ResistStatusEffect"

    RestoreHealth = "RestoreHealth"
    RestorePercentHealth = "RestorePercentHealth"
    RestoreMana = "RestoreMana"
    RestorePercentMana = "RestorePercentMana"

    # Everything in this group is associated with percent effect values
    AdjustedManaCosts = "AdjustedManaCosts"
    HealingAbilityBuff = "HealingAbilityBuff"
    AdditionalXP = "AdditionalXP"
    PotionMod = "PotionMod"
    
    Damage = "Damage"
    
    ResurrectOnce = "ResurrectOnce"
    Summon = "Summon"
    GrantAbility = "GrantAbility"


class ConditionType(StrEnum):
    Unknown = "Unknown"

    # These conditions are what I'll use to split between doing certain item effects
    # on some types of items versus others, allowing gems to be more versatile.
    IsItemInHand = "IsItemInHand"
    IsItemArmor = "IsItemArmor"

    IsBelowPercentHealth = "IsBelowPercentHealth"
    IsAbovePercentHealth = "IsAbovePercentHealth"
    IsFullHealth = "IsFullHealth"


class ItemEffectCategory(StrEnum):
    Permanent = "Permanent"
    OnTurnStart = "OnTurnStart"
    OnTurnEnd = "OnTurnEnd"
    OnDamaged = "OnDamaged"
    OnSuccessfulAbilityUsed = "OnSuccessfulAbilityUsed"
    OnSuccessfulAttack = "OnSuccessfulAttack"
    OnAttacked = "OnAttacked"
    OnAbilityUsedAgainst = "OnAbilityUsedAgainst"

# -----------------------------------------------------------------------------
# PRIORITY DICT
# -----------------------------------------------------------------------------

EFFECT_PRIORITY: MappingProxyType[EffectType, int] = MappingProxyType({
    EffectType.CleanseStatusEffects: 0,

    EffectType.ConMod: 1,
    EffectType.StrMod: 2,
    EffectType.DexMod: 3,
    EffectType.IntMod: 4,
    EffectType.LckMod: 5,
    EffectType.MemMod: 6,

    EffectType.DmgReflect: 7,
    EffectType.DmgResist: 8,
    EffectType.DmgVulnerability: 9,
    EffectType.DmgBuff: 10,
    EffectType.DmgBuffSelfMaxHealth: 11,
    EffectType.DmgBuffSelfRemainingHealth: 12,
    EffectType.DmgBuffOtherMaxHealth: 13,
    EffectType.DmgBuffOtherRemainingHealth: 14,
    EffectType.DmgBuffLegends: 15,
    EffectType.DmgBuffPoisoned: 16,
    EffectType.DmgBuffBleeding: 17,

    EffectType.DmgBuffFromStr: 18,
    EffectType.DmgBuffFromDex: 19,
    EffectType.DmgBuffFromInt: 20,
    EffectType.DmgBuffFromLck: 21,

    EffectType.RestoreArmor: 22,
    EffectType.RestorePercentArmor: 23,
    
    EffectType.PiercingDmg: 24,
    EffectType.PiercingPercentDmg: 25,
    EffectType.SplashDmg: 26,
    EffectType.SplashPercentMaxDmg: 27,

    EffectType.CritDmgBuff: 28,
    EffectType.CritDmgReduction: 29,

    EffectType.HealthSteal: 30,
    EffectType.ManaSteal: 31,

    EffectType.AdjustedCDs: 32,

    EffectType.ChanceStatusEffect: 33,
    EffectType.ResistStatusEffect: 34,

    EffectType.RestoreHealth: 35,
    EffectType.RestorePercentHealth: 36,
    EffectType.RestoreMana: 37,
    EffectType.RestorePercentMana: 38,

    EffectType.AdjustedManaCosts: 39,
    EffectType.HealingAbilityBuff: 40,
    EffectType.AdditionalXP: 41,
    EffectType.PotionMod: 42,

    EffectType.Damage: 43,

    EffectType.ResurrectOnce: 44,
    EffectType.Summon: 45,
    EffectType.GrantAbility: 46,
})

# -----------------------------------------------------------------------------
# EFFECT CLASS
# -----------------------------------------------------------------------------

class Effect():
    def __init__(self, effect_type: EffectType, effect_value: int | float, effect_time: int, conditions: List[ConditionType], condition_values: List[int | float], associated_status_effect: StatusEffectKey | None=None, summon: Summons | None=None, granted_ability: str | None=None):
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.effect_time = effect_time
        self.conditions = conditions
        self.condition_values = condition_values
        self.associated_status_effect = associated_status_effect
        self.summon = summon
        self.granted_ability = granted_ability

    @staticmethod
    def load_from_state(effect_data: dict):
        return Effect(
            effect_data.get("effect_type", ""),
            effect_data.get("effect_value", 0),
            effect_data.get("effect_time", 0),
            effect_data.get("conditions", []),
            effect_data.get("condition_values", []),
            effect_data.get("associated_status_effect", None),
            effect_data.get("summon", None),
            effect_data.get("granted_ability", None)
        )

    def meets_conditions(self, entity: Player | NPC, item: Item):
        conditions_met = True
        for i, condition in enumerate(self.conditions):
            if condition == ConditionType.IsAbovePercentHealth:
                conditions_met &= entity.get_expertise().hp / entity.get_expertise().max_hp > self.condition_values[i]
            if condition == ConditionType.IsBelowPercentHealth:
                conditions_met &= entity.get_expertise().hp / entity.get_expertise().max_hp < self.condition_values[i]
            if condition == ConditionType.IsFullHealth:
                conditions_met &= entity.get_expertise().hp == entity.get_expertise().max_hp
            if condition == ConditionType.IsItemArmor:
                class_tags = item.get_class_tags()
                conditions_met &= (
                    ClassTag.Equipment.Equipment in class_tags and 
                    not ClassTag.Equipment.MainHand in class_tags and
                    not ClassTag.Equipment.OffHand in class_tags
                )
            if condition == ConditionType.IsItemInHand:
                class_tags = item.get_class_tags()
                conditions_met &= (
                    ClassTag.Equipment.MainHand in class_tags or
                    ClassTag.Equipment.OffHand in class_tags
                )
        return conditions_met

    def get_descriptive_name(self) -> str:
        match self.effect_type:
            case EffectType.CleanseStatusEffects:
                return "Cleanse Statuses"
            case EffectType.ConMod:
                return "Augment Constitution"
            case EffectType.StrMod:
                return "Augment Strength"
            case EffectType.DexMod:
                return "Augment Dexterity"
            case EffectType.IntMod:
                return "Augment Intelligence"
            case EffectType.LckMod:
                return "Augment Luck"
            case EffectType.MemMod:
                return "Augment Memory"
            case EffectType.DmgReflect:
                return "Damage Reflect"
            case EffectType.DmgResist:
                return "Damage Resist"
            case EffectType.DmgVulnerability:
                return "Damage Vulnerability"
            case EffectType.DmgBuff:
                return "Damage Buff"
            case EffectType.DmgBuffSelfMaxHealth:
                return "Damage Buff (% Max Health)"
            case EffectType.DmgBuffSelfRemainingHealth:
                return "Damage Buff (% Remaining Health)"
            case EffectType.DmgBuffOtherMaxHealth:
                return "Damage Buff (% Enemy Max Health)"
            case EffectType.DmgBuffOtherRemainingHealth:
                return "Damage Buff (% Enemy Remaining Health)"
            case EffectType.DmgBuffLegends:
                return "Damage Buff (Against Legendaries)"
            case EffectType.DmgBuffPoisoned:
                return "Damage Buff (Against Poisoned)"
            case EffectType.DmgBuffBleeding:
                return "Damage Buff (Against Bleeding)"
            case EffectType.DmgBuffFromStr:
                return "Damage Scaling (Str)"
            case EffectType.DmgBuffFromDex:
                return "Damage Scaling (Dex)"
            case EffectType.DmgBuffFromInt:
                return "Damage Scaling (Int)"
            case EffectType.RestoreArmor:
                return "Restore Armor"
            case EffectType.RestorePercentArmor:
                return "Restore % Armor"
            case EffectType.PiercingDmg:
                return "Piercing Damage"
            case EffectType.PiercingPercentDmg:
                return "% Piercing Damage"
            case EffectType.SplashDmg:
                return "Splash Damage"
            case EffectType.SplashPercentMaxDmg:
                return "% Splash Damage"
            case EffectType.CritDmgBuff:
                return "Augment Crit Effect"
            case EffectType.CritDmgReduction:
                return "Crit Damage Reduction"
            case EffectType.HealthSteal:
                return "Steal Health"
            case EffectType.ManaSteal:
                return "Steal Mana"
            case EffectType.AdjustedCDs:
                return "Augment Cooldowns"
            # TODO: Could abstract this to something shared between this function
            # and the string formatter below
            case EffectType.ChanceStatusEffect:
                se_key: StatusEffectKey | None = self.associated_status_effect
                if se_key == StatusEffectKey.Poisoned:
                    return "Poisoned Chance"
                elif se_key == StatusEffectKey.Bleeding:
                    return "Bleeding Chance"
                elif se_key == StatusEffectKey.TurnSkipChance:
                    return "Faltering Chance"
                elif se_key == StatusEffectKey.Taunted:
                    return "Taunted Chance"
                elif se_key == StatusEffectKey.CannotTarget:
                    return "Convinced Chance"
                elif se_key == StatusEffectKey.Charmed:
                    return "Charmed Chance"
                elif se_key == StatusEffectKey.CannotAttack:
                    return "Atrophied Chance"
                elif se_key == StatusEffectKey.Sleeping:
                    return "Sleeping Chance"
                elif se_key == StatusEffectKey.Decaying:
                    return "Decaying"
                elif se_key == StatusEffectKey.Undying:
                    return "Undying"
                elif se_key == StatusEffectKey.CannotUseAbilities:
                    return "Enfeebled Chance"
                elif se_key == StatusEffectKey.BonusDamageOnAttack:
                    return "Patient Chance"
                elif se_key == StatusEffectKey.StackingDamage:
                    return "Reverberating Chance"
                elif se_key == StatusEffectKey.Marked:
                    return "Marked Chance"
                elif se_key == StatusEffectKey.FixedDmgTick:
                    return "Echoing Chance"
            case EffectType.ResistStatusEffect:
                se_key: StatusEffectKey | None = self.associated_status_effect
                if se_key == StatusEffectKey.Poisoned:
                    return "Resist Poisoned Chance"
                elif se_key == StatusEffectKey.Bleeding:
                    return "Resist Bleeding Chance"
                elif se_key == StatusEffectKey.TurnSkipChance:
                    return "Resist Faltering Chance"
                elif se_key == StatusEffectKey.Taunted:
                    return "Resist Taunted Chance"
                elif se_key == StatusEffectKey.CannotTarget:
                    return "Resist Convinced Chance"
                elif se_key == StatusEffectKey.Charmed:
                    return "Resist Charmed Chance"
                elif se_key == StatusEffectKey.CannotAttack:
                    return "Resist Atrophied Chance"
                elif se_key == StatusEffectKey.Sleeping:
                    return "Resist Sleeping Chance"
                elif se_key == StatusEffectKey.Decaying:
                    return "Resist Decaying Chance"
                elif se_key == StatusEffectKey.CannotUseAbilities:
                    return "Resist Enfeebled Chance"
                elif se_key == StatusEffectKey.BonusDamageOnAttack:
                    return "Resist Patient Chance"
                elif se_key == StatusEffectKey.StackingDamage:
                    return "Resist Reverberating Chance"
                elif se_key == StatusEffectKey.Marked:
                    return "Resist Marked Chance"
                elif se_key == StatusEffectKey.FixedDmgTick:
                    return "Resist Echoing Chance"
            case EffectType.RestoreHealth:
                return "Restore Health"
            case EffectType.RestorePercentHealth:
                return "Restore % Health"
            case EffectType.RestoreMana:
                return "Restore Mana"
            case EffectType.RestorePercentMana:
                return "Restore % Mana"
            case EffectType.AdjustedManaCosts:
                return "Augment Mana Costs"
            case EffectType.HealingAbilityBuff:
                return "Augment Healing Abilities"
            case EffectType.AdditionalXP:
                return "Additional XP"
            case EffectType.PotionMod:
                return "Augment Potion Effectiveness"
            case EffectType.Damage:
                return "Cause Damage"
            case EffectType.ResurrectOnce:
                return "Resurrect Once"
            case EffectType.Summon:
                return "Summon"
            case EffectType.GrantAbility:
                return "Grant Ability"
        return "Unknown"

    def camel_case_split(self, string: str):
        matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", string)
        return [m.group(0) for m in matches]

    def __str__(self, filter_condition: ConditionType | None=None):
        display_string = ""

        if self.effect_type == EffectType.CleanseStatusEffects:
            display_string += f"Cleanses Status Effects"

        if self.effect_type == EffectType.ConMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Constitution"
        if self.effect_type == EffectType.StrMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Strength"
        if self.effect_type == EffectType.DexMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Dexterity"
        if self.effect_type == EffectType.IntMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Intelligence"
        if self.effect_type == EffectType.LckMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Luck"
        if self.effect_type == EffectType.MemMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} Memory"

        if self.effect_type == EffectType.DmgReflect:
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Reflected"
        if self.effect_type == EffectType.DmgResist:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Resist"
        if self.effect_type == EffectType.DmgVulnerability:
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Vulnerability"
        if self.effect_type == EffectType.DmgBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Dealt"
        if self.effect_type == EffectType.DmgBuffSelfMaxHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Max Health as Damage"
        if self.effect_type == EffectType.DmgBuffSelfRemainingHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Remaining Health as Damage"
        if self.effect_type == EffectType.DmgBuffOtherMaxHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Enemy Max Health as Damage"
        if self.effect_type == EffectType.DmgBuffOtherRemainingHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Enemy Remaining Health as Damage"
        if self.effect_type == EffectType.DmgBuffLegends:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Against Legendaries"
        if self.effect_type == EffectType.DmgBuffPoisoned:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Against Poisoned Enemies"
        if self.effect_type == EffectType.DmgBuffBleeding:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Against Bleeding Enemies"

        if self.effect_type == EffectType.DmgBuffFromStr:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Str"
        if self.effect_type == EffectType.DmgBuffFromDex:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Dex"
        if self.effect_type == EffectType.DmgBuffFromInt:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Int"
        if self.effect_type == EffectType.DmgBuffFromLck:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Lck"
        
        if self.effect_type == EffectType.RestoreArmor:
            display_string += f"Restore {int(self.effect_value)} Armor"
        if self.effect_type == EffectType.RestorePercentArmor:
            display_string += f"Restore {round(self.effect_value * 100, 2)}% Armor"

        if self.effect_type == EffectType.PiercingDmg:
            display_string += f"{int(self.effect_value)} Piercing Damage"
        if self.effect_type == EffectType.PiercingPercentDmg:
            display_string += f"{round(self.effect_value * 100, 2)}% Piercing Damage"
        if self.effect_type == EffectType.SplashDmg:
            display_string += f"{int(self.effect_value)} Splash Damage"
        if self.effect_type == EffectType.SplashPercentMaxDmg:
            display_string += f"{round(self.effect_value * 100, 2)}% Max Damage as Splash Damage"
        
        if self.effect_type == EffectType.CritDmgBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Crit Effect"
        if self.effect_type == EffectType.CritDmgReduction:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Crit Damage Reduction"

        if self.effect_type == EffectType.HealthSteal:
            display_string += f"{round(self.effect_value * 100, 2)}% Health Steal"
        if self.effect_type == EffectType.ManaSteal:
            display_string += f"{round(self.effect_value * 100, 2)}% Mana Steal"
        
        if self.effect_type == EffectType.AdjustedCDs:
            turn_str = "Turn" if self.effect_value == 1 else "Turns"
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{int(self.effect_value)} {turn_str} on Ability Cooldowns"
        
        if self.effect_type == EffectType.ChanceStatusEffect:
            se_key: StatusEffectKey | None = self.associated_status_effect
            if se_key == StatusEffectKey.Poisoned:
                display_string += f"{round(self.effect_value * 100, 2)}% Poisoned Chance"
            elif se_key == StatusEffectKey.Bleeding:
                display_string += f"{round(self.effect_value * 100, 2)}% Bleeding Chance"
            elif se_key == StatusEffectKey.TurnSkipChance:
                display_string += f"{round(self.effect_value * 100, 2)}% Faltering Chance"
            elif se_key == StatusEffectKey.Taunted:
                display_string += f"{round(self.effect_value * 100, 2)}% Taunted Chance"
            elif se_key == StatusEffectKey.CannotTarget:
                display_string += f"{round(self.effect_value * 100, 2)}% Convinced Chance"
            elif se_key == StatusEffectKey.Charmed:
                display_string += f"{round(self.effect_value * 100, 2)}% Charmed Chance"
            elif se_key == StatusEffectKey.CannotAttack:
                display_string += f"{round(self.effect_value * 100, 2)}% Atrophied Chance"
            elif se_key == StatusEffectKey.Sleeping:
                display_string += f"{round(self.effect_value * 100, 2)}% Sleeping Chance"
            elif se_key == StatusEffectKey.Decaying:
                # Guaranteed to happen; the effect value is the percent decrease for healing
                # effectiveness
                display_string += f"{round(self.effect_value * 100, 2)}% Decaying"
            elif se_key == StatusEffectKey.Undying:
                display_string += f"{round(self.effect_value * 100, 2)}% Undying Chance"
            elif se_key == StatusEffectKey.CannotUseAbilities:
                display_string += f"{round(self.effect_value * 100, 2)}% Enfeebled Chance"
            elif se_key == StatusEffectKey.DmgReduction:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Protected"
            elif se_key == StatusEffectKey.DmgVulnerability:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Vulnerable"
            elif se_key == StatusEffectKey.FixedDmgTick:
                # Guaranteed to happen
                display_string += f"{int(self.effect_value)} Echoing"
            elif se_key == StatusEffectKey.Generating:
                # Guaranteed to happen
                display_string += f"{int(self.effect_value)} Coins Generated per Attack"
            elif se_key == StatusEffectKey.Tarnished:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Tarnished"
            elif se_key == StatusEffectKey.Sleeping:
                display_string += f"{round(self.effect_value * 100, 2)}% Sleeping Chance"
            elif se_key == StatusEffectKey.ManaToHP:
                display_string += f"{round(self.effect_value * 100, 2)}% Sanguinated Chance"
            elif se_key == StatusEffectKey.PoisonHeals:
                display_string += f"{round(self.effect_value * 100, 2)}% Absorbing Chance"
            elif se_key == StatusEffectKey.DmgBuff:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Empowered"
            elif se_key == StatusEffectKey.DmgDebuff:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Diminished"
            elif se_key == StatusEffectKey.StackingDamage:
                # Guaranteed to happen
                display_string += f"{round(self.effect_value * 100, 2)}% Reverberating"
            # All attribute buffs and debuffs are guaranteed to happen
            elif se_key == StatusEffectKey.ConBuff:
                display_string += f"+{int(self.effect_value)} Constitution"
            elif se_key == StatusEffectKey.ConDebuff:
                display_string += f"{int(self.effect_value)} Constitution"
            elif se_key == StatusEffectKey.StrBuff:
                display_string += f"+{int(self.effect_value)} Strength"
            elif se_key == StatusEffectKey.StrDebuff:
                display_string += f"{int(self.effect_value)} Strength"
            elif se_key == StatusEffectKey.DexBuff:
                display_string += f"+{int(self.effect_value)} Dexterity"
            elif se_key == StatusEffectKey.DexDebuff:
                display_string += f"{int(self.effect_value)} Dexterity"
            elif se_key == StatusEffectKey.IntBuff:
                display_string += f"+{int(self.effect_value)} Intelligence"
            elif se_key == StatusEffectKey.IntDebuff:
                display_string += f"{int(self.effect_value)} Intelligence"
            elif se_key == StatusEffectKey.LckBuff:
                display_string += f"+{int(self.effect_value)} Luck"
            elif se_key == StatusEffectKey.LckDebuff:
                display_string += f"{int(self.effect_value)} Luck"
            elif se_key == StatusEffectKey.MemBuff:
                display_string += f"+{int(self.effect_value)} Memory"
            elif se_key == StatusEffectKey.MemDebuff:
                display_string += f"{int(self.effect_value)} Memory"
            elif se_key == StatusEffectKey.BonusDamageOnAttack:
                if self.effect_value > 0:
                    display_string += "+"
                # Guaranteed to happen
                display_string += f"{int(self.effect_value)} future damage after attacking"
        if self.effect_type == EffectType.ResistStatusEffect:
            se_key: StatusEffectKey | None = self.associated_status_effect
            if se_key == StatusEffectKey.Poisoned:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Poisoned Chance"
            elif se_key == StatusEffectKey.Bleeding:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Bleeding Chance"
            elif se_key == StatusEffectKey.TurnSkipChance:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Faltering Chance"
            elif se_key == StatusEffectKey.Taunted:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Taunted Chance"
            elif se_key == StatusEffectKey.CannotTarget:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Convinced Chance"
            elif se_key == StatusEffectKey.Charmed:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Charmed Chance"
            elif se_key == StatusEffectKey.CannotAttack:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Atrophied Chance"
            elif se_key == StatusEffectKey.Sleeping:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Sleeping Chance"
            elif se_key == StatusEffectKey.Decaying:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Decaying Chance"
            elif se_key == StatusEffectKey.DmgVulnerability:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Vulnerable Chance"
            elif se_key == StatusEffectKey.DmgDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Diminished Chance"
            elif se_key == StatusEffectKey.CannotUseAbilities:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Enfeebled Chance"
            elif se_key == StatusEffectKey.ConDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Frail Chance"
            elif se_key == StatusEffectKey.StrDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Weakened Chance"
            elif se_key == StatusEffectKey.DexDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Slowed Chance"
            elif se_key == StatusEffectKey.IntDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Drained Chance"
            elif se_key == StatusEffectKey.LckDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Unlucky Chance"
            elif se_key == StatusEffectKey.MemDebuff:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Forgetful Chance"
            elif se_key == StatusEffectKey.FixedDmgTick:
                display_string += f"{round(self.effect_value * 100, 2)}% Resist Echoing Chance"

        if self.effect_type == EffectType.RestoreHealth:
            display_string += f"Restore {int(self.effect_value)} Health"
        if self.effect_type == EffectType.RestorePercentHealth:
            display_string += f"Restore {round(self.effect_value * 100, 2)}% Health"
        if self.effect_type == EffectType.RestoreMana:
            display_string += f"Restore {int(self.effect_value)} Mana"
        if self.effect_type == EffectType.RestorePercentMana:
            display_string += f"Restore {round(self.effect_value * 100, 2)}% Mana"

        if self.effect_type == EffectType.AdjustedManaCosts:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Ability Mana Costs"
        if self.effect_type == EffectType.HealingAbilityBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Healing Ability Effect"
        if self.effect_type == EffectType.AdditionalXP:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% XP Gained"
        if self.effect_type == EffectType.PotionMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Potion Effect"

        if self.effect_type == EffectType.Damage:
            display_string += f"Deals {int(self.effect_value)} Damage"
        elif self.effect_type == EffectType.Summon:
            summon_str: str = " ".join(self.camel_case_split(str(self.summon)))
            display_string += f"Summons {int(self.effect_value)} {summon_str} at the start of the duel"
        elif self.effect_type == EffectType.GrantAbility:
            display_string += f"Grants Ability: {self.granted_ability}"

        # For now, specifically skip ResurrectOnce, since it's in the item description.

        if self.effect_time > 0:
            turn_str = "turn" if self.effect_time == 1 else "turns"
            display_string += f" for {self.effect_time} {turn_str}"

        # TODO: This does assume all conditions are conjunctive. I should devise a
        # neat way to do disjunctive conditions in the future.
        conditions_strs = []
        for i, condition in enumerate(self.conditions):
            if condition != filter_condition:
                if condition == ConditionType.IsAbovePercentHealth:
                    conditions_strs.append(f"above {round(self.condition_values[i] * 100, 2)}% health")
                if condition == ConditionType.IsBelowPercentHealth:
                    conditions_strs.append(f"below {round(self.condition_values[i] * 100, 2)}% health")
                if condition == ConditionType.IsFullHealth:
                    conditions_strs.append("at full health")
                if condition == ConditionType.IsItemArmor:
                    conditions_strs.append("socketed in armor")
                if condition == ConditionType.IsItemInHand:
                    conditions_strs.append("socketed in a main-hand or off-hand item")
                
            if len(conditions_strs) > 1 and i == len(self.conditions) - 1:
                conditions_strs[-1] = "and " + conditions_strs[-1]

        if len(conditions_strs) > 0:
            display_string += " when " + ", ".join(conditions_strs)

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.effect_type = state.get("effect_type", EffectType.Unknown)
        self.effect_value = state.get("effect_value", 0)
        self.effect_time = state.get("effect_time", 0)
        self.conditions = state.get("conditions", [])
        self.condition_values = state.get("condition_values", [])
        self.associated_status_effect = state.get("associated_status_effect", None)
        self.summon = state.get("summon", None)
        self.granted_ability = state.get("granted_ability", None)

# -----------------------------------------------------------------------------
# ITEM EFFECTS CLASS
# -----------------------------------------------------------------------------

class ItemEffects():
    def __init__(self, permanent: List[Effect], on_turn_start: List[Effect], on_turn_end: List[Effect], on_damaged: List[Effect], on_successful_ability_used: List[Effect], on_successful_attack: List[Effect], on_attacked: List[Effect], on_ability_used_against: List[Effect]):
        # Permanent is a special case since it doesn't ever trigger like the others and therefore encapsulates
        # the concept of inherent item mods which are going to be referenced in a bunch of places.
        self.permanent: List[Effect] = permanent
        
        self.on_turn_start: List[Effect] = on_turn_start
        self.on_turn_end: List[Effect] = on_turn_end
        self.on_damaged: List[Effect] = on_damaged # After taking damage from any source (post reduction and armor)
        self.on_successful_ability_used: List[Effect] = on_successful_ability_used
        self.on_successful_attack: List[Effect] = on_successful_attack
        self.on_attacked: List[Effect] = on_attacked # On being attacked (not dodged)
        self.on_ability_used_against: List[Effect] = on_ability_used_against

    def get_permanent_attribute_mods(self) -> Attributes:
        attr_mods = Attributes(0, 0, 0, 0, 0, 0)
        for effect in self.permanent:
            if effect.effect_type == EffectType.ConMod:
                attr_mods.constitution += int(effect.effect_value)
            if effect.effect_type == EffectType.StrMod:
                attr_mods.strength += int(effect.effect_value)
            if effect.effect_type == EffectType.DexMod:
                attr_mods.dexterity += int(effect.effect_value)
            if effect.effect_type == EffectType.IntMod:
                attr_mods.intelligence += int(effect.effect_value)
            if effect.effect_type == EffectType.LckMod:
                attr_mods.luck += int(effect.effect_value)
            if effect.effect_type == EffectType.MemMod:
                attr_mods.memory += int(effect.effect_value)
        return attr_mods

    def has_item_effect(self, effect_type: EffectType):
        all_effects: List[List[Effect]] = [
            self.permanent,
            self.on_turn_start,
            self.on_turn_end,
            self.on_damaged,
            self.on_successful_ability_used,
            self.on_successful_attack,
            self.on_attacked,
            self.on_ability_used_against
        ]
        return any(any(effect.effect_type == effect_type for effect in effect_group) for effect_group in all_effects)        

    def add_effect_in_category(self, effect: Effect, category: ItemEffectCategory):
        if category == ItemEffectCategory.Permanent:
            self.permanent.append(effect)
        elif category == ItemEffectCategory.OnTurnStart:
            self.on_turn_start.append(effect)
        elif category == ItemEffectCategory.OnTurnEnd:
            self.on_turn_end.append(effect)
        elif category == ItemEffectCategory.OnDamaged:
            self.on_damaged.append(effect)
        elif category == ItemEffectCategory.OnSuccessfulAbilityUsed:
            self.on_successful_ability_used.append(effect)
        elif category == ItemEffectCategory.OnSuccessfulAttack:
            self.on_successful_attack.append(effect)
        elif category == ItemEffectCategory.OnAttacked:
            self.on_attacked.append(effect)
        elif category == ItemEffectCategory.OnAbilityUsedAgainst:
            self.on_ability_used_against.append(effect)

    def get_effects_by_category(self, category: ItemEffectCategory):
        if category == ItemEffectCategory.Permanent:
            return self.permanent
        elif category == ItemEffectCategory.OnTurnStart:
            return self.on_turn_start
        elif category == ItemEffectCategory.OnTurnEnd:
            return self.on_turn_end
        elif category == ItemEffectCategory.OnDamaged:
            return self.on_damaged
        elif category == ItemEffectCategory.OnSuccessfulAbilityUsed:
            return self.on_successful_ability_used
        elif category == ItemEffectCategory.OnSuccessfulAttack:
            return self.on_successful_attack
        elif category == ItemEffectCategory.OnAttacked:
            return self.on_attacked
        elif category == ItemEffectCategory.OnAbilityUsedAgainst:
            return self.on_ability_used_against

    def sort_by_priority(self, effects: List[Effect]):
        return sorted(effects, key=lambda effect: EFFECT_PRIORITY[effect.effect_type])

    def get_socket_str(self, condition_type: ConditionType):
        def filter_by_condition(effect_lst: List[Effect], ct: ConditionType):
            return [effect for effect in effect_lst if (ct in effect.conditions or len(effect.conditions) == 0)]

        display_string = ""

        permanent_effects_strs = [effect.__str__(condition_type) for effect in filter_by_condition(self.permanent, condition_type)]
        display_string += "\n".join(permanent_effects_strs) + ("\n" if len(permanent_effects_strs) > 0 else "")

        on_turn_start_strs = [effect.__str__(condition_type) + " at the start of your turn" for effect in filter_by_condition(self.on_turn_start, condition_type)]
        display_string += "\n".join(on_turn_start_strs) + ("\n" if len(on_turn_start_strs) > 0 else "")

        on_turn_end_strs = [effect.__str__(condition_type) + " at the end of your turn" for effect in filter_by_condition(self.on_turn_end, condition_type)]
        display_string += "\n".join(on_turn_end_strs) + ("\n" if len(on_turn_end_strs) > 0 else "")

        on_damaged_strs = [effect.__str__(condition_type) + " when you're damaged" for effect in filter_by_condition(self.on_damaged, condition_type)]
        display_string += "\n".join(on_damaged_strs) + ("\n" if len(on_damaged_strs) > 0 else "")

        on_successful_ability_strs = [effect.__str__(condition_type) + " when you successfully use an ability" for effect in filter_by_condition(self.on_successful_ability_used, condition_type)]
        display_string += "\n".join(on_successful_ability_strs) + ("\n" if len(on_successful_ability_strs) > 0 else "")

        on_successful_attack_strs = [effect.__str__(condition_type) + " when you successfully attack" for effect in filter_by_condition(self.on_successful_attack, condition_type)]
        display_string += "\n".join(on_successful_attack_strs) + ("\n" if len(on_successful_attack_strs) > 0 else "")

        on_attacked_strs = [effect.__str__(condition_type) + " when you're attacked" for effect in filter_by_condition(self.on_attacked, condition_type)]
        display_string += "\n".join(on_attacked_strs) + ("\n" if len(on_attacked_strs) > 0 else "")

        on_ability_used_against_strs = [effect.__str__(condition_type) + " when an ability is used on you" for effect in filter_by_condition(self.on_ability_used_against, condition_type)]
        display_string += "\n".join(on_ability_used_against_strs) + ("\n" if len(on_ability_used_against_strs) > 0 else "")

        return display_string

    def __add__(self, other: ItemEffects):
        return ItemEffects(
            self.sort_by_priority(self.permanent + other.permanent),
            self.sort_by_priority(self.on_turn_start + other.on_turn_start),
            self.sort_by_priority(self.on_turn_end + other.on_turn_end),
            self.sort_by_priority(self.on_damaged + other.on_damaged),
            self.sort_by_priority(self.on_successful_ability_used + other.on_successful_ability_used),
            self.sort_by_priority(self.on_successful_attack + other.on_successful_attack),
            self.sort_by_priority(self.on_attacked + other.on_attacked),
            self.sort_by_priority(self.on_ability_used_against + other.on_ability_used_against)
        )

    def __str__(self):
        display_string = ""

        permanent_effect_str = "\n".join([str(effect) for effect in self.permanent])
        if permanent_effect_str != "":
            display_string += permanent_effect_str + "\n\n"

        on_turn_start_str = "\n".join([str(effect) for effect in self.on_turn_start])
        if on_turn_start_str != "":
            display_string += "At the start of your turn:\n\n" + f"*{on_turn_start_str}*\n\n"
        
        on_turn_end_str = "\n".join([str(effect) for effect in self.on_turn_end])
        if on_turn_end_str != "":
            display_string += "At the end of your turn:\n\n" + f"*{on_turn_end_str}*\n\n"
        
        on_damaged_str = "\n".join([str(effect) for effect in self.on_damaged])
        if on_damaged_str != "":
            display_string += "When you're damaged:\n\n" + f"*{on_damaged_str}*\n\n"

        on_successful_ability_used_str = "\n".join([str(effect) for effect in self.on_successful_ability_used])
        if on_successful_ability_used_str != "":
            display_string += "When you successfully use an ability:\n\n" + f"*{on_successful_ability_used_str}*\n\n"
        
        on_successful_attack_str = "\n".join([str(effect) for effect in self.on_successful_attack])
        if on_successful_attack_str != "":
            display_string += "When you successfully attack:\n\n" + f"*{on_successful_attack_str}*\n\n"
        
        on_attacked_str = "\n".join([str(effect) for effect in self.on_attacked])
        if on_attacked_str != "":
            display_string += "When you're attacked:\n\n" + f"*{on_attacked_str}*\n\n"

        on_ability_used_against_str = "\n".join([str(effect) for effect in self.on_ability_used_against])
        if on_ability_used_against_str != "":
            display_string += "When an ability is used on you:\n\n" + f"*{on_ability_used_against_str}*\n\n"

        # Remove the last two newlines
        return display_string[:-2]

    def __len__(self):
        return len(
            self.permanent +
            self.on_turn_start +
            self.on_turn_end +
            self.on_damaged +
            self.on_successful_ability_used +
            self.on_successful_attack +
            self.on_attacked +
            self.on_ability_used_against
        )

    def load_effect_from_state(self, data):
        if isinstance(data, Effect):
            return data
        return Effect.load_from_state(data)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.permanent = [self.load_effect_from_state(data) for data in state.get("permanent", [])]
        self.on_turn_start = [self.load_effect_from_state(data) for data in state.get("on_turn_start", [])]
        self.on_turn_end = [self.load_effect_from_state(data) for data in state.get("on_turn_end", [])]
        self.on_damaged = [self.load_effect_from_state(data) for data in state.get("on_damaged", [])]
        self.on_successful_ability_used = [self.load_effect_from_state(data) for data in state.get("on_successful_ability_used", [])]
        self.on_successful_attack = [self.load_effect_from_state(data) for data in state.get("on_successful_attack", [])]
        self.on_attacked = [self.load_effect_from_state(data) for data in state.get("on_attacked", [])]
        self.on_ability_used_against = [self.load_effect_from_state(data) for data in state.get("on_ability_used_against", [])]