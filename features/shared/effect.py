from __future__ import annotations

from features.shared.attributes import Attributes
from features.shared.enums import ClassTag
from types import MappingProxyType
from strenum import StrEnum

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
    DmgBuff = "DmgBuff"
    DmgBuffSelfMaxHealth = "DmgBuffSelfMaxHealth"
    DmgBuffSelfRemainingHealth = "DmgBuffSelfRemainingHealth"
    DmgBuffOtherMaxHealth = "DmgBuffOtherMaxHealth"
    DmgBuffOtherRemainingHealth = "DmgBuffOtherRemainingHealth"
    DmgBuffLegends = "DmgBuffLegends"
    DmgBuffPoisoned = "DmgBuffPoisoned"
    DmgBuffBleeding = "DmgBuffBleeding"
    DmgBuffFromDex = "DmgBuffFromDex"
    DmgBuffFromInt = "DmgBuffFromInt"

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
    AdditionalXP = "AdditionalXP"
    PotionMod = "PotionMod"
    
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
    EffectType.DmgBuff: 9,
    EffectType.DmgBuffSelfMaxHealth: 10,
    EffectType.DmgBuffSelfRemainingHealth: 11,
    EffectType.DmgBuffOtherMaxHealth: 12,
    EffectType.DmgBuffOtherRemainingHealth: 13,
    EffectType.DmgBuffLegends: 14,
    EffectType.DmgBuffPoisoned: 15,
    EffectType.DmgBuffBleeding: 16,
    EffectType.DmgBuffFromDex: 17,
    EffectType.DmgBuffFromInt: 18,

    EffectType.RestoreArmor: 19,
    EffectType.RestorePercentArmor: 20,
    
    EffectType.PiercingDmg: 21,
    EffectType.PiercingPercentDmg: 22,
    EffectType.SplashDmg: 23,
    EffectType.SplashPercentMaxDmg: 24,

    EffectType.CritDmgBuff: 25,
    EffectType.CritDmgReduction: 26,

    EffectType.HealthSteal: 27,
    EffectType.ManaSteal: 28,

    EffectType.AdjustedCDs: 29,

    EffectType.ChancePoisoned: 30,
    EffectType.ResistPoisoned: 31,
    EffectType.ChanceBleeding: 32,
    EffectType.ResistBleeding: 33,
    EffectType.ChanceFaltering: 34,
    EffectType.ResistFaltering: 35,
    EffectType.ChanceTaunted: 36,
    EffectType.ResistTaunted: 37,
    EffectType.ChanceConvinced: 38,
    EffectType.ResistConvinced: 39,

    EffectType.RestoreHealth: 40,
    EffectType.RestorePercentHealth: 41,
    EffectType.RestoreMana: 42,
    EffectType.RestorePercentMana: 43,

    EffectType.AdjustedManaCosts: 44,
    EffectType.HealingAbilityBuff: 45,
    EffectType.AdditionalXP: 46,
    EffectType.PotionMod: 47,

    EffectType.ResurrectOnce: 48
})

# -----------------------------------------------------------------------------
# EFFECT CLASS
# -----------------------------------------------------------------------------

class Effect():
    def __init__(self, effect_type: EffectType, effect_value: int | float, effect_time: int, conditions: List[ConditionType], condition_values: List[int | float]):
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.effect_time = effect_time
        self.conditions = conditions
        self.condition_values = condition_values

    @staticmethod
    def load_from_state(effect_data: dict):
        return Effect(
            effect_data.get("effect_type", ""),
            effect_data.get("effect_value", 0),
            effect_data.get("effect_time", 0),
            effect_data.get("conditions", []),
            effect_data.get("condition_values", [])
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
        if self.effect_type == EffectType.DmgBuffFromDex:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Dex"
        if self.effect_type == EffectType.DmgBuffFromInt:
            if self.effect_value > 0:
                display_string += "+"
            display_string += f"{round(self.effect_value * 100, 2)}% Damage Scaling from Int"
        
        if self.effect_type == EffectType.RestoreArmor:
            display_string += f"{int(self.effect_value)} Armor Restored"
        if self.effect_type == EffectType.RestorePercentArmor:
            display_string += f"{round(self.effect_value * 100, 2)}% Armor Restored"

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
        
        if self.effect_type == EffectType.ChancePoisoned:
            display_string += f"{round(self.effect_value * 100, 2)}% Poisoned Chance"
        if self.effect_type == EffectType.ResistPoisoned:
            display_string += f"{round(self.effect_value * 100, 2)}% Resist Poisoned Chance"
        if self.effect_type == EffectType.ChanceBleeding:
            display_string += f"{round(self.effect_value * 100, 2)}% Bleeding Chance"
        if self.effect_type == EffectType.ResistBleeding:
            display_string += f"{round(self.effect_value * 100, 2)}% Resist Bleeding Chance"
        if self.effect_type == EffectType.ChanceFaltering:
            display_string += f"{round(self.effect_value * 100, 2)}% Faltering Chance"
        if self.effect_type == EffectType.ResistFaltering:
            display_string += f"{round(self.effect_value * 100, 2)}% Resist Faltering Chance"
        if self.effect_type == EffectType.ChanceTaunted:
            display_string += f"{round(self.effect_value * 100, 2)}% Taunted Chance"
        if self.effect_type == EffectType.ResistTaunted:
            display_string += f"{round(self.effect_value * 100, 2)}% Resist Taunted Chance"
        if self.effect_type == EffectType.ChanceConvinced:
            display_string += f"{round(self.effect_value * 100, 2)}% Convinced Chance"
        if self.effect_type == EffectType.ResistConvinced:
            display_string += f"{round(self.effect_value * 100, 2)}% Resist Convinced Chance"

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

        # For now, specifically skip ResurrectOnce, since it's in the item description.

        if self.effect_time > 0:
            display_string += f" for {self.effect_time} turns"

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

# -----------------------------------------------------------------------------
# ITEM EFFECTS CLASS
# -----------------------------------------------------------------------------

class ItemEffects():
    def __init__(self, permanent: List[Effect]=[], on_turn_start: List[Effect]=[], on_turn_end: List[Effect]=[], on_damaged: List[Effect]=[], on_successful_ability_used: List[Effect]=[], on_successful_attack: List[Effect]=[], on_attacked: List[Effect]=[], on_ability_used_against: List[Effect]=[]):
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