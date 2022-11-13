from __future__ import annotations

from features.shared.item import ClassTag
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
    ExtraArmor = "ExtraArmor" # TODO: Implement once armor changes are done
    RestoreArmor = "RestoreArmor" # TODO: Implement once armor changes are done

    PiercingDmg = "PiercingDmg"
    SplashDmg = "SplashDmg"

    # Everything in this group is associated with percent effect values
    CritDmgBuff = "CritDmgBuff"
    CritDmgReduction = "CritDmgReduction"

    HealthSteal = "HealthSteal"
    ManaSteal = "ManaSteal"

    AdjustedCDs = "AdjustedCDs"

    # Everything in this group is associated with percent effect values
    ChancePoisoned = "ChancePoisoned"
    ResistPoisoned = "ResistPoisoned"
    ChanceBleeding = "ChanceBleeding"
    ResistBleeding = "ResistBleeding"
    ChanceFaltering = "ChanceFaltering"
    ResistFaltering = "ResistFaltering"
    ChanceTaunted = "ChanceTaunted"
    ResistTaunted = "ResistTaunted"
    ChanceConvinced = "ChanceConvinced"
    ResistConvinced = "ResistConvinced"

    RestoreHealth = "RestoreHealth"
    RestorePercentHealth = "RestorePercentHealth"
    RestoreMana = "RestoreMana"
    RestorePercentMana = "RestorePercentMana"

    # Everything in this group is associated with percent effect values
    AdjustedManaCosts = "AdjustedManaCosts"
    HealingAbilityBuff = "HealingAbilityBuff"
    AdditionalXP = "AdditionalXP" # TODO: Implement this

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
    EffectType.IntMod: 3,
    EffectType.LckMod: 4,
    EffectType.MemMod: 5,

    EffectType.DmgReflect: 6,
    EffectType.DmgResist: 7,
    EffectType.DmgBuff: 8,
    EffectType.DmgBuffSelfMaxHealth: 9,
    EffectType.DmgBuffSelfRemainingHealth: 10,
    EffectType.DmgBuffOtherMaxHealth: 11,
    EffectType.DmgBuffOtherRemainingHealth: 12,
    EffectType.DmgBuffLegends: 13,
    EffectType.DmgBuffPoisoned: 14,
    EffectType.DmgBuffBleeding: 15,
    EffectType.DmgBuffFromDex: 16,

    EffectType.ExtraArmor: 17,
    EffectType.RestoreArmor: 18,
    
    EffectType.PiercingDmg: 19,
    EffectType.SplashDmg: 20,
    EffectType.CritDmgBuff: 21,
    EffectType.CritDmgReduction: 22,

    EffectType.HealthSteal: 23,
    EffectType.ManaSteal: 24,

    EffectType.AdjustedCDs: 25,

    EffectType.ChancePoisoned: 26,
    EffectType.ResistPoisoned: 27,
    EffectType.ChanceBleeding: 28,
    EffectType.ResistBleeding: 29,
    EffectType.ChanceFaltering: 30,
    EffectType.ResistFaltering: 31,
    EffectType.ChanceTaunted: 32,
    EffectType.ResistTaunted: 33,
    EffectType.ChanceConvinced: 34,
    EffectType.ResistConvinced: 35,

    EffectType.RestoreHealth: 36,
    EffectType.RestorePercentHealth: 37,
    EffectType.RestoreMana: 38,
    EffectType.RestorePercentMana: 39,

    EffectType.AdjustedManaCosts: 40,
    EffectType.HealingAbilityBuff: 41,
    EffectType.AdditionalXP: 42,

    EffectType.ResurrectOnce: 43
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
            display_string += f"{self.effect_value} Piercing Damage"
        if self.effect_type == EffectType.SplashDmg:
            display_string += f"{self.effect_value} Damage Splash"
        if self.effect_type == EffectType.CritDmgBuff:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Crit Damage"
        if self.effect_type == EffectType.CritDmgReduction:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{self.effect_value * 100}% Crit Damage Reduction"

        if self.effect_type == EffectType.HealthSteal:
            display_string += f"{self.effect_value} Health Stolen"
        if self.effect_type == EffectType.ManaSteal:
            display_string += f"{self.effect_value} Mana Stolen"
        
        if self.effect_type == EffectType.AdjustedCDs:
            turn_str = "Turn" if self.effect_value == 1 else "Turns"
            if self.effect_value > 0:
                display_string += "+"
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
        if self.effect_type == EffectType.ChanceTaunted:
            display_string += f"{self.effect_value * 100}% Taunted Chance"
        if self.effect_type == EffectType.ResistTaunted:
            display_string += f"{self.effect_value * 100}% Resist Taunted Chance"
        if self.effect_type == EffectType.ChanceConvinced:
            display_string += f"{self.effect_value * 100}% Convinced Chance"
        if self.effect_type == EffectType.ResistConvinced:
            display_string += f"{self.effect_value * 100}% Resist Convinced Chance"

        if self.effect_type == EffectType.RestoreHealth:
            display_string += f"Restore {self.effect_value} Health"
        if self.effect_type == EffectType.RestorePercentHealth:
            display_string += f"Restore {self.effect_value * 100}% Health"
        if self.effect_type == EffectType.RestoreMana:
            display_string += f"Restore {self.effect_value} Mana"
        if self.effect_type == EffectType.RestorePercentMana:
            display_string += f"Restore {self.effect_value * 100}% Mana"

        if self.effect_type == EffectType.AdjustedManaCosts:
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
