from __future__ import annotations

from types import MappingProxyType
from strenum import StrEnum

from typing import List

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

# TODO: I actually need to implement all of these for each of the associated
# cases in ItemEffects.
class EffectType(StrEnum):
    Unknown = "Unknown"

    ConMod = "ConMod"
    StrMod = "StrMod"
    DexMod = "DexMod"
    IntMod = "IntMod"
    LckMod = "LckMod"
    MemMod = "MemMod"

    # Everything in this group is associated with percent effect values
    DmgReflect = "DmgReflect"
    DmgResist = "DmgResist"
    DmgBuff = "DmgBuff"
    DmgBuffSelfMaxHealth = "DmgBuffSelfMaxHealth"
    DmgBuffSelfRemainingHealth = "DmgBuffSelfRemainingHealth"
    DmgBuffOtherMaxHealth = "DmgBuffOtherMaxHealth"
    DmgBuffOtherRemainingHealth = "DmgBuffOtherRemainingHealth"
    DmgBuffLegends = "DmgBuffLegends"
    DmgBuffPoisoned = "DmgBuffPoisoned"
    DmgBuffBleeding = "DmgBuffBleeding"
    DmgBuffFromDex = "DmgBuffFromDex"

    # Everything in this group is associated with percent effect values
    ExtraArmor = "ExtraArmor"
    RestoreArmor = "RestoreArmor"

    # Everything in this group is associated with percent effect values
    PiercingDmg = "PiercingDmg"
    SplashDmg = "SplashDmg"
    CritDmgBuff = "CritDmgBuff"
    CritDmgResist = "CritDmgResist"

    # Everything in this group is associated with percent effect values
    HealthSteal = "HealthSteal"
    ManaSteal = "ManaSteal"

    LoweredCDs = "LoweredCDs"

    # Everything in this group is associated with percent effect values
    ChancePoisoned = "ChancePoisoned"
    ResistPoisoned = "ResistPoisoned"
    ChanceBleeding = "ChanceBleeding"
    ResistBleeding = "ResistBleeding"
    ChanceFaltering = "ChanceFaltering"
    ResistFaltering = "ResistFaltering"

    RestoreHealth = "RestoreHealth"
    RestorePercentHealth = "RestorePercentHealth"
    RestoreMana = "RestoreMana"
    RestorePercentMana = "RestorePercentMana"

    # Everything in this group is associated with percent effect values
    ReducedManaCosts = "ReducedManaCosts"
    HealingAbilityBuff = "HealingAbilityBuff"
    AdditionalXP = "AdditionalXP"

    ResurrectOnce = "ResurrectOnce"


class ConditionType(StrEnum):
    Unknown = "Unknown"

    # These conditions are what I'll use to split between doing certain item effects
    # on some types of items versus others, allowing gems to be more versatile.
    IsItemInHand = "IsItemInHand"
    IsItemArmor = "IsItemArmor"

    IsBelowPercentHealth = "IsBelowPercentHealth"
    IsAbovePercentHealth = "IsAbovePercentHealth"
    IsFullHealth = "IsFullHealth"

# -----------------------------------------------------------------------------
# PRIORITY DICT
# -----------------------------------------------------------------------------

# TODO: Finish this and figure out the ordering
EFFECT_PRIORITY: MappingProxyType[EffectType, int] = MappingProxyType({
    EffectType.ConMod: 0,
    EffectType.StrMod: 1,
    EffectType.DexMod: 2,
})

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class Effect():
    def __init__(self, effect_type: EffectType, effect_value: int | float, effect_time: int, conditions: List[ConditionType], condition_values: List[int | float]):
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.effect_time = effect_time
        self.conditions = conditions
        self.condition_values = condition_values

    def __str__(self):
        display_string = ""

        if self.effect_type == EffectType.ConMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Constitution"
        if self.effect_type == EffectType.StrMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Strength"
        if self.effect_type == EffectType.DexMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Dexterity"
        if self.effect_type == EffectType.IntMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Intelligence"
        if self.effect_type == EffectType.LckMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Luck"
        if self.effect_type == EffectType.MemMod:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Memory"

        if self.effect_type == EffectType.DmgReflect:
            display_string += f"{self.effect_value * 100}% Damage Reflected"
        if self.effect_type == EffectType.DmgResist:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Resist"
        if self.effect_type == EffectType.DmgBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Dealt"
        if self.effect_type == EffectType.DmgBuffSelfMaxHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Max Health as Damage"
        if self.effect_type == EffectType.DmgBuffSelfRemainingHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Remaining Health as Damage"
        if self.effect_type == EffectType.DmgBuffOtherMaxHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Enemy Max Health as Damage"
        if self.effect_type == EffectType.DmgBuffOtherRemainingHealth:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Enemy Remaining Health as Damage"
        if self.effect_type == EffectType.DmgBuffLegends:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Against Legendaries"
        if self.effect_type == EffectType.DmgBuffPoisoned:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Against Poisoned Enemies"
        if self.effect_type == EffectType.DmgBuffBleeding:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Against Bleeding Enemies"
        if self.effect_type == EffectType.DmgBuffFromDex:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Damage Scaling from Dex"
        
        if self.effect_type == EffectType.ExtraArmor:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value} Extra Armor"
        if self.effect_type == EffectType.RestoreArmor:
            display_string += f"{self.effect_value} Armor Restored"

        if self.effect_type == EffectType.PiercingDmg:
            display_string += f"{self.effect_value * 100}% Damage Ignores Armor"
        if self.effect_type == EffectType.SplashDmg:
            display_string += f"{self.effect_value * 100}% Damage Splash"
        if self.effect_type == EffectType.CritDmgBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Crit Damage"
        if self.effect_type == EffectType.CritDmgResist:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Crit Damage Resist"

        if self.effect_type == EffectType.HealthSteal:
            display_string += f"{self.effect_value * 100}% Health Stolen"
        if self.effect_type == EffectType.ManaSteal:
            display_string += f"{self.effect_value * 100}% Mana Stolen"
        
        if self.effect_type == EffectType.LoweredCDs:
            turn_str = "Turn" if self.effect_value == 1 else "Turns"
            display_string += f"{self.effect_value} {turn_str} on Ability Cooldowns"
        
        if self.effect_type == EffectType.ChancePoisoned:
            display_string += f"{self.effect_value * 100}% Poisoned Chance"
        if self.effect_type == EffectType.ResistPoisoned:
            display_string += f"{self.effect_value * 100}% Resist Poisoned Chance"
        if self.effect_type == EffectType.ChanceBleeding:
            display_string += f"{self.effect_value * 100}% Bleeding Chance"
        if self.effect_type == EffectType.ResistBleeding:
            display_string += f"{self.effect_value * 100}% Resist Bleeding Chance"
        if self.effect_type == EffectType.ChanceFaltering:
            display_string += f"{self.effect_value * 100}% Faltering Chance"
        if self.effect_type == EffectType.ResistFaltering:
            display_string += f"{self.effect_value * 100}% Resist Faltering Chance"

        if self.effect_type == EffectType.RestoreHealth:
            display_string += f"Restore {self.effect_value} Health"
        if self.effect_type == EffectType.RestorePercentHealth:
            display_string += f"Restore {self.effect_value * 100}% Health"
        if self.effect_type == EffectType.RestoreMana:
            display_string += f"Restore {self.effect_value} Mana"
        if self.effect_type == EffectType.RestorePercentMana:
            display_string += f"Restore {self.effect_value * 100}% Mana"

        if self.effect_type == EffectType.ReducedManaCosts:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Ability Mana Costs"
        if self.effect_type == EffectType.HealingAbilityBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Healing Ability Effect"
        if self.effect_type == EffectType.AdditionalXP:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% XP Gained"

        # For now, specifically skip ResurrectOnce, since it's in the item description.

        if self.effect_time > 0:
            display_string += f" for {self.effect_time} turns"

        if len(self.conditions) > 0:
            display_string += " when "
        
        # TODO: This does assume all conditions are conjunctive. I should devise a
        # neat way to do disjunctive conditions in the future.
        conditions_strs = []
        for i, condition in enumerate(self.conditions):
            if condition == ConditionType.IsAbovePercentHealth:
                conditions_strs.append(f"above {self.condition_values[i]}% health")
            if condition == ConditionType.IsBelowPercentHealth:
                conditions_strs.append(f"below {self.condition_values[i]}% health")
            if condition == ConditionType.IsFullHealth:
                conditions_strs.append(f"at full health")
            
            if i == len(self.conditions) - 1:
                conditions_strs[-1] = "and " + conditions_strs[-1]
        display_string += ", ".join(conditions_strs)

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.effect_type = state.get("effect_type", EffectType.Unknown)
        self.effect_value = state.get("effect_value", 0)
        self.effect_time = state.get("effect_time", 0)
        self.conditions = state.get("conditions", [])
        self.condition_values = state.get("condition_values", [])
