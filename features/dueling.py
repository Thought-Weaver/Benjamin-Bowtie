from __future__ import annotations

from math import ceil
from random import choice, random

import discord

from dataclasses import dataclass
from discord.embeds import Embed
from discord.ext import commands
from strenum import StrEnum
from features.expertise import ExpertiseClass
from features.shared.attributes import Attributes
from features.shared.constants import DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, STR_DMG_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.item import WeaponStats
from features.shared.statuseffect import *

from typing import List, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from features.shared.effect import Effect
    from features.expertise import Expertise
    from features.shared.ability import Ability
    from features.shared.effect import ItemEffects
    from features.shared.item import Item
    from features.shared.statuseffect import StatusEffect

# -----------------------------------------------------------------------------
# DUELING CLASS
# -----------------------------------------------------------------------------

class Dueling():
    def __init__(self):
        # All abilities unlocked and purchased
        self.available_abilities: List[Ability] = []
        # Abilities that the player has equipped and can be used
        self.abilities: List[Ability] = []

        # Temporary variables maintained for duels
        # They're stored here to make it easier to check if a Player/NPC
        # is currently in a duel
        self.is_in_combat: bool = False
        self.status_effects: List[StatusEffect] = []
        # Some enemies might start with more than 1 by default
        self.init_actions_remaining: int = 1
        # Storing here because abilities will affect them and access is
        # easier this way
        self.actions_remaining: int = 1

    # TODO: Implement an abstract method for automatically taking a turn
    # which NPCs will implement.

    @staticmethod
    def format_armor_dmg_reduct_str(damage: int, actual_damage_dealt: int):
        # Could deal more damage due to weaknesses or less due to armor and resistances
        # This is here since it's only really used during Dueling
        if damage == actual_damage_dealt:
            return ""
        
        damage_reduction_str = "+" if actual_damage_dealt > damage else ""
        damage_reduction_str = f" ({damage_reduction_str}{-(damage - actual_damage_dealt)})" if damage != actual_damage_dealt else ""
        return damage_reduction_str

    def get_total_percent_dmg_reduct(self):
        total_percent_reduction = 0
        for status_effect in self.status_effects:
            if status_effect.key == StatusEffectKey.DmgReduction:
                total_percent_reduction = min(0.75, total_percent_reduction + status_effect.value)
            if status_effect.key == StatusEffectKey.DmgVulnerability:
                total_percent_reduction = max(-0.25, total_percent_reduction + status_effect.value)
        return total_percent_reduction

    def reset_ability_cds(self):
        for ability in self.abilities:
            ability.reset_cd()

    def decrement_all_ability_cds(self):
        for ability in self.abilities:
            ability.decrement_cd()

    def decrement_statuses_time_remaining(self):
        remaining_effects = []
        for status_effect in self.status_effects:
            status_effect.decrement_turns_remaining()
            if status_effect.turns_remaining > 0 or status_effect.turns_remaining == -1:
                remaining_effects.append(status_effect)
        self.status_effects = remaining_effects

    def ability_exists(self, ability: Ability):
        for i, dueling_ability in enumerate(self.abilities):
            if dueling_ability == ability:
                return i
        return -1

    def get_combined_attribute_mods(self) -> Attributes:
        result = Attributes(0, 0, 0, 0, 0, 0)
        for status_effect in self.status_effects:
            if status_effect.key == StatusEffectKey.ConBuff or status_effect.key == StatusEffectKey.ConDebuff:
                result.constitution += int(status_effect.value)
            if status_effect.key == StatusEffectKey.StrBuff or status_effect.key == StatusEffectKey.StrDebuff:
                result.strength += int(status_effect.value)
            if status_effect.key == StatusEffectKey.DexBuff or status_effect.key == StatusEffectKey.DexDebuff:
                result.dexterity += int(status_effect.value)
            if status_effect.key == StatusEffectKey.IntBuff or status_effect.key == StatusEffectKey.IntDebuff:
                result.intelligence += int(status_effect.value)
            if status_effect.key == StatusEffectKey.LckBuff or status_effect.key == StatusEffectKey.LckDebuff:
                result.luck += int(status_effect.value)
        return result

    def get_statuses_string(self) -> str:
        return "*Status Effects:*\n\n" + "\n".join([str(se) for se in self.status_effects])

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.available_abilities = state.get("available_abilities", [])
        self.abilities = state.get("abilities", [])

        self.is_in_combat = False
        self.status_effects = []
        self.init_actions_remaining = 1
        self.actions_remaining = 1

    def map_item_effect_cat_to_arr(self, item_effects: ItemEffects, item_effect_cat: ItemEffectCategory):
        if item_effect_cat == ItemEffectCategory.Permanent:
            return item_effects.permanent
        elif item_effect_cat == ItemEffectCategory.OnTurnStart:
            return item_effects.on_turn_start
        elif item_effect_cat == ItemEffectCategory.OnTurnEnd:
            return item_effects.on_turn_end
        elif item_effect_cat == ItemEffectCategory.OnDamaged:
            return item_effects.on_damaged
        elif item_effect_cat == ItemEffectCategory.OnSuccessfulAbilityUsed:
            return item_effects.on_successful_ability_used
        elif item_effect_cat == ItemEffectCategory.OnSuccessfulAttack:
            return item_effects.on_successful_attack
        elif item_effect_cat == ItemEffectCategory.OnAttacked:
            return item_effects.on_attacked
        elif item_effect_cat == ItemEffectCategory.OnAbilityUsedAgainst:
            return item_effects.on_ability_used_against
        return []


    # TODO: These functions aren't abstracted particularly well. I should be able to take some pieces from
    # those below and put them into helper functions to reduce code duplication.
    def apply_on_successful_attack_or_ability_effects(self, item: Item, item_effect: Effect, self_entity: Player | NPC, other_entity: Player | NPC, other_entity_index: int, damage_dealt: int) -> Tuple[int, str]:
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if not item_effect.meets_conditions(self_entity, item):
            return (damage_dealt, "")

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value
            )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{0}" + f" is now {status_effect.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value
                )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{0}" + f" is now {status_effect.name} from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.DmgBuffSelfMaxHealth:
            additional_dmg = int(item_effect.effect_value * self_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {item.get_full_name()}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffSelfRemainingHealth:
            additional_dmg = int(item_effect.effect_value * self_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {item.get_full_name()}"
            )

        if item_effect.effect_type == EffectType.DmgBuffOtherMaxHealth:
            additional_dmg = int(item_effect.effect_value * other_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {item.get_full_name()}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffOtherRemainingHealth:
            additional_dmg = int(item_effect.effect_value * other_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {item.get_full_name()}"
            )            

        # TODO: When legendary enemies are implemented, I'll need to handle that here

        if item_effect.effect_type == EffectType.DmgBuffPoisoned:
            if any(status_effect.key == StatusEffectKey.Poisoned for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = int(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage from {item.get_full_name()}"
                )

        if item_effect.effect_type == EffectType.DmgBuffBleeding:
            if any(status_effect.key == StatusEffectKey.Bleeding for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = int(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage from {item.get_full_name()}"
                )

        # TODO: When armor changes are implemented, I'll want to implement the armor effects here

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = int(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, 0, 0, other_entity.get_equipment())
            return (damage_dealt, f"Stole {health_steal} HP from " + "{" + f"{other_entity_index}" + "}" + f" using {item.get_full_name()}")

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = int(item_effect.effect_value * other_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            other_entity.get_expertise().remove_mana(mana_steal)
            return (damage_dealt, f"Stole {mana_steal} mana from " + "{" + f"{other_entity_index}" + "}" + f" using {item.get_full_name()}")

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)
            self_entity.get_expertise().heal(healing)
            return (damage_dealt, f"Healed {healing} HP from {item.get_full_name()}")
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = int(item_effect.effect_value * self_entity.get_expertise().max_hp)
            self_entity.get_expertise().heal(healing)
            return (damage_dealt, f"Healed {healing} HP from {item.get_full_name()}")

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, f"Restored {restoration} mana from {item.get_full_name()}")
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = int(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, f"Restored {restoration} mana from {item.get_full_name()}")

        return (damage_dealt, "")

    def apply_on_attacked_or_damaged_effects(self, item: Item, item_effect: Effect, self_entity: Player | NPC, other_entity: Player | NPC, self_entity_index: int, damage_dealt: int):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if not item_effect.meets_conditions(self_entity, item):
            return ""

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                source_str=f"{item.get_full_name()}"
            )
            self.status_effects.append(status_effect)
            return "{" + f"{self_entity_index}" + "}" + f" is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(status_effect)
            return "{" + f"{self_entity_index}" + "}" + f" is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgReflect and damage_dealt > 0:
            armor = other_entity.get_equipment().get_total_reduced_armor(other_entity.get_expertise().level)
            percent_dmg_reduct = other_entity.get_dueling().get_total_percent_dmg_reduct()

            damage_to_reflect = int(damage_dealt * item_effect.effect_value)
            other_entity.get_expertise().damage(damage_to_reflect, armor, percent_dmg_reduct, other_entity.get_equipment())
            return "{" + f"{self_entity_index}" + "}" + f" reflected {damage_to_reflect} damage back to " + "{0}"

        # TODO: When armor changes are implemented, I'll want to implement the armor effects here

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = int(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, 0, 0, other_entity.get_equipment())
            return f"Stole {health_steal} HP from " + "{0}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = int(item_effect.effect_value * other_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            other_entity.get_expertise().remove_mana(mana_steal)
            return f"Stole {mana_steal} mana from " + "{0}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)
            self_entity.get_expertise().heal(healing)
            return f"Healed {healing} HP from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = int(item_effect.effect_value * self_entity.get_expertise().max_hp)
            self_entity.get_expertise().heal(healing)
            return f"Healed {healing} HP from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return f"Restored {restoration} mana from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = int(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return f"Restored {restoration} mana from {item.get_full_name()}"

        return ""

    def apply_chance_status_effect_from_total_item_effects(self, item_effect_cat: ItemEffectCategory, target: Player | NPC, self_entity: Player | NPC, target_index: int):
        # The reason this is abstracted is because we should only ever apply status effect conditions like this
        # once. If we were to do the aggregate repeatedly for each item that contributes that'd be too powerful,
        # and if we were to do each item separately, then it wouldn't actually be the sum of the probability which
        # is intuitive to the player.

        # TODO: In the future, I may also confer positive status effects using this system, at which point I'll need to
        # add a self_index as well.
        
        result_strs: List[str] = []

        # TODO: There's probably a way to make this neater.
        chance_poisoned = 0
        turns_poisoned = 0
        chance_bleeding = 0
        turns_bleeding = 0
        chance_faltering = 0
        turns_faltering = 0
        chance_taunted = 0
        turns_taunted = 0
        chance_convinced = 0
        turns_convinced = 0

        for item in self_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                item_effects_arr: List[Effect] = self.map_item_effect_cat_to_arr(item_effects, item_effect_cat)

                for item_effect in item_effects_arr:
                    if not item_effect.meets_conditions(self_entity, item):
                        continue

                    if item_effect.effect_type == EffectType.ChancePoisoned:
                        chance_poisoned += int(item_effect.effect_value)
                        turns_poisoned = max(turns_poisoned, item_effect.effect_time)
                    if item_effect.effect_type == EffectType.ResistPoisoned:
                        chance_poisoned -= int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.ChanceBleeding:
                        chance_bleeding += int(item_effect.effect_value)
                        turns_bleeding = max(turns_bleeding, item_effect.effect_time)
                    if item_effect.effect_type == EffectType.ResistBleeding:
                        chance_bleeding -= int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.ChanceFaltering:
                        chance_faltering += int(item_effect.effect_value)
                        turns_faltering = max(turns_faltering, item_effect.effect_time)
                    if item_effect.effect_type == EffectType.ResistFaltering:
                        chance_faltering -= int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.ChanceTaunted:
                        chance_taunted += int(item_effect.effect_value)
                        turns_taunted = max(turns_taunted, item_effect.effect_time)
                    if item_effect.effect_type == EffectType.ResistTaunted:
                        chance_taunted -= int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.ChanceConvinced:
                        chance_convinced += int(item_effect.effect_value)
                        turns_convinced = max(turns_convinced, item_effect.effect_time)
                    if item_effect.effect_type == EffectType.ResistConvinced:
                        chance_convinced -= int(item_effect.effect_value)

        if random() < chance_poisoned:
            status_effect = Poisoned(
                turns_remaining=turns_poisoned,
                value=POISONED_PERCENT_HP
            )
            target.get_dueling().status_effects.append(status_effect)
            result_strs.append("{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {turns_poisoned}")

        if random() < chance_bleeding:
            status_effect = Bleeding(
                turns_remaining=turns_bleeding,
                value=BLEED_PERCENT_HP
            )
            target.get_dueling().status_effects.append(status_effect)
            result_strs.append("{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {turns_bleeding}")

        if random() < chance_faltering:
            status_effect = TurnSkipChance(
                turns_remaining=turns_faltering,
                value=1
            )
            target.get_dueling().status_effects.append(status_effect)
            result_strs.append("{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {turns_faltering}")

        if random() < chance_taunted:
            status_effect = Taunted(
                turns_remaining=turns_taunted,
                forced_to_attack=self_entity
            )
            target.get_dueling().status_effects.append(status_effect)
            result_strs.append("{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {turns_taunted}")

        if random() < chance_convinced:
            status_effect = CannotTarget(
                turns_remaining=turns_convinced,
                cant_target=self_entity
            )
            target.get_dueling().status_effects.append(status_effect)
            result_strs.append("{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {turns_convinced}")

        return result_strs

    def apply_on_turn_start_or_end_effects(self, item: Item, item_effect: Effect, entity: Player | NPC, entity_name: str):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if not item_effect.meets_conditions(entity, item):
            return ""

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                source_str=f"{item.get_full_name()}"
            )
            self.status_effects.append(status_effect)
            return f"{entity_name} is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(status_effect)
            return f"{entity_name} is now {status_effect.name} from {item.get_full_name()}"

        # TODO: When armor changes are implemented, I'll want to implement the armor effects here

        return ""


    def apply_consumable_item_effect(self, item: Item, item_effect: Effect, self_entity: Player | NPC, target_entity: Player | NPC):
        if not item_effect.meets_conditions(self_entity, item):
            return ""

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                source_str=f"{item.get_full_name()}"
            )
            self.status_effects.append(status_effect)
            return "{1}" + f" is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{item.get_full_name()}"
                )
            self.status_effects.append(status_effect)
            return "{1}" + f" is now {status_effect.name} from {item.get_full_name()}"

        # TODO: When armor changes are implemented, I'll want to implement the armor effects here

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = int(item_effect.effect_value * target_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            target_entity.get_expertise().damage(health_steal, 0, 0, target_entity.get_equipment())
            return f"Stole {health_steal} HP from " + "{1}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = int(item_effect.effect_value * target_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            target_entity.get_expertise().remove_mana(mana_steal)
            return f"Stole {mana_steal} mana from " + "{1}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)
            self_entity.get_expertise().heal(healing)
            return f"Healed {healing} HP from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = int(item_effect.effect_value * self_entity.get_expertise().max_hp)
            self_entity.get_expertise().heal(healing)
            return f"Healed {healing} HP from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return f"Restored {restoration} mana from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = int(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return f"Restored {restoration} mana from {item.get_full_name()}"

        return ""

# -----------------------------------------------------------------------------
# DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

from features.npcs.npc import NPC
from features.player import Player

class Intent(StrEnum):
    Attack = "Attack"
    Ability = "Ability"
    Item = "Item"


class AttackActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Attack")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Attack)
            response = view.show_targets()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AbilityActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Ability")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Ability)
            response = view.show_abilities()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ItemActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Item")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            view.set_intent(Intent.Item)
            response = view.show_items()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class TargetButton(discord.ui.Button):
    def __init__(self, label: str, target: Player | NPC, index: int, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        self._target = target
        self._index = index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_target(self._target, self._index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseItemButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._exact_item_index = exact_item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_item(self._exact_item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ChooseAbilityButton(discord.ui.Button):
    def __init__(self, ability_index: int, ability: Ability, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{ability.get_name()}", row=row, emoji=ability.get_icon())
        
        self._ability_index = ability_index
        self._ability = ability

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.select_ability(self._ability_index, self._ability)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BackToActionSelectButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.exit_to_action_select()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmAbilityButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_ability()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ContinueToNextActionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Continue")
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.continue_turn()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BackUsingIntentButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label=f"Back", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.go_back_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DoActionOnTargetsButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Finish", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.do_action_on_selected_targets(is_finished=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmTargetButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Choose", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.confirm_target()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingNextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.next_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelingPrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.prev_page()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SkipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Skip")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DuelView = self.view
        if interaction.user == view.get_user_for_current_turn():
            response = view.continue_turn(skip_turn=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DuelView(discord.ui.View):
    # Using a data class instead of a tuple to make the code more readable
    @dataclass
    class DuelResult():
        game_won: bool
        winners: List[Player | NPC] | None

    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User], allies: List[Player | NPC], enemies: List[Player | NPC]):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._allies = allies
        self._enemies = enemies
        self._turn_order = sorted(allies + enemies, key=lambda x: x.get_combined_attributes().dexterity, reverse=True)
        self._turn_index = 0

        self._intent: (Intent | None) = None
        self._selected_targets: List[Player | NPC] = []
        self._targets_remaining = 1
        self._selected_ability: (Ability | None) = None
        self._selected_ability_index: int = -1
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1
        self._target_own_group: bool = False
        self._current_target: Player | NPC | None = None # For passing along to the confirmation
        self._current_target_index: int = -1
        self._selecting_targets = False # For next/prev buttons

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._additional_info_string_data = ""

        for entity in allies + enemies:
            entity.get_dueling().is_in_combat = True
            # Make sure stats are correct.
            entity.get_expertise().update_stats(entity.get_combined_attributes())

        cur_entity: (Player | NPC) = self._turn_order[self._turn_index]
        if isinstance(cur_entity, Player):
            self.show_actions()
        # TODO: Handle NPCs doing their own turns

    def get_user_from_player(self, player: Player):
        for user in self._users:
            if self._database[str(self._guild_id)]["members"][str(user.id)] == player:
                return user
        return None

    def get_user_for_current_turn(self):
        cur_turn_entity = self._turn_order[self._turn_index]
        if isinstance(cur_turn_entity, Player):
            return self.get_user_from_player(cur_turn_entity)
        return None

    def get_name(self, entity: Player | NPC):
        if isinstance(entity, NPC):
            return entity.get_name()
        user = self.get_user_from_player(entity)
        return user.display_name if user is not None else "Player Name"

    def get_turn_index(self, entity: Player | NPC):
        for i, other_entity in enumerate(self._turn_order):
            if other_entity == entity:
                return i
        return -1

    def check_for_win(self) -> DuelResult:
        allies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._allies))
        enemies_alive: List[Player | NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._enemies))
        
        if len(allies_alive) == 0 and len(enemies_alive) == 0: # Tie, which may happen due to reflected damage
            return self.DuelResult(True, None)
        if len(enemies_alive) == 0:
            return self.DuelResult(True, self._allies)
        if len(allies_alive) == 0:
            return self.DuelResult(True, self._enemies)
        
        return self.DuelResult(False, None)

    def _reset_turn_variables(self, reset_actions=False):
        self._intent = None
        self._selected_targets = []
        self._targets_remaining = 1
        self._selected_ability = None
        self._selected_ability_index = -1
        self._selected_item = None
        self._selected_item_index = -1
        self._target_own_group = False
        self._current_target = None
        self._current_target_index = -1
        self._selecting_targets = False
        self._page = 0

        if reset_actions:
            self._actions_remaining = self._turn_order[self._turn_index].get_dueling().init_actions_remaining

    def set_next_turn(self):
        previous_entity: Player | NPC = self._turn_order[self._turn_index]
        
        item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnEnd, previous_entity, previous_entity, 0)
        
        for result_str in item_status_effects:
            formatted_str = result_str.format([self.get_name(previous_entity)])
            self._additional_info_string_data += formatted_str    
        
        for item in previous_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_end:
                result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, previous_entity, self.get_name(previous_entity))
                if result_str != "":
                    self._additional_info_string_data += result_str + " "

        self._turn_index = (self._turn_index + 1) % len(self._turn_order)
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        entity: Player | NPC = self._turn_order[self._turn_index]

        item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnStart, entity, entity, 0)
        
        for result_str in item_status_effects:
            formatted_str = result_str.format([self.get_name(previous_entity)])
            self._additional_info_string_data += formatted_str    

        for item in previous_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_start:
                result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, entity, self.get_name(entity))
                if result_str != "":
                    self._additional_info_string_data += result_str + " "
        
        start_damage: int = 0
        start_heals: int = 0
        max_should_skip_chance: float = 0
        heals_from_poison: bool = any(se.key == StatusEffectKey.PoisonHeals for se in entity.get_dueling().status_effects)

        for se in entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.FixedDmgTick:
                start_damage += int(se.value)
            if se.key == StatusEffectKey.Bleeding:
                start_damage += int(entity.get_expertise().max_hp * se.value)
            if se.key == StatusEffectKey.Poisoned:
                if heals_from_poison:
                    start_heals += int(entity.get_expertise().max_hp * se.value)
                else:
                    start_damage += int(entity.get_expertise().max_hp * se.value)
            if se.key == StatusEffectKey.RegenerateHP:
                start_heals += int(entity.get_expertise().max_hp * se.value)
            # Only take the largest chance to skip the turn
            if se.key == StatusEffectKey.TurnSkipChance:
                max_should_skip_chance = max(se.value, max_should_skip_chance)
        
        # Fixed damage is taken directly, no reduction
        entity.get_expertise().damage(start_damage, 0, 0, entity.get_equipment())
        if start_damage > 0:
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_damage} damage! "

        entity.get_expertise().heal(start_heals)
        if start_heals > 0:
            self._additional_info_string_data += f"{self.get_name(entity)} had {start_heals} health restored! "

        if random() < max_should_skip_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            self._additional_info_string_data += f"{self.get_name(entity)}'s turn was skipped!"

        duel_result = self.check_for_win()
        if duel_result.game_won:
            return duel_result

        # Continue to iterate if the fixed damage killed the current entity
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        self._reset_turn_variables(True)

        return duel_result

    def _is_ally(self, entity: Player | NPC):
        cur_turn_player = self._turn_order[self._turn_index]
        if cur_turn_player in self._allies:
            return entity in self._allies
        else:
            return entity in self._enemies

    def get_duel_info_str(self):
        info_str = "──────────\n"
        for i, entity in enumerate(self._turn_order):
            group_icon = ":handshake:" if self._is_ally(entity) else ":imp:"
            info_str += f"({i + 1}) **{self.get_name(entity)}** {group_icon}\n\n{entity.get_expertise().get_health_and_mana_string()}"
            if len(entity.get_dueling().status_effects) > 0:
                info_str += f"\n\n{entity.get_dueling().get_statuses_string()}"
            info_str += "\n──────────\n"

        player_name = self.get_user_for_current_turn().display_name

        return info_str + f"\n*It's {player_name}'s turn!*"

    def get_selected_entity_full_duel_info_str(self):
        if self._current_target is None:
            return ""

        name = self.get_name(self._current_target)
        expertise = self._current_target.get_expertise()
        dueling = self._current_target.get_dueling()

        duel_string = f"──────────\n({self._current_target_index + 1}) **{name}**\n\n{expertise.get_health_and_mana_string()}"
        if len(dueling.status_effects) > 0:
            duel_string += f"\n\n{dueling.get_statuses_string()}"

        return f"{duel_string}\n──────────"

    def get_victory_screen(self, duel_result: DuelResult):
        self.clear_items()

        if duel_result.winners is None:
            for entity in self._turn_order:
                entity.get_dueling().status_effects = []
                entity.get_dueling().is_in_combat = False
                entity.get_dueling().reset_ability_cds()

                entity.get_expertise().update_stats(entity.get_combined_attributes())
                entity.get_expertise().hp = entity.get_expertise().max_hp
                entity.get_expertise().mana = entity.get_expertise().max_mana
                
                entity.get_stats().dueling.duels_fought += 1
                entity.get_stats().dueling.duels_tied += 1

                entity.get_expertise().level_up_check()

            return Embed(
                title="Victory for Both and Neither",
                description="A hard-fought battle resulting in a tie. Neither side emerges truly victorious and yet both have defeated their enemies."
            )
        
        # TODO: Implement what happens when an NPC group wins/loses.
        losers = self._allies if duel_result.winners == self._enemies else self._enemies

        for winner in duel_result.winners:
            winner.get_stats().dueling.duels_fought += 1
            winner.get_stats().dueling.duels_won += 1
        for loser in losers:
            loser.get_stats().dueling.duels_fought += 1

        if all(isinstance(entity, Player) for entity in self._turn_order):
            # This should only happen in a PvP duel
            winner_str = ""
            winner_xp = ceil(2 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                winner_expertise = winner.get_expertise()
                winner_dueling = winner.get_dueling()
                
                final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                
                winner_dueling.reset_ability_cds()
                winner_dueling.status_effects = []
                winner_dueling.is_in_combat = False

                winner_expertise.update_stats(winner.get_combined_attributes())
                winner_expertise.hp = winner_expertise.max_hp
                winner_expertise.mana = winner_expertise.max_mana

                winner_expertise.level_up_check()

                winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"

            loser_str = ""
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (2 * len(losers)))
            for loser in losers:
                loser_expertise = loser.get_expertise()
                loser_dueling = loser.get_dueling()
                
                final_loser_xp = loser_expertise.add_xp_to_class(loser_xp, ExpertiseClass.Guardian, loser.get_equipment())

                loser_dueling.reset_ability_cds()
                loser_dueling.status_effects = []
                loser_dueling.is_in_combat = False

                loser_expertise.update_stats(loser.get_combined_attributes())
                loser_expertise.hp = loser_expertise.max_hp
                loser_expertise.mana = loser_expertise.max_mana

                loser_expertise.level_up_check()

                loser_str += f"{self.get_name(loser)} *(+{final_loser_xp} Guardian xp)*\n"

            return Embed(title="Duel Finished", description=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}\nPractice for the journeys yet to come.")

        return Embed(title="Beyond the Veil", description="Hello, wayward adventurer. You've reached the in-between -- how strange.")

    def show_actions(self):
        self.clear_items()

        entity: Player | NPC = self._turn_order[self._turn_index]
        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in entity.get_dueling().status_effects)

        if not restricted_to_items:
            self.add_item(AttackActionButton())
            self.add_item(AbilityActionButton())
        self.add_item(ItemActionButton())
        self.add_item(SkipButton())

        self._reset_turn_variables()

        return Embed(title="Choose an Action", description=self.get_duel_info_str())

    def set_intent(self, intent: Intent):
        self._intent = intent

    def show_targets(self, target_own_group: bool=False):
        self.clear_items()

        self._selecting_targets = True

        cur_turn_entity: Player = self._turn_order[self._turn_index]
        taunt_target: Player | NPC | None = None
        for se in cur_turn_entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.Taunted:
                # TODO: Why not just check this instead of using keys? Is there
                # any risk associated with it? Arguably, it's nicer to potentially
                # have the enum moved to the new enums file and avoid import issues.
                assert(isinstance(se, Taunted))
                taunt_target = se.forced_to_attack
                break
        if taunt_target is not None:
            self._selected_targets = [taunt_target]
            return self.do_action_on_selected_targets()

        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Selected Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""
        
        self._target_own_group = target_own_group and self._intent != Intent.Attack

        # This should only be called for a Player
        targets: List[Player | NPC] = []

        # In the special case of attacking with a weapon, display information about the weapon so the user is informed.
        main_hand_item = cur_turn_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(cur_turn_entity.get_combined_attributes().strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        description = "" if self._intent != Intent.Attack else f"{self.get_name(cur_turn_entity)} is attacking with {main_hand_item.get_full_name() if main_hand_item is not None else 'a good slap'} for {weapon_stats.get_range_str()}.\n\n"

        if self._current_target is not None:
            description += self.get_selected_entity_full_duel_info_str() + "\n\n"

        if (cur_turn_entity in self._enemies and target_own_group) or (cur_turn_entity in self._allies and not target_own_group):
            targets = self._enemies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        elif (cur_turn_entity in self._enemies and not target_own_group) or (cur_turn_entity in self._allies and target_own_group):
            targets = self._allies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        
        all_targets = targets[self._page * self._NUM_PER_PAGE:min(len(targets), (self._page + 1) * self._NUM_PER_PAGE)]
        filtered_targets = list(filter(lambda target: target.get_expertise().hp > 0, all_targets)) if not self._target_own_group else all_targets
        page_slots = sorted(filtered_targets, key=lambda target: self.get_turn_index(target))
        for i, target in enumerate(page_slots):
            turn_number: int = self.get_turn_index(target)
            if isinstance(target, NPC):
                self.add_item(TargetButton(f"({turn_number + 1}) {target.get_name()}", target, turn_number, i))
            if isinstance(target, Player):
                user = self.get_user_from_player(target)
                self.add_item(TargetButton(f"({turn_number + 1}) {user.display_name}", target, turn_number, i))

        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(targets) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        if self._current_target is not None and self._current_target_index != -1:
            self.add_item(ConfirmTargetButton(min(4, len(page_slots))))
        if len(self._selected_targets) > 0:
            # This handles the cases where you might not want/need to select the max number
            # of possible targets.
            self.add_item(DoActionOnTargetsButton(min(4, len(page_slots))))
        self.add_item(BackUsingIntentButton(min(4, len(page_slots))))

        return Embed(title="Choose a Target", description=description)

    def attack_selected_targets(self):
        attacker = self._turn_order[self._turn_index]
        attacker_name = self.get_name(attacker)
        attacker_attrs = attacker.get_combined_attributes()
        attacker_equipment = attacker.get_equipment()

        generating_value = 0
        tarnished_value = 0
        for se in attacker.get_dueling().status_effects:
            if se.key == StatusEffectKey.Generating:
                generating_value = se.value
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        cursed_coins_damage = 0

        main_hand_item = attacker_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        # Base possible damage is [1, 2], basically fist fighting
        unarmed_strength_bonus = int(attacker_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        splash_dmg = 0
        splash_percent_dmg = 0
        for item in attacker_equipment.get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for item_effect in item_effects.permanent:
                    if item_effect.effect_type == EffectType.SplashDmg:
                        splash_dmg += int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.SplashPercentMaxDmg:
                        splash_percent_dmg += int(weapon_stats.get_max_damage() * item_effect.effect_value)

        result_strs = [f"{attacker_name} attacked using {main_hand_item.get_full_name() if main_hand_item is not None else 'a good slap'}!\n"]
        for i, target in enumerate(self._selected_targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()
            target_attrs = target.get_combined_attributes()

            target_name = self.get_name(target)
            target_dodged = random() < target_attrs.dexterity * DEX_DODGE_SCALE
            
            if target_dodged:
                target.get_stats().dueling.attacks_dodged += 1
                result_strs.append(f"{target_name} dodged the attack")
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < attacker_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                attacker.get_stats().dueling.critical_hit_successes += 1

            piercing_dmg = 0
            piercing_percent_dmg = 0
            critical_hit_dmg_buff = 0
            for item in attacker_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(attacker, item):
                            continue

                        if item_effect.effect_type == EffectType.PiercingDmg:
                            piercing_dmg += int(item_effect.effect_value)
                        if item_effect.effect_type == EffectType.PiercingPercentDmg:
                            piercing_percent_dmg += item_effect.effect_value
                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)
                        
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1 
            base_damage = weapon_stats.get_random_damage(attacker_attrs, item_effects)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * STR_DMG_SCALE * max(attacker_attrs.strength, 0)), damage)

            # Doing these after damage computation because the player doesn't get an indication the effect occurred
            # until the Continue screen, so it feels slightly more natural to have them not affect damage dealt. I
            # may reverse this decision later.
            result_strs += [s.format([target_name]) for s in attacker.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, attacker, i + 1)]

            for item in attacker_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_attack:
                    damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, attacker, target, i + 1, damage)
                    if result_str != "":
                        result_strs.append(result_str.format([attacker_name, target_name]))

            result_strs += [s.format([attacker_name]) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAttacked, attacker, target, 0)]

            for item in target_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_attacked:
                    result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, i + 1, damage)
                    if result_str != "":
                        result_strs.append(result_str.format([target_name, attacker_name]))

            target_armor = max(target_equipment.get_total_reduced_armor(target_expertise.level) - piercing_dmg - int(damage * piercing_percent_dmg), 0)
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()

            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, target_equipment)

            if actual_damage_dealt > 0:
                result_strs += [s.format([attacker_name]) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, attacker, target, 0)]
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, i + 1, actual_damage_dealt)
                        if result_str != "":
                            result_strs.append(result_str.format([target_name, attacker_name]))

            attacker.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != attacker), se.on_being_hit_buffs))
                    result_strs.append(f"{target_name} gained {se.get_buffs_str()}")
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)
            target.get_expertise().update_stats(target.get_combined_attributes())

            generating_string = ""
            if generating_value != 0:
                attacker.get_inventory().add_coins(int(generating_value))
                generating_string = f" and gained {generating_value} coins"

                if tarnished_value != 0:
                    cursed_coins_damage += int(tarnished_value * generating_value)
            
            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}{generating_string}")
        
            attacker.get_stats().dueling.attacks_done += 1
        
        if cursed_coins_damage != 0:
            if attacker in self._enemies:
                for other in self._allies:
                    other.get_expertise().damage(cursed_coins_damage, 0, 0, other.get_equipment())
                    attacker.get_stats().dueling.damage_dealt += cursed_coins_damage
                
                names_str = ", ".join([self.get_name(other) for other in self._allies])
                result_strs.append(f"{attacker_name} dealt {cursed_coins_damage} damage to {names_str}")
            elif attacker in self._allies:
                for other in self._enemies:
                    other.get_expertise().damage(cursed_coins_damage, 0, 0, other.get_equipment())
                    attacker.get_stats().dueling.damage_dealt += cursed_coins_damage
                
                names_str = ", ".join([self.get_name(other) for other in self._enemies])
                result_strs.append(f"{attacker_name} dealt {cursed_coins_damage} damage to {names_str} using Cursed Coins")

        if splash_dmg > 0 or splash_percent_dmg > 0:
            if attacker in self._enemies:
                for target in self._allies:
                    target_armor = target.get_equipment().get_total_reduced_armor(target.get_expertise().level)
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                    target.get_expertise().damage(splash_dmg + splash_percent_dmg, target_armor, percent_dmg_reduct, target.get_equipment())
                names_str = ", ".join([self.get_name(other) for other in self._allies])
                result_strs.append(f"{attacker_name} dealt {splash_dmg + splash_percent_dmg} splash damage to {names_str}")
            else:
                for target in self._enemies:
                    target_armor = target.get_equipment().get_total_reduced_armor(target.get_expertise().level)
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                    target.get_expertise().damage(splash_dmg + splash_percent_dmg, target_armor, percent_dmg_reduct, target.get_equipment())
                names_str = ", ".join([self.get_name(other) for other in self._enemies])
                result_strs.append(f"{attacker_name} dealt {splash_dmg + splash_percent_dmg} splash damage to {names_str}")

        return "\n".join(result_strs)

    def use_ability_on_selected_targets(self):
        if self._selected_ability is None:
            return self.show_abilities("*Error: That ability doesn't exist.*")

        caster = self._turn_order[self._turn_index]
        names = [self.get_name(caster), *list(map(lambda x: self.get_name(x), self._selected_targets))]
        result_str = self._selected_ability.use_ability(caster, self._selected_targets)

        caster.get_stats().dueling.abilities_used += 1
        # TODO: Add level up check mid-combat?
        xp_to_add: int = int(self._selected_ability.get_level_requirement() / 2)
        class_key: ExpertiseClass = self._selected_ability.get_class_key()
        final_xp = caster.get_expertise().add_xp_to_class(xp_to_add, class_key, caster.get_equipment())

        return result_str.format(*names) + f"\n\n*You gained {final_xp} {class_key} xp!*"

    def use_item_on_selected_targets(self):
        if self._selected_item is None:
            return self.show_items("*Error: That item doesn't exist.*")

        applicator = self._turn_order[self._turn_index]
        applicator_dueling = applicator.get_dueling()
        applicator_name = self.get_name(applicator)

        result_strs = []
        for i, target in enumerate(self._selected_targets):
            result_strs += [s.format([self.get_name(target)]) for s in applicator_dueling.apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, applicator, i + 1)]

            item_effects = self._selected_item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    result_str = applicator_dueling.apply_consumable_item_effect(self._selected_item, effect, applicator, target)
                    result_strs.append(result_str.format(applicator_name, self.get_name(target)))

        applicator.get_inventory().remove_item(self._selected_item_index, 1)
        applicator.get_stats().dueling.items_used += 1
        
        return "\n".join(result_strs)

    def confirm_target(self):
        if self._current_target is None:
            return self.show_targets()

        selected_target_names = "\n".join(list(map(lambda x: self.get_name(x), self._selected_targets)))
        selected_targets_str = f"Current Targets:\n\n{selected_target_names}\n\n" if len(selected_target_names) > 0 else ""

        if self._current_target != self._turn_order[self._current_target_index]:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}*Error: That target changed position in the turn order or something else terrible happened.*\n\n{self._targets_remaining} targets remaining.")
        
        if self._current_target in self._selected_targets:
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You already selected that target. {self._targets_remaining} targets remaining.")
        
        entity = self._turn_order[self._turn_index]
        if any(se.key == StatusEffectKey.CannotTarget and se.cant_target == entity for se in entity.get_dueling().status_effects):
            return Embed(title="Choose a Target", description=f"{selected_targets_str}You can't select that target due to being Convinced. {self._targets_remaining} targets remaining.")

        self._selected_targets.append(self._current_target)
        self._targets_remaining -= 1
        self._current_target = None

        return self.do_action_on_selected_targets()

    def do_action_on_selected_targets(self, is_finished=False):
        # I'm using a boolean for that case at the moment rather than setting self._targets_remaining to 0, just to
        # make a clear distinction about this case in the code.
        if self._targets_remaining == 0 or self._targets_remaining == -1 or is_finished:
            self._page = 0
            self.clear_items()
            self.add_item(ContinueToNextActionButton())

            catch_phrases = []
            result_str = ""
            if self._intent == Intent.Attack:
                catch_phrases = [
                    "Now, strike!",
                    "Yield to none!",
                    "Glory is yours!"
                ]
                result_str = self.attack_selected_targets()
            if self._intent == Intent.Ability:
                catch_phrases = [
                    "Behold true power!",
                    "Surge as they crumble!",
                    "Calamity unleashed!"
                ]
                result_str = self.use_ability_on_selected_targets()
            if self._intent == Intent.Item:
                catch_phrases = [
                    "A useful trinket!",
                    "The time is now!",
                    "A perfect purpose!"
                ]
                result_str = self.use_item_on_selected_targets()
            
            return Embed(title=choice(catch_phrases), description=result_str)
        self._page = 0
        self._selecting_targets = True
        return self.show_targets(self._target_own_group)

    def show_items(self, error_str: str | None=None):
        self._page = 0
        self._get_current_items_page_buttons()
        return self._get_current_page_info(error_str)

    def show_abilities(self, error_str: str | None=None):
        self._page = 0
        self._get_current_abilities_page_buttons()
        return self._get_current_page_info(error_str)

    def _get_current_items_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index]
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Consumable.UsableWithinDuels])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(ChooseItemButton(exact_item_index, item, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            self.add_item(ConfirmItemButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def _get_current_abilities_page_buttons(self):
        self.clear_items()
        player: Player = self._turn_order[self._turn_index]
        expertise: Expertise = player.get_expertise()
        dueling: Dueling = player.get_dueling()
        # Theoretically, this should only account for equipment/expertise, but if I add in an ability that reduces memory,
        # I'll want to have this.
        available_memory: int = max(0, player.get_combined_attributes().memory)

        page_slots = dueling.abilities[self._page * self._NUM_PER_PAGE:min(len(dueling.abilities), (self._page + 1) * self._NUM_PER_PAGE)][:available_memory]
        for i, ability in enumerate(page_slots):
            self.add_item(ChooseAbilityButton(i + (self._page * self._NUM_PER_PAGE), ability, i))
        
        if self._page != 0:
            self.add_item(DuelingPrevButton(min(4, len(page_slots))))
        if len(dueling.abilities) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(DuelingNextButton(min(4, len(page_slots))))

        sanguinated_active = any(se.key == StatusEffectKey.ManaToHP for se in dueling.status_effects)

        if self._selected_ability is not None:
            if self._selected_ability.get_cur_cooldown() == 0:
                if expertise.mana >= self._selected_ability.get_mana_cost() or sanguinated_active:
                    self.add_item(ConfirmAbilityButton(min(4, len(page_slots))))
        self.add_item(BackToActionSelectButton(min(4, len(page_slots))))

    def exit_to_action_select(self):
        self._reset_turn_variables()
        return self.show_actions()

    def _get_current_page_info(self, error_str: str | None=None):
        player: Player = self._turn_order[self._turn_index]
        description = ""
        if self._intent == Intent.Item:
            description = "Selected item info will be displayed here."
            if self._selected_item is not None:
                description = f"──────────\n{self._selected_item}\n──────────"
        if self._intent == Intent.Ability:
            description = f"{player.get_expertise().get_health_and_mana_string()}\nCoins: {player.get_inventory().get_coins_str()}\n\n"
            if self._selected_ability is not None:
                description += f"──────────\n{self._selected_ability}\n──────────"
            else:
                description += "Selected ability info will be displayed here."
        if error_str is not None:
            description += f"\n\n{error_str}"
        return Embed(title=f"Choose an {self._intent}", description=description)

    def next_page(self):
        self._page += 1
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_current_items_page_buttons()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            self._get_current_abilities_page_buttons()
        if self._selecting_targets:
            self._current_target = None
            self._current_target_index = -1
            return self.show_targets(self._target_own_group)
        return self._get_current_page_info()

    def select_item(self, exact_item_index: int, item: Item):
        self._selected_item_index = exact_item_index
        self._selected_item = item

        self._get_current_items_page_buttons()
        return self._get_current_page_info()
        
    def select_ability(self, ability_index: int, ability: Ability):
        self._selected_ability_index = ability_index
        self._selected_ability = ability

        self._get_current_abilities_page_buttons()
        return self._get_current_page_info()

    def confirm_item(self):
        if self._selected_item is None:
            return self.show_items("*Error: That item couldn't be selected.*")

        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_inventory().item_exists(self._selected_item)
        if self._selected_item is not None and found_index == self._selected_item_index:
            consumable_stats = self._selected_item.get_consumable_stats()
            if consumable_stats is None:
                return self.show_items("*Error: That item doesn't have consumable stats.*")
            
            self._targets_remaining = consumable_stats.get_num_targets()
            target_own_group = consumable_stats.get_target_own_group()

            if self._targets_remaining == 0:
                self._selected_targets = [entity]
                return self.do_action_on_selected_targets()
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    self._selected_targets = self._enemies
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    self._selected_targets = self._allies
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_items("*Error: That item couldn't be selected.*")

    def confirm_ability(self):
        if self._selected_ability is None:
            return self.show_abilities("*Error: That item couldn't be selected.*")

        entity: Player | NPC = self._turn_order[self._turn_index]
        found_index = entity.get_dueling().ability_exists(self._selected_ability)
        if found_index == self._selected_ability_index:
            self._targets_remaining = self._selected_ability.get_num_targets()
            target_own_group = self._selected_ability.get_target_own_group()

            if self._targets_remaining == 0:
                self._selected_targets = [entity]
                return self.do_action_on_selected_targets()
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    self._selected_targets = self._enemies
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    self._selected_targets = self._allies
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_abilities("*Error: That ability couldn't be selected.*")

    def select_target(self, target: Player | NPC, index: int):
        self._current_target_index = index
        self._current_target = target

        return self.show_targets(self._target_own_group)
 
    def continue_turn(self, skip_turn=False):
        self._page = 0
        cur_entity: (Player | NPC) = self._turn_order[self._turn_index]

        # Check here before setting next turn, just in case
        duel_result = self.check_for_win()
        if duel_result.game_won:
            return self.get_victory_screen(duel_result)

        dueling: Dueling = cur_entity.get_dueling()
        dueling.actions_remaining = max(0, dueling.actions_remaining - 1)
        if dueling.actions_remaining == 0 or skip_turn:
            # CDs and status effect time remaining decrement at the end of the turn,
            # so they actually last a turn
            dueling.decrement_all_ability_cds()
            dueling.decrement_statuses_time_remaining()
            cur_entity.get_expertise().update_stats(cur_entity.get_combined_attributes())
            duel_result = self.set_next_turn()
            if duel_result.game_won:
                return self.get_victory_screen(duel_result)
        
        next_entity: (Player | NPC) = self._turn_order[self._turn_index]
        next_entity_dueling: Dueling = next_entity.get_dueling()
        if isinstance(next_entity, Player):
            next_entity_dueling.actions_remaining = next_entity_dueling.init_actions_remaining
            return self.show_actions()
        # TODO: Handle NPC AI doing their own turns

    def go_back_using_intent(self):
        self._page = 0
        self._selecting_targets = False
        if self._intent == Intent.Attack:
            return self.show_actions()
        if self._intent == Intent.Ability:
            self._selected_ability = None
            self._selected_ability_index = -1
            return self.show_abilities()
        if self._intent == Intent.Item:
            self._selected_item = None
            self._selected_item_index = -1
            return self.show_items()

# -----------------------------------------------------------------------------
# PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.accept_request(interaction.user)
        if not view.all_accepted():
            await interaction.response.edit_message(embed=response, view=view, content=None)
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel. This duel has been cancelled.")
                return
            
            users: List[discord.User] = [view.get_challenger(), *view.get_opponents()]
            challenger_player: Player = view.get_challenger_player()
            opponents_players: List[Player] = view.get_opponents_players()
            
            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), users, [challenger_player], opponents_players)
            initial_info: Embed = duel_view.show_actions()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't decline this request!", view=view)
            return

        view.clear_items()
        await interaction.response.edit_message(content="The duel was declined.", view=view, embed=None)


class PlayerVsPlayerDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, challenger: discord.User, opponents: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._challenger = challenger
        self._opponents = opponents

        self._acceptances: List[discord.User] = []

        self.add_item(AcceptButton())
        self.add_item(DeclineButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_info_embed(self):
        not_accepted = list(filter(lambda x: x not in self._acceptances, self._opponents))
        not_accepted_names = "\n".join(list(map(lambda x: x.display_name, not_accepted)))
        return Embed(title="PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The game will begin when all challenged players accept the invitation to duel.\n\n**Waiting on acceptances from:**\n\n{not_accepted_names}"
        ))

    def accept_request(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user not in self._acceptances:
            self._acceptances.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._acceptances for user in self._opponents)

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in [*self._opponents, self._challenger])

    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_challenger(self):
        return self._challenger

    def get_opponents(self):
        return self._opponents

    def get_challenger_player(self):
        return self._get_player(self._challenger.id)

    def get_opponents_players(self):
        return [self._get_player(opponent.id) for opponent in self._opponents]

# -----------------------------------------------------------------------------
# GROUP PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user.id != view.get_duel_starter().id:
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't start this duel!", view=view)
            return
        
        if not view.all_accepted():
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="All players choose a team before the duel can start.")
        elif len(view.get_team_1()) == 0 or len(view.get_team_2()) == 0:
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="At least one player must be on each team.")
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel. This duel has been cancelled.")
                return

            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_team_1_players(), view.get_team_2_players())
            initial_info: Embed = duel_view.show_actions()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class Team1Button(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Team 1")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_users():
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.add_to_team_1(interaction.user)
        await interaction.response.edit_message(embed=response, view=view, content=None)


class Team2Button(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Team 2")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GroupPlayerVsPlayerDuelView = self.view

        if interaction.user not in view.get_users():
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.add_to_team_2(interaction.user)
        await interaction.response.edit_message(embed=response, view=view, content=None)


class GroupPlayerVsPlayerDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._duel_starter = users[0]

        self._team_1: List[discord.User] = []
        self._team_2: List[discord.User] = []

        self.add_item(Team1Button())
        self.add_item(Team2Button())
        self.add_item(StartButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_info_embed(self):
        team_1_names = "\n".join(list(map(lambda x: x.display_name, self._team_1)))
        team_2_names = "\n".join(list(map(lambda x: x.display_name, self._team_2)))
        return Embed(title="Group PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The game will begin when all players have selected a team and at least 1 person is on each team.\n\n──────────\n**Team 1:**\n\n{team_1_names}\n──────────\n**Team 2:**\n\n{team_2_names}\n──────────"
        ))

    def add_to_team_1(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user in self._team_2:
            self._team_2.remove(user)
        if user not in self._team_1:
            self._team_1.append(user)
        
        return self.get_info_embed()

    def add_to_team_2(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="PvP Duel Cancelled",
                description=f"{user.display_name} is already in a duel and can't accept this one!"
            )

        if user in self._team_1:
            self._team_1.remove(user)
        if user not in self._team_2:
            self._team_2.append(user)
        
        return self.get_info_embed()

    def all_accepted(self):
        return all(user in self._team_1 or user in self._team_2 for user in self._users)

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_team_1_players(self):
        return [self._get_player(user.id) for user in self._team_1]

    def get_team_2_players(self):
        return [self._get_player(user.id) for user in self._team_2]
    
    def get_bot(self):
        return self._bot

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_team_1(self):
        return self._team_1

    def get_team_2(self):
        return self._team_2

    def get_users(self):
        return self._users

    def get_duel_starter(self):
        return self._duel_starter
