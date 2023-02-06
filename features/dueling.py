from __future__ import annotations

from math import ceil
from random import choice, random

import discord
import itertools
import jsonpickle

from dataclasses import dataclass
from discord.embeds import Embed
from discord.ext import commands
from strenum import StrEnum
from features.expertise import ExpertiseClass
from features.shared.attributes import Attributes
from features.shared.constants import COMPANION_BATTLE_POINTS, POISONED_PERCENT_HP, BLEED_PERCENT_HP, DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, STR_DMG_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, WeaponStats
from features.shared.statuseffect import *

from typing import Dict, List, TYPE_CHECKING, Tuple
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
        # With the armor rework, at the start of the duel, this gets set
        # to the player/npc's total armor. When this reaches 0, damage
        # is done to the entity's health.
        self.armor: int = 0

    def damage_armor(self, damage: int):
        # This function returns the damage remaining to deal to the entity's
        # health.
        if self.armor == 0:
            return damage
        
        diff = self.armor - damage
        self.armor = max(diff, 0)

        # If there's remaining damage, this will return a positive amount of
        # it to deal to the entity's health.
        return abs(min(diff, 0))

    def get_armor_string(self, max_reduced_armor: int):
        armor_num_squares = ceil(self.armor / max_reduced_armor * 10)
        armor_squares_string = ""

        for i in range(1, 11):
            armor_squares_string += "⬜" if i <= armor_num_squares else "⬛"

        return f"Armor: {armor_squares_string} ({self.armor}/{max_reduced_armor})"

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

    def add_status_effect_with_resist(self, status_effect: StatusEffect, target: Player | NPC, target_index: int, item_effect_cat: ItemEffectCategory | None=None, resist_status_effect: Dict[StatusEffectKey, Tuple[float, List[str]]] | None=None) -> str:
        if resist_status_effect is None:
            resist_status_effect = {}
        
            for item in target.get_equipment().get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    item_effects_arr: List[Effect] = self.map_item_effect_cat_to_arr(item_effects, item_effect_cat) if item_effect_cat is not None else self.map_item_effect_cat_to_arr(item_effects, ItemEffectCategory.Permanent)

                    for item_effect in item_effects_arr:
                        if not item_effect.meets_conditions(target, item):
                            continue

                        if item_effect.effect_type == EffectType.ResistStatusEffect:
                            se_key: StatusEffectKey | None = item_effect.associated_status_effect
                            if se_key is not None:
                                current_resist_info = resist_status_effect.get(se_key, (0, []))
                                resist_status_effect[se_key] = (item_effect.effect_value + current_resist_info[0], current_resist_info[1] + [item.get_full_name()])

        chance_resist, resist_item_strs = resist_status_effect.get(status_effect.key, (0, []))
        if random() >= chance_resist:
            self.status_effects.append(status_effect)
            return "{" + f"{target_index}" + "}" + f" is now {status_effect.name} for {status_effect.turns_remaining} turns"
        else:
            items_str = ", ".join(resist_item_strs)
            return "{" + f"{target_index}" + "}" + f" resisted {status_effect.name} using {items_str}"

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
        status_strs: List[str] = [str(se) for se in self.status_effects if se.turns_remaining != 0]

        if len(status_strs) == 0:
            return ""

        return "*Status Effects:*\n\n" + "\n".join(status_strs)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.available_abilities = state.get("available_abilities", [])
        self.abilities = state.get("abilities", [])

        self.is_in_combat = state.get("is_in_combat", False)
        self.status_effects = state.get("status_effects", [])
        self.init_actions_remaining = state.get("init_actions_remaining", 1)
        self.actions_remaining = state.get("actions_remaining", 1)

        self.armor = state.get("armor", 0)

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
    def apply_on_successful_attack_or_ability_effects(self, item: Item | None, item_effect: Effect, self_entity: Player | NPC, other_entity: Player | NPC, other_entity_index: int, damage_dealt: int, source_str: str) -> Tuple[int, str]:
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if item is not None and not item_effect.meets_conditions(self_entity, item):
            return (damage_dealt, "")

        if item_effect.effect_type == EffectType.CleanseStatusEffects:
            self_entity.get_dueling().status_effects = []
            return (damage_dealt, "{0}" + f" has had their status effects removed")

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{0}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                trigger_first_turn=False
            )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{0}" + f" is now {status_effect.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{0}" + f" is now {status_effect.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgBuffSelfMaxHealth:
            additional_dmg = int(item_effect.effect_value * self_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffSelfRemainingHealth:
            additional_dmg = int(item_effect.effect_value * self_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )

        if item_effect.effect_type == EffectType.DmgBuffOtherMaxHealth:
            additional_dmg = int(item_effect.effect_value * other_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffOtherRemainingHealth:
            additional_dmg = int(item_effect.effect_value * other_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )            

        # TODO: When legendary enemies are implemented, I'll need to handle that here

        if item_effect.effect_type == EffectType.DmgBuffPoisoned:
            if any(status_effect.key == StatusEffectKey.Poisoned for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = int(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage on Poisoned target from {source_str}"
                )

        if item_effect.effect_type == EffectType.DmgBuffBleeding:
            if any(status_effect.key == StatusEffectKey.Bleeding for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = int(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage on Bleeding target from {source_str}"
                )

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{0}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            armor_from_effect: int = int(max_reduced_armor * item_effect.effect_value)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{0}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = int(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, other_entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            return (damage_dealt, "{0}" + f" stole {health_steal} HP from " + "{" + f"{other_entity_index}" + "}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = int(item_effect.effect_value * other_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            other_entity.get_expertise().remove_mana(mana_steal)
            return (damage_dealt, "{0}" + f" stole {mana_steal} mana from " + "{" + f"{other_entity_index}" + "}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{0}" + f" healed {healing} HP from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = int(item_effect.effect_value * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{0}" + f" healed {healing} HP from {source_str}")

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{0}" + f" restored {restoration} mana from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = int(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{0}" + f" restored {restoration} mana from {source_str}")

        return (damage_dealt, "")

    def apply_on_attacked_or_damaged_effects(self, item: Item | None, item_effect: Effect, self_entity: Player | NPC, other_entity: Player | NPC, self_entity_index: int, damage_dealt: int, source_str: str):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if item is not None and not item_effect.meets_conditions(self_entity, item):
            return (damage_dealt, "")

        if item_effect.effect_type == EffectType.CleanseStatusEffects:
            self_entity.get_dueling().status_effects = []
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" has had their status effects removed")

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {attr_mod.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                source_str=f"{source_str}",
                trigger_first_turn=False
            )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {status_effect.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=False
                )
            self.status_effects.append(status_effect)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" is now {status_effect.name} from {source_str}")

        if item_effect.effect_type == EffectType.DmgReflect and damage_dealt > 0:
            damage_to_reflect = int(damage_dealt * item_effect.effect_value)

            org_armor = other_entity.get_dueling().armor
            damage_done = other_entity.get_expertise().damage(damage_to_reflect, other_entity.get_dueling(), percent_reduct=0, ignore_armor=False)
            cur_armor = other_entity.get_dueling().armor

            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" reflected {damage_done}{armor_str} damage back to " + "{0}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            armor_from_effect: int = int(max_reduced_armor * item_effect.effect_value)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = int(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, other_entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" stole {health_steal} HP from " + "{0}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = int(item_effect.effect_value * other_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            other_entity.get_expertise().remove_mana(mana_steal)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" stole {mana_steal} mana from " + "{0}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" healed {healing} HP from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = int(item_effect.effect_value * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" healed {healing} HP from {source_str}")

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {restoration} mana from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = int(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {restoration} mana from {source_str}")

        # TODO: This could be a condition in the effect itself.
        if item is not None and item_effect.effect_type == EffectType.ResurrectOnce and self_entity.get_expertise().hp <= 0:
            self_entity.get_expertise().heal(self_entity.get_expertise().max_hp)

            equipment_dict = self_entity.get_equipment().get_all_equipment_dict()
            for slot, equipped_item in equipment_dict.items():
                if equipped_item is not None and equipped_item.get_key() == item.get_key():
                    self_entity.get_equipment().unequip_item_from_slot(slot)

            item_index = self_entity.get_inventory().search_by_key(item.get_key())
            self_entity.get_inventory().remove_item(item_index, 1)

            return (damage_dealt, f"{item.get_full_name()} prevented " + "{" + f"{self_entity_index}" + "}" + " from dying, restored you to full health, and shattered")

        return (damage_dealt, "")

    def apply_chance_status_effect_from_total_item_effects(self, item_effect_cat: ItemEffectCategory, target: Player | NPC, self_entity: Player | NPC, target_index: int):
        # The reason this is abstracted is because we should only ever apply status effect conditions like this
        # once. If we were to do the aggregate repeatedly for each item that contributes that'd be too powerful,
        # and if we were to do each item separately, then it wouldn't actually be the sum of the probability which
        # is intuitive to the player.

        # TODO: In the future, I may also confer positive status effects using this system, at which point I'll need to
        # add a self_index as well.
        
        result_strs: List[str] = []

        # The first element in the tuple is the percent chance of receiving the effect and the
        # second element is the time it'll last.
        chance_status_effect: Dict[StatusEffectKey, Tuple[float, int]] = {}
        # The first element in the tuple is the percent chance of resisting the effect and the
        # second element is the list of item names that contributed to resisting.
        resist_status_effect: Dict[StatusEffectKey, Tuple[float, List[str]]] = {}

        for item in self_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                item_effects_arr: List[Effect] = self.map_item_effect_cat_to_arr(item_effects, item_effect_cat)

                for item_effect in item_effects_arr:
                    if not item_effect.meets_conditions(self_entity, item):
                        continue

                    if item_effect.effect_type == EffectType.ChanceStatusEffect:
                        se_key: StatusEffectKey | None = item_effect.associated_status_effect
                        if se_key is not None:
                            current_effect_info = chance_status_effect.get(se_key, (0, 0))
                            chance_status_effect[se_key] = (item_effect.effect_value + current_effect_info[0], max(item_effect.effect_time, current_effect_info[1]))
                    elif item_effect.effect_type == EffectType.ResistStatusEffect:
                        se_key: StatusEffectKey | None = item_effect.associated_status_effect
                        if se_key is not None:
                            current_resist_info = resist_status_effect.get(se_key, (0, []))
                            resist_status_effect[se_key] = (item_effect.effect_value + current_resist_info[0], current_resist_info[1] + [item.get_full_name()])

        chance_poisoned, turns_poisoned = chance_status_effect.get(StatusEffectKey.Poisoned, (0, 0))
        if random() < chance_poisoned:
            status_effect = Poisoned(
                turns_remaining=turns_poisoned,
                value=POISONED_PERCENT_HP,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_bleeding, turns_bleeding = chance_status_effect.get(StatusEffectKey.Bleeding, (0, 0))
        if random() < chance_bleeding:
            status_effect = Bleeding(
                turns_remaining=turns_bleeding,
                value=BLEED_PERCENT_HP,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_faltering, turns_faltering = chance_status_effect.get(StatusEffectKey.TurnSkipChance, (0, 0))
        if random() < chance_faltering:
            status_effect = TurnSkipChance(
                turns_remaining=turns_faltering,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_taunted, turns_taunted = chance_status_effect.get(StatusEffectKey.Taunted, (0, 0))
        if random() < chance_taunted:
            status_effect = Taunted(
                turns_remaining=turns_taunted,
                forced_to_attack=self_entity,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_convinced, turns_convinced = chance_status_effect.get(StatusEffectKey.CannotTarget, (0, 0))
        if random() < chance_convinced:
            status_effect = CannotTarget(
                turns_remaining=turns_convinced,
                cant_target=self_entity,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_charmed, turns_charmed = chance_status_effect.get(StatusEffectKey.Charmed, (0, 0))
        if random() < chance_charmed:
            status_effect = Charmed(
                turns_remaining=turns_charmed,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_atrophied, turns_atrophied = chance_status_effect.get(StatusEffectKey.CannotAttack, (0, 0))
        if random() < chance_atrophied:
            status_effect = CannotAttack(
                turns_remaining=turns_atrophied,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_sleeping, turns_sleeping = chance_status_effect.get(StatusEffectKey.Sleeping, (0, 0))
        if random() < chance_sleeping:
            status_effect = Sleeping(
                turns_remaining=turns_sleeping,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        # Decaying is a special case because the amount of the effect varies, so the first
        # element in the tuple represents the percent of decay.
        percent_decaying, turns_decaying = chance_status_effect.get(StatusEffectKey.Decaying, (0, 0))
        if percent_decaying != 0:
            status_effect = Decaying(
                turns_remaining=turns_decaying,
                value=percent_decaying,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_undying, turns_undying = chance_status_effect.get(StatusEffectKey.Undying, (0, 0))
        if random() < chance_undying:
            status_effect = Undying(
                turns_remaining=turns_undying,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        chance_enfeebled, turns_enfeebled = chance_status_effect.get(StatusEffectKey.CannotUseAbilities, (0, 0))
        if random() < chance_enfeebled:
            status_effect = CannotUseAbilities(
                turns_remaining=turns_enfeebled,
                value=1,
                trigger_first_turn=False
            )
            result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index, item_effect_cat, resist_status_effect))

        return result_strs

    def apply_on_turn_start_or_end_effects(self, item: Item | None, item_effect: Effect, entity: Player | NPC, entity_name: str, is_turn_start: bool, source_str: str):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if item is not None and not item_effect.meets_conditions(entity, item):
            return ""

        if item_effect.effect_type == EffectType.CleanseStatusEffects:
            entity.get_dueling().status_effects = []
            return "{0}" + f" has had their status effects removed"

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    int(item_effect.effect_value),
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(attr_mod)
            return f"{entity_name} is now {attr_mod.name} from {source_str}"

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value,
                source_str=f"{source_str}",
                trigger_first_turn=is_turn_start
            )
            self.status_effects.append(status_effect)
            return f"{entity_name} is now {status_effect.name} from {source_str}"

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value,
                    source_str=f"{source_str}",
                    trigger_first_turn=is_turn_start
                )
            self.status_effects.append(status_effect)
            return f"{entity_name} is now {status_effect.name} from {source_str}"

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = int(item_effect.effect_value)

            decaying_adjustment: float = 0
            for se in entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            entity.get_expertise().heal(healing)
            return f"{entity_name} healed {healing} HP from {source_str}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            entity.get_expertise().heal(healing)
            return f"{entity_name} healed {healing} HP from {source_str}"

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            entity.get_expertise().restore_mana(restoration)
            return f"{entity_name} restored {restoration} mana from {source_str}"
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = ceil(item_effect.effect_value * entity.get_expertise().max_mana)
            entity.get_expertise().restore_mana(restoration)
            return f"{entity_name} restored {restoration} mana from {source_str}"

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level)
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - entity.get_dueling().armor))
            entity.get_dueling().armor += to_restore
            return f" {entity_name} restored {to_restore} Armor using {source_str}"

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level)
            armor_from_effect: int = ceil(max_reduced_armor * item_effect.effect_value)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - entity.get_dueling().armor))
            entity.get_dueling().armor += to_restore
            return f"{entity_name} restored {to_restore} Armor using {source_str}"

        return ""

    def apply_consumable_item_effect(self, item: Item, item_effect: Effect, self_entity: Player | NPC, target_entity: Player | NPC):
        if not item_effect.meets_conditions(self_entity, item):
            return ""

        potion_effect_mod: float = 1.0
        if ClassTag.Consumable.Potion in item.get_class_tags():
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.PotionBuff:
                    potion_effect_mod += se.value

        if item_effect.effect_type == EffectType.CleanseStatusEffects:
            target_entity.get_dueling().status_effects = []
            return "{1}" + f" has had their status effects removed"

        if item_effect.effect_type == EffectType.ConMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = ConBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = ConDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.StrMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = StrBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = StrDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DexMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = DexBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = DexDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.IntMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = IntBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = IntDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.LckMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = LckBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = LckDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.MemMod:
            attr_mod = None
            if item_effect.effect_value >= 0:
                attr_mod = MemBuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                attr_mod = MemDebuff(
                    item_effect.effect_time,
                    ceil(item_effect.effect_value * potion_effect_mod),
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(attr_mod)
            return "{1}" + f" is now {attr_mod.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgResist:
            status_effect = DmgReduction(
                item_effect.effect_time,
                item_effect.effect_value * potion_effect_mod,
                source_str=f"{item.get_full_name()}",
                trigger_first_turn=False
            )
            self.status_effects.append(status_effect)
            return "{1}" + f" is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.DmgBuff:
            status_effect = None
            if item_effect.effect_value >= 0:
                status_effect = DmgBuff(
                    item_effect.effect_time,
                    item_effect.effect_value * potion_effect_mod,
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            else:
                status_effect = DmgDebuff(
                    item_effect.effect_time,
                    item_effect.effect_value * potion_effect_mod,
                    source_str=f"{item.get_full_name()}",
                    trigger_first_turn=False
                )
            self.status_effects.append(status_effect)
            return "{1}" + f" is now {status_effect.name} from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            to_restore = min(ceil(item_effect.effect_value * potion_effect_mod), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return "{1}" + f" restored {to_restore} Armor using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level)
            armor_from_effect: int = ceil(max_reduced_armor * item_effect.effect_value * potion_effect_mod)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return "{1}" + f" restored {to_restore} Armor using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = ceil(item_effect.effect_value * potion_effect_mod * target_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            target_entity.get_expertise().damage(health_steal, target_entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            return "{0}" + f" stole {health_steal} HP from " + "{1}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = ceil(item_effect.effect_value * potion_effect_mod * target_entity.get_expertise().mana)
            self_entity.get_expertise().restore_mana(mana_steal)
            target_entity.get_expertise().remove_mana(mana_steal)
            return "{0}" + f" stole {mana_steal} mana from " + "{1}" + f" using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreHealth:
            healing = ceil(item_effect.effect_value * potion_effect_mod)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return "{1}" + f" healed {healing} HP from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * potion_effect_mod * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += int(healing * decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return "{1}" + f" healed {healing} HP from {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = ceil(item_effect.effect_value * potion_effect_mod)
            self_entity.get_expertise().restore_mana(restoration)
            return "{1}" + f" restored {restoration} mana from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = ceil(item_effect.effect_value * potion_effect_mod * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return "{1}" + f" restored {restoration} mana from {item.get_full_name()}"

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
            view.set_targets_remaining_based_on_weapon()
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
        cur_turn_user: discord.User | None = view.get_user_for_current_turn()
        if cur_turn_user is None or interaction.user == cur_turn_user:
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

    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, users: List[discord.User], allies: List[Player | NPC], enemies: List[Player | NPC], skip_init_updates: bool=False, companion_battle:bool=False):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._allies: List[Player | NPC] = allies
        self._enemies: List[Player | NPC] = enemies
        self._turn_order: List[Player | NPC] = sorted(allies + enemies, key=lambda x: x.get_combined_attributes().dexterity, reverse=True)
        self._turn_index: int = 0

        self._companion_battle: bool = companion_battle

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
        self._selecting_targets: bool = False # For next/prev buttons
        self._npc_initial_embed: Embed | None = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._additional_info_string_data = ""

        if not skip_init_updates:
            for entity in allies + enemies:
                entity.get_dueling().is_in_combat = True
                entity.get_dueling().armor = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level)
                # Make sure stats are correct.
                entity.get_expertise().update_stats(entity.get_combined_attributes())

            cur_entity: (Player | NPC) = self._turn_order[self._turn_index]
            if isinstance(cur_entity, Player):
                companions = cur_entity.get_companions()
                if companions.current_companion is not None:
                    companion_ability = companions.companions[companions.current_companion].get_dueling_ability(effect_category=None)
                    
                    if isinstance(companion_ability, Ability):
                        cur_entity.get_dueling().abilities.append(companion_ability)
                
            if isinstance(cur_entity, Player) or self._companion_battle:
                self.show_actions()
            else:
                self._npc_initial_embed = self.take_npc_turn()

    def get_user_from_player(self, player: Player | NPC):
        for user in self._users:
            if str(user.id) == player.get_id():
                return user
        return None

    def get_user_for_current_turn(self):
        cur_turn_entity = self._turn_order[self._turn_index]
        if isinstance(cur_turn_entity, Player) or self._companion_battle:
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

    def get_entities_by_ids(self, ids: List[str]):
        entities: List[Player | NPC] = []
        for entity_id in ids:
            for entity in self._turn_order:
                if entity.get_id() == entity_id:
                    entities.append(entity)
        return entities

    def get_initial_embed(self):
        if self._npc_initial_embed is not None:
            return self._npc_initial_embed
        else:
            return self.show_actions()

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
        
        self._additional_info_string_data = ""

        for result_str in item_status_effects:
            formatted_str = result_str.format(self.get_name(previous_entity))
            self._additional_info_string_data += formatted_str + "\n"
        
        for item in previous_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_end:
                result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, previous_entity, self.get_name(previous_entity), is_turn_start=False, source_str=item.get_full_name())
                if result_str != "":
                    self._additional_info_string_data += result_str

        if isinstance(previous_entity, Player):
            companions = previous_entity.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                current_companion = companions.companions[companion_key]
                companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnTurnEnd)
                if isinstance(companion_effect, Effect):
                    result_str = previous_entity.get_dueling().apply_on_turn_start_or_end_effects(None, companion_effect, previous_entity, self.get_name(previous_entity), is_turn_start=False, source_str=current_companion.get_icon_and_name())
                    if result_str != "":
                        self._additional_info_string_data += result_str

        self._turn_index = (self._turn_index + 1) % len(self._turn_order)
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        entity: Player | NPC = self._turn_order[self._turn_index]

        item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnStart, entity, entity, 0)
        
        for result_str in item_status_effects:
            formatted_str = result_str.format(self.get_name(previous_entity))
            self._additional_info_string_data += formatted_str + "\n"

        for item in entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_start:
                result_str = entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, entity, self.get_name(entity), is_turn_start=True, source_str=item.get_full_name())
                if result_str != "":
                    self._additional_info_string_data += result_str
        
        if isinstance(entity, Player):
            companions = entity.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                current_companion = companions.companions[companion_key]
                companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnTurnStart)
                if isinstance(companion_effect, Effect):
                    result_str = entity.get_dueling().apply_on_turn_start_or_end_effects(None, companion_effect, entity, self.get_name(entity), is_turn_start=True, source_str=current_companion.get_icon_and_name())
                    if result_str != "":
                        self._additional_info_string_data += result_str
        
        start_damage: int = 0
        start_heals: int = 0
        max_should_skip_chance: float = 0
        heals_from_poison: bool = any(se.key == StatusEffectKey.PoisonHeals for se in entity.get_dueling().status_effects)
        max_sleeping_chance: float = 0
    
        for se in entity.get_dueling().status_effects:
            if se.turns_remaining > 0 or se.turns_remaining == -1:
                if se.key == StatusEffectKey.FixedDmgTick:
                    start_damage += int(se.value)
                if se.key == StatusEffectKey.Bleeding:
                    start_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.Poisoned:
                    if heals_from_poison:
                        start_heals += ceil(entity.get_expertise().max_hp * se.value)
                    else:
                        start_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.RegenerateHP:
                    start_heals += ceil(entity.get_expertise().max_hp * se.value)
                # Only take the largest chance to skip the turn
                if se.key == StatusEffectKey.TurnSkipChance:
                    max_should_skip_chance = max(se.value, max_should_skip_chance)
                if se.key == StatusEffectKey.Sleeping:
                    max_sleeping_chance = max(se.value, max_sleeping_chance)
            
        # Fixed damage is taken directly, no reduction
        entity.get_expertise().damage(start_damage, entity.get_dueling(), percent_reduct=0, ignore_armor=True)
        if start_damage > 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_damage} damage! "

        entity.get_expertise().heal(start_heals)
        if start_heals > 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} had {start_heals} health restored! "

        if random() < max_should_skip_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)}'s turn was skipped!"
            for se in entity.get_dueling().status_effects:
                # This is a special case to make sure that Faltering doesn't always skip the entity; if it triggers,
                # then it has to be decremented to avoid potentially skipping their turn forever
                if se.key == StatusEffectKey.TurnSkipChance:
                    se.decrement_turns_remaining()

        if random() < max_sleeping_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} is Sleeping and their turn was skipped!"
            for se in entity.get_dueling().status_effects:
                # This is a special case to make sure that Faltering doesn't always skip the entity; if it triggers,
                # then it has to be decremented to avoid potentially skipping their turn forever
                if se.key == StatusEffectKey.Sleeping:
                    se.decrement_turns_remaining()

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
        info_str = "᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n"
        for i, entity in enumerate(self._turn_order):
            group_icon = ":handshake:" if self._is_ally(entity) else ":imp:"

            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level)
            armor_str: str = f"\n{entity.get_dueling().get_armor_string(max_reduced_armor)}" if max_reduced_armor > 0 else ""

            info_str += f"({i + 1}) **{self.get_name(entity)}** {group_icon} (Lvl. {entity.get_expertise().level})\n\n{entity.get_expertise().get_health_and_mana_string()}{armor_str}"
            if len(entity.get_dueling().status_effects) > 0:
                statuses_str = entity.get_dueling().get_statuses_string()
                if statuses_str != "":
                    info_str += f"\n\n{statuses_str}"
            info_str += "\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n"

        player_name = self.get_user_for_current_turn().display_name

        additional_info_str = f"\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{self._additional_info_string_data}" if self._additional_info_string_data != "" else ""
        return info_str + f"\n*It's {player_name}'s turn!*{additional_info_str}"

    def get_selected_entity_full_duel_info_str(self):
        if self._current_target is None:
            return ""

        name = self.get_name(self._current_target)
        expertise = self._current_target.get_expertise()
        dueling = self._current_target.get_dueling()
        equipment = self._current_target.get_equipment()

        max_reduced_armor: int = equipment.get_total_reduced_armor(expertise.level)
        armor_str = f"\n{dueling.get_armor_string(max_reduced_armor)}" if max_reduced_armor > 0 else ""

        duel_string = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n({self._current_target_index + 1}) **{name}**\n\n{expertise.get_health_and_mana_string()}{armor_str}"
        if len(dueling.status_effects) > 0:
            duel_string += f"\n\n{dueling.get_statuses_string()}"

        return f"{duel_string}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"

    def _remove_companion_ability(self, entity: Player | NPC):
        if isinstance(entity, Player):
            companions = entity.get_companions()
            if companions.current_companion is not None:
                companion_ability = companions.companions[companions.current_companion].get_dueling_ability(effect_category=None)
                
                if isinstance(companion_ability, Ability):
                    try:
                        entity.get_dueling().abilities.remove(companion_ability)
                    except:
                        pass

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
                
                if not self._companion_battle:
                    entity.get_stats().dueling.duels_fought += 1
                    entity.get_stats().dueling.duels_tied += 1
                else:
                    entity.get_stats().companions.companion_battles_fought += 1
                    entity.get_stats().companions.companion_battles_tied += 1

                entity.get_expertise().level_up_check()

            return Embed(
                title="Victory for Both and Neither",
                description="A hard-fought battle resulting in a tie. Neither side emerges truly victorious and yet both have defeated their enemies."
            )
        
        losers = self._allies if duel_result.winners == self._enemies else self._enemies

        if self._companion_battle:
            winner_owner_players: List[Player] = [self._database[str(self._guild_id)].get("members", {}).get(npc.get_id(), None) for npc in duel_result.winners]
            winner_str: str = ""
            for player in winner_owner_players:
                player.get_dueling().is_in_combat = False
                companion_key = player.get_companions().current_companion
                if companion_key is not None:
                    current_companion = player.get_companions().companions[companion_key]

                    xp_gained: int = ceil(0.5 * current_companion.pet_battle_xp_gain)
                    current_companion.add_xp(xp_gained)

                    current_companion.add_companion_points(COMPANION_BATTLE_POINTS)

                    winner_str += f"{current_companion.get_icon_and_name()} *(+{xp_gained} xp)*\n"

                    player.get_stats().companions.companion_battles_fought += 1
                    player.get_stats().companions.companion_battles_won += 1

            loser_owner_players: List[Player] = [self._database[str(self._guild_id)].get("members", {}).get(npc.get_id(), None) for npc in losers]
            loser_str: str = ""
            for player in loser_owner_players:
                player.get_dueling().is_in_combat = False

                companion_key = player.get_companions().current_companion
                if companion_key is not None:
                    current_companion = player.get_companions().companions[companion_key]
                    
                    xp_gained: int = ceil(0.5 * current_companion.pet_battle_xp_gain)
                    current_companion.add_xp(xp_gained)

                    current_companion.add_companion_points(COMPANION_BATTLE_POINTS)

                    loser_str += f"{current_companion.get_icon_and_name()} *(+{xp_gained} xp)*\n"

                    player.get_stats().companions.companion_battles_fought += 1

            result_str: str = f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}"
            return Embed(title="Companion Battle Complete", description=f"Your bonds have grown stronger and your companions have gained experience.\n\n{result_str}")

        for winner in duel_result.winners:
            winner.get_stats().dueling.duels_fought += 1
            winner.get_stats().dueling.duels_won += 1
        for loser in losers:
            loser.get_stats().dueling.duels_fought += 1

        for entity in self._turn_order:
            self._remove_companion_ability(entity)

        if all(isinstance(entity, Player) for entity in self._turn_order):
            # This should only happen in a PvP duel
            winner_str = ""
            winner_xp = ceil(0.75 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
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
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (4 * len(losers)))
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
        elif all(isinstance(entity, NPC) for entity in self._enemies):
            winner_str = ""
            winner_xp = ceil(0.25 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                if isinstance(winner, Player):
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())

                    winner_expertise.level_up_check()

                    winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"
                else:
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())
                    winner_expertise.hp = winner_expertise.max_hp
                    winner_expertise.mana = winner_expertise.max_mana

            for loser in losers:
                if isinstance(loser, Player):
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())
                else:
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())
                    loser_expertise.hp = loser_expertise.max_hp
                    loser_expertise.mana = loser_expertise.max_mana
            
            if losers == self._enemies:
                winner_str += "\n"
                player_winners = list(filter(lambda x: isinstance(x, Player), duel_result.winners))
                for loser in losers:
                    assert(isinstance(loser, NPC))
                    for reward_key, probability in loser.get_dueling_rewards().items():
                        if random() < probability:
                            new_item = LOADED_ITEMS.get_new_item(reward_key)
                            item_winner = choice(player_winners)
                            item_winner.get_inventory().add_item(new_item)
                            winner_str += f"{self.get_name(item_winner)} received {new_item.get_full_name_and_count()}\n"

            if winner_str != "":
                return Embed(title="Duel Finished", description=f"You are victorious:\n\n{winner_str}")
            else:
                return Embed(title="Duel Finished", description=f"You have been vanquished!")
        else: # In a completely mixed duel
            winner_str = ""
            winner_xp = ceil(0.25 * sum(loser.get_expertise().level for loser in losers) / len(duel_result.winners))
            for winner in duel_result.winners:
                if isinstance(winner, Player):
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    final_winner_xp = winner_expertise.add_xp_to_class(winner_xp, ExpertiseClass.Guardian, winner.get_equipment())
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())

                    winner_expertise.level_up_check()

                    winner_str += f"{self.get_name(winner)} *(+{final_winner_xp} Guardian xp)*\n"
                else:
                    winner_expertise = winner.get_expertise()
                    winner_dueling = winner.get_dueling()
                    
                    winner_dueling.reset_ability_cds()
                    winner_dueling.status_effects = []
                    winner_dueling.is_in_combat = False

                    winner_expertise.update_stats(winner.get_combined_attributes())
                    winner_expertise.hp = winner_expertise.max_hp
                    winner_expertise.mana = winner_expertise.max_mana

            loser_str = ""
            loser_xp = ceil(sum(winner.get_expertise().level for winner in duel_result.winners) / (4 * len(losers)))
            for loser in losers:
                if isinstance(loser, Player):
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    final_loser_xp = loser_expertise.add_xp_to_class(loser_xp, ExpertiseClass.Guardian, loser.get_equipment())

                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())

                    loser_expertise.level_up_check()

                    loser_str += f"{self.get_name(loser)} *(+{final_loser_xp} Guardian xp)*\n"
                else:
                    loser_expertise = loser.get_expertise()
                    loser_dueling = loser.get_dueling()
                    
                    loser_dueling.reset_ability_cds()
                    loser_dueling.status_effects = []
                    loser_dueling.is_in_combat = False

                    loser_expertise.update_stats(loser.get_combined_attributes())
                    loser_expertise.hp = loser_expertise.max_hp
                    loser_expertise.mana = loser_expertise.max_mana

                    loser_expertise.level_up_check()

            return Embed(title="Duel Finished", description=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}")

    def show_actions(self):
        self.clear_items()

        entity: Player | NPC = self._turn_order[self._turn_index]
        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in entity.get_dueling().status_effects)
        cannot_attack: bool = any(se.key == StatusEffectKey.CannotAttack for se in entity.get_dueling().status_effects)
        cannot_use_abilities: bool = any(se.key == StatusEffectKey.CannotUseAbilities for se in entity.get_dueling().status_effects)

        if not restricted_to_items:
            if not cannot_attack:
                self.add_item(AttackActionButton())
            if not cannot_use_abilities:
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

        charmed: bool = any(se.key == StatusEffectKey.Charmed for se in cur_turn_entity.get_dueling().status_effects)
            
        if (cur_turn_entity in self._enemies and target_own_group) or (cur_turn_entity in self._allies and not target_own_group):
            targets = self._enemies if not charmed else self._allies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        elif (cur_turn_entity in self._enemies and not target_own_group) or (cur_turn_entity in self._allies and target_own_group):
            targets = self._allies if not charmed else self._enemies
            target_str = "target" if self._targets_remaining == 1 else "targets"
            ally_or_op_str = "ally" if target_own_group else "opponent"
            description += f"{selected_targets_str}Choose an {ally_or_op_str}. {self._targets_remaining} {target_str} remaining."
        
        for se in cur_turn_entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.CannotTarget:
                assert(isinstance(se, CannotTarget))
                if se.cant_target in targets:
                    targets.remove(se.cant_target)

        all_targets = targets[self._page * self._NUM_PER_PAGE:min(len(targets), (self._page + 1) * self._NUM_PER_PAGE)]
        filtered_targets = list(filter(lambda target: target.get_expertise().hp > 0, all_targets)) if not self._target_own_group else all_targets
        page_slots = sorted(filtered_targets, key=lambda target: self.get_turn_index(target))
        for i, target in enumerate(page_slots):
            turn_number: int = self.get_turn_index(target)
            self.add_item(TargetButton(f"({turn_number + 1}) {self.get_name(target)}", target, turn_number, i))

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
        bonus_damage: int = 0
        bonus_percent_damage: float = 1
        for se in attacker.get_dueling().status_effects:
            if se.key == StatusEffectKey.Generating:
                generating_value = se.value
            elif se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
            elif se.key == StatusEffectKey.BonusDamageOnAttack:
                bonus_damage += int(se.value)
            elif se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value
        cursed_coins_damage = 0

        main_hand_item = attacker_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        # Base possible damage is [1, 2], basically fist fighting
        unarmed_strength_bonus = int(attacker_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        splash_dmg = 0
        splash_percent_dmg = 0
        for item in attacker_equipment.get_all_equipped_items():
            other_item_effects = item.get_item_effects()
            if other_item_effects is not None:
                for item_effect in other_item_effects.permanent:
                    if item_effect.effect_type == EffectType.SplashDmg:
                        splash_dmg += int(item_effect.effect_value)
                    if item_effect.effect_type == EffectType.SplashPercentMaxDmg:
                        splash_percent_dmg += ceil(weapon_stats.get_max_damage() * item_effect.effect_value)

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
                other_item_effects = item.get_item_effects()
                if other_item_effects is not None:
                    for item_effect in other_item_effects.permanent:
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
            base_damage = weapon_stats.get_random_damage(attacker_attrs, item_effects, max(0, level_req - attacker.get_expertise().level))

            stacking_damage: float = 1
            if main_hand_item is not None:
                for se in target_dueling.status_effects:
                    if se.key == StatusEffectKey.StackingDamage:
                        assert(isinstance(se, StackingDamage))
                        if se.caster == attacker and se.source_str == main_hand_item.get_full_name():
                            stacking_damage += se.value
                    if se.key == StatusEffectKey.AttackingChanceToApplyStatus:
                        assert(isinstance(se, AttackingChanceToApplyStatus))
                        if random() < se.value:
                            se_apply_str: str = target.get_dueling().add_status_effect_with_resist(se.status_effect, target, 0).format(target_name)
                            result_strs.append(se_apply_str)

            damage = ceil(base_damage * stacking_damage)
            damage += min(ceil(base_damage * STR_DMG_SCALE * max(attacker_attrs.strength, 0)), base_damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage)
            damage += bonus_damage

            # Doing these after damage computation because the player doesn't get an indication the effect occurred
            # until the Continue screen, so it feels slightly more natural to have them not affect damage dealt. I
            # may reverse this decision later.
            result_strs += [s.format(target_name) for s in attacker.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, attacker, 0)]

            for item in attacker_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_successful_attack:
                    damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, attacker, target, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            if isinstance(attacker, Player):
                companions = attacker.get_companions()
                companion_key = companions.current_companion
                if companion_key is not None:
                    current_companion = companions.companions[companion_key]
                    companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnSuccessfulAttack)
                    if isinstance(companion_effect, Effect):
                        damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(None, companion_effect, attacker, target, 1, damage, current_companion.get_icon_and_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

            result_strs += [s.format(attacker_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAttacked, attacker, target, 0)]

            for item in target_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_attacked:
                    damage, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            if isinstance(attacker, Player):
                companions = attacker.get_companions()
                companion_key = companions.current_companion
                if companion_key is not None:
                    current_companion = companions.companions[companion_key]
                    companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnAttacked)
                    if isinstance(companion_effect, Effect):
                        damage, result_str = attacker.get_dueling().apply_on_attacked_or_damaged_effects(None, companion_effect, target, attacker, 1, damage, current_companion.get_icon_and_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)

            if actual_damage_dealt > 0:
                result_strs += [s.format(attacker_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, attacker, target, 0)]
                for item in target_equipment.get_all_equipped_items():
                    other_item_effects = item.get_item_effects()
                    if other_item_effects is None:
                        continue
                    for item_effect in other_item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, actual_damage_dealt, item.get_full_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

                if isinstance(attacker, Player):
                    companions = attacker.get_companions()
                    companion_key = companions.current_companion
                    if companion_key is not None:
                        current_companion = companions.companions[companion_key]
                        companion_effect = current_companion.get_dueling_ability(effect_category=ItemEffectCategory.OnDamaged)
                        if isinstance(companion_effect, Effect):
                            damage, result_str = attacker.get_dueling().apply_on_attacked_or_damaged_effects(None, companion_effect, target, attacker, 1, damage, current_companion.get_icon_and_name())
                            if result_str != "":
                                result_strs.append(result_str.format(attacker_name, target_name))

            attacker.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target != attacker), se.on_being_hit_buffs))
                    result_strs.append(f"{target_name} gained {se.get_buffs_str()}")

                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                attacker_dmg_reduct = attacker.get_dueling().get_total_percent_dmg_reduct()

                attacker_org_armor = attacker.get_dueling().armor
                actual_reflected_damage = attacker.get_expertise().damage(reflected_damage, attacker.get_dueling(), attacker_dmg_reduct, ignore_armor=False)
                attacker_cur_armor = attacker.get_dueling().armor
                
                attacker_dmg_reduct_str = f" ({attacker_dmg_reduct * 100}% Reduction)" if attacker_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({attacker_cur_armor - attacker_org_armor} Armor)" if attacker_cur_armor - attacker_org_armor < 0 else ""

                result_strs.append(f"{target_name} reflected {actual_reflected_damage}{reflect_armor_str}{attacker_dmg_reduct_str} back to {attacker_name}")

            target.get_expertise().update_stats(target.get_combined_attributes())

            generating_string = ""
            if generating_value != 0:
                attacker.get_inventory().add_coins(int(generating_value))
                generating_string = f" and gained {generating_value} coins"

                if tarnished_value != 0:
                    cursed_coins_damage += ceil(tarnished_value * generating_value)
            
            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({target_dueling.armor - org_armor} Armor)" if target_dueling.armor - org_armor < 0 else ""

            result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}{generating_string}")
        
            attacker.get_stats().dueling.attacks_done += 1
        
        if cursed_coins_damage != 0:
            if attacker in self._enemies:
                for other in self._allies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct()
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")
            elif attacker in self._allies:
                for other in self._enemies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct()
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")

        if splash_dmg > 0 or splash_percent_dmg > 0:
            if attacker in self._enemies:
                for target in self._allies:
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt} splash damage to {self.get_name(target)}")
            else:
                for target in self._enemies:
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt} splash damage to {self.get_name(target)}")

        return "\n".join(result_strs)

    def use_ability_on_selected_targets(self):
        assert(self._selected_ability is not None)

        caster = self._turn_order[self._turn_index]
        names = [self.get_name(caster), *list(map(lambda x: self.get_name(x), self._selected_targets))]
        result_str = self._selected_ability.use_ability(caster, self._selected_targets)

        self._selected_ability.set_turn_after_lapsed(False)

        caster.get_stats().dueling.abilities_used += 1
        xp_str: str = ""
        if isinstance(caster, Player):
            xp_to_add: int = ceil(self._selected_ability.get_level_requirement() / 4)
            class_key: ExpertiseClass = self._selected_ability.get_class_key()
            final_xp = caster.get_expertise().add_xp_to_class(xp_to_add, class_key, caster.get_equipment())
            xp_str = f"\n\n*You gained {final_xp} {class_key} xp!*"

        # TODO: In special case for companion battles, handle incrementing companion ability
        # use stats and XP gain

        return result_str.format(*names) + xp_str

    def use_item_on_selected_targets(self):
        assert(self._selected_item is not None)

        applicator = self._turn_order[self._turn_index]
        applicator_dueling = applicator.get_dueling()
        applicator_name = self.get_name(applicator)

        result_strs = []
        for target in self._selected_targets:
            result_strs += [s.format(applicator_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.Permanent, applicator, target, 0)]
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
        if self._targets_remaining <= 0 or is_finished:
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
                description = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
        if self._intent == Intent.Ability:
            description = f"{player.get_expertise().get_health_and_mana_string()}\nCoins: {player.get_inventory().get_coins_str()}\n\n"
            if self._selected_ability is not None:
                description += f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_ability}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
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
            
            charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    if not charmed:
                        self._selected_targets = self._enemies
                    else:
                        self._selected_targets = self._allies
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    if not charmed:
                        self._selected_targets = self._allies
                    else:
                        self._selected_targets = self._enemies
                return self.do_action_on_selected_targets()

            if self._targets_remaining == -2:
                self._selected_targets = self._turn_order
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
            
            charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)
            
            if self._targets_remaining == -1:
                if (entity in self._enemies and target_own_group) or (entity in self._allies and not target_own_group):
                    if not charmed:
                        self._selected_targets = self._enemies
                    else:
                        self._selected_targets = self._allies
                elif (entity in self._enemies and not target_own_group) or (entity in self._allies and target_own_group):
                    if not charmed:
                        self._selected_targets = self._allies
                    else:
                        self._selected_targets = self._enemies

            if self._targets_remaining == -2:
                self._selected_targets = self._turn_order
                return self.do_action_on_selected_targets()

            self._page = 0
            self._selecting_targets = True
            return self.show_targets(target_own_group)
        return self.show_abilities("*Error: That ability couldn't be selected.*")

    def select_target(self, target: Player | NPC, index: int):
        self._current_target_index = index
        self._current_target = target

        return self.show_targets(self._target_own_group)
 
    def set_targets_remaining_based_on_weapon(self):
        cur_entity: Player | NPC = self._turn_order[self._turn_index]
        main_hand_item: Item | None = cur_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        
        if main_hand_item is None:
            self._targets_remaining = 1
        else:
            weapon_stats = main_hand_item.get_weapon_stats()
            if weapon_stats is None:
                self._targets_remaining = 1
            else:
                self._targets_remaining = weapon_stats.get_num_targets()

    def continue_turn(self, skip_turn=False):
        self._page = 0
        cur_entity: Player | NPC = self._turn_order[self._turn_index]

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
        
        next_entity: Player | NPC = self._turn_order[self._turn_index]
        if next_entity != cur_entity:
            next_entity_dueling: Dueling = next_entity.get_dueling()
            next_entity_dueling.actions_remaining = next_entity_dueling.init_actions_remaining
        
        cur_turn_user = self.get_user_for_current_turn()
        if isinstance(next_entity, Player) or (cur_turn_user is not None and next_entity.get_id() == str(cur_turn_user.id)):
            return self.show_actions()
        else:
            return self.take_npc_turn()

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

    def take_npc_turn(self):
        cur_npc: NPC = self._turn_order[self._turn_index]
        npc_dueling: Dueling = cur_npc.get_dueling()
        npc_inventory = cur_npc.get_inventory()

        # Based on the chosen action, the vars below will be used to make the action for real
        optimal_fitness_score: float | None = None
        chosen_action: Intent | None = None

        selected_ability: Ability | None = None
        selected_ability_index: int = -1

        selected_item: Item | None = None
        selected_item_index: int = -1

        selected_targets: List[Player | NPC] = []

        def update_optimal_fitness(fitness_score: float, intent: Intent, ability: Ability | None, ability_index: int, item: Item | None, item_index: int, targets: List[Player | NPC]):
            nonlocal optimal_fitness_score, chosen_action, selected_ability, selected_ability_index, selected_item, selected_item_index, selected_targets

            if optimal_fitness_score is None or fitness_score > optimal_fitness_score:
                optimal_fitness_score = fitness_score
                chosen_action = intent
                
                selected_ability = ability
                selected_ability_index = ability_index

                selected_item = item
                selected_item_index = item_index

                selected_targets = targets

        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in npc_dueling.status_effects)
        cannot_attack: bool = any(se.key == StatusEffectKey.CannotAttack for se in npc_dueling.status_effects)
        taunt_targets: List[Player | NPC] = [se.forced_to_attack for se in npc_dueling.status_effects if isinstance(se, Taunted)]

        cannot_use_abilities: bool = any(se.key == StatusEffectKey.CannotUseAbilities for se in npc_dueling.status_effects) or len(taunt_targets) > 0
        cannot_use_items: bool = len(taunt_targets) > 0

        charmed: bool = any(se.key == StatusEffectKey.Charmed for se in npc_dueling.status_effects)

        enemies = self._allies if (cur_npc in self._enemies and not charmed) else self._enemies

        for se in npc_dueling.status_effects:
            if se.key == StatusEffectKey.CannotTarget:
                assert(isinstance(se, CannotTarget))
                if se.cant_target in enemies:
                    enemies.remove(se.cant_target)

        # Step 1: Try attacking all enemies
        if not restricted_to_items:
            if not cannot_attack:
                self.set_targets_remaining_based_on_weapon()

                if self._targets_remaining == 0:
                    # Who knows, maybe I'll make something that can attack itself.
                    dueling_copy: DuelView = self.create_copy()
                    dueling_copy._selected_targets = [dueling_copy._turn_order[dueling_copy._turn_index]]
                    dueling_copy.attack_selected_targets()

                    copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                    update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, [cur_npc])
                elif self._targets_remaining < 0:
                    dueling_copy: DuelView = self.create_copy()

                    targets = []
                    if self._targets_remaining == -1:
                        targets = self._enemies
                    elif self._targets_remaining == -2:
                        targets = self._turn_order
                    
                    target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                    dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                    dueling_copy.attack_selected_targets()

                    copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)
                    
                    update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, enemies)
                else:
                    if len(taunt_targets) > 0:
                        targets = [choice(taunt_targets)]
                        dueling_copy: DuelView = self.create_copy()
                        target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.attack_selected_targets()

                        copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))
                    elif len(enemies) > 0:
                        combinations = list(itertools.combinations(enemies, self._targets_remaining))
                        for targets in combinations:
                            dueling_copy: DuelView = self.create_copy()
                            target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.attack_selected_targets()

                            copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                            update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))

            if not cannot_use_abilities:
                # Step 2: Try using all abilities
                for i, ability in enumerate(npc_dueling.abilities):
                    if cur_npc.get_expertise().mana < ability.get_mana_cost() or ability.get_cur_cooldown() != 0:
                        continue

                    self._targets_remaining = ability.get_num_targets()

                    if self._targets_remaining < 0:
                        dueling_copy: DuelView = self.create_copy()

                        dueling_copy._selected_ability = dueling_copy._turn_order[dueling_copy._turn_index].get_dueling().abilities[i]
                        dueling_copy._selected_ability_index = i

                        targets = []
                        if self._targets_remaining == -1:
                            target_own_group = dueling_copy._selected_ability.get_target_own_group()
                            if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                                if not charmed:
                                    targets = self._enemies
                                else:
                                    targets = self._allies
                            elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                                if not charmed:
                                    targets = self._allies
                                else:
                                    targets = self._enemies
                        elif self._targets_remaining == -2:
                            targets = self._turn_order
                        target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_ability_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    elif self._targets_remaining == 0:
                        dueling_copy: DuelView = self.create_copy()

                        dueling_copy._selected_ability = dueling_copy._turn_order[dueling_copy._turn_index].get_dueling().abilities[i]
                        dueling_copy._selected_ability_index = i

                        targets = [cur_npc]
                        target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_ability_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                        update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    else:
                        targets = []
                        target_own_group = ability.get_target_own_group()
                        if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                            if not charmed:
                                targets = self._enemies
                            else:
                                targets = self._allies
                        elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                            if not charmed:
                                targets = self._allies
                            else:
                                targets = self._enemies

                        for se in npc_dueling.status_effects:
                            if se.key == StatusEffectKey.CannotTarget:
                                assert(isinstance(se, CannotTarget))
                                if se.cant_target in targets:
                                    targets.remove(se.cant_target)

                        if len(targets) > 0:
                            combinations = list(itertools.combinations(targets, self._targets_remaining))
                            for targets in combinations:
                                dueling_copy: DuelView = self.create_copy()

                                dueling_copy._selected_ability = dueling_copy._turn_order[dueling_copy._turn_index].get_dueling().abilities[i]
                                dueling_copy._selected_ability_index = i

                                target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                                dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                                dueling_copy.use_ability_on_selected_targets()

                                copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                                dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                                dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                                fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                                update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, list(targets))

        if not cannot_use_items:
            # Step 3: Try using all items
            inventory_slots = npc_inventory.get_inventory_slots()
            filtered_indices = npc_inventory.filter_inventory_slots([ClassTag.Consumable.UsableWithinDuels])
            filtered_items = [inventory_slots[i] for i in filtered_indices]
            for i, item in enumerate(filtered_items):
                consumable_stats = item.get_consumable_stats()
                if consumable_stats is None:
                    continue
                
                self._targets_remaining = consumable_stats.get_num_targets()

                if self._targets_remaining < 0:
                    dueling_copy: DuelView = self.create_copy()

                    dueling_copy._selected_item = dueling_copy._turn_order[dueling_copy._turn_index].get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = []
                    if self._targets_remaining == -1:
                        target_own_group = consumable_stats.get_target_own_group()
                        if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                            if not charmed:
                                targets = self._enemies
                            else:
                                targets = self._allies
                        elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                            if not charmed:
                                targets = self._allies
                            else:
                                targets = self._enemies
                    elif self._targets_remaining == -2:
                        targets = self._turn_order
                    target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                    dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                    dueling_copy.use_item_on_selected_targets()

                    copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                    update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                elif self._targets_remaining == 0:
                    dueling_copy: DuelView = self.create_copy()

                    dueling_copy._selected_item = dueling_copy._turn_order[dueling_copy._turn_index].get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = [cur_npc]
                    target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                    dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                    dueling_copy.use_item_on_selected_targets()

                    copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)

                    update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                else:
                    targets = []
                    target_own_group = consumable_stats.get_target_own_group()
                    if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                        if not charmed:
                            targets = self._enemies
                        else:
                            targets = self._allies
                    elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                        if not charmed:
                            targets = self._allies
                        else:
                            targets = self._enemies

                    for se in npc_dueling.status_effects:
                        if se.key == StatusEffectKey.CannotTarget:
                            assert(isinstance(se, CannotTarget))
                            if se.cant_target in targets:
                                targets.remove(se.cant_target)

                    if len(targets) > 0:
                        combinations = list(itertools.combinations(enemies, self._targets_remaining))
                        for targets in combinations:
                            dueling_copy: DuelView = self.create_copy()

                            dueling_copy._selected_item = dueling_copy._turn_order[dueling_copy._turn_index].get_inventory().get_inventory_slots()[i]
                            dueling_copy._selected_item_index = i

                            target_ids: List[str] = list(filter(lambda x: x != "", map(lambda x: x.get_id(), targets)))
                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.use_item_on_selected_targets()

                            copy_cur_npc: NPC = dueling_copy._turn_order[dueling_copy._turn_index] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies)
                            
                            update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, list(targets))

        optimal_result_str: str = ""
        action_str: str = ""
        if chosen_action == Intent.Attack:
            action_str = "attacks!"

            self._selected_targets = selected_targets
            optimal_result_str = self.attack_selected_targets()
        elif chosen_action == Intent.Ability:
            action_str = "uses an ability!"
        
            self._selected_targets = selected_targets
            self._selected_ability = selected_ability
            self._selected_ability_index = selected_ability_index
            optimal_result_str = self.use_ability_on_selected_targets()
        elif chosen_action == Intent.Item:
            action_str = "uses an item!"

            self._selected_targets = selected_targets
            self._selected_item = selected_item
            self._selected_item_index = selected_item_index
            optimal_result_str = self.use_item_on_selected_targets()
        else:
            action_str = "skips their turn!"

        self.clear_items()
        self.add_item(ContinueToNextActionButton())

        additional_info_str = f"{self._additional_info_string_data}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if self._additional_info_string_data != "" else ""
        return Embed(title=f"{cur_npc.get_name()} {action_str}", description=f"{additional_info_str}{optimal_result_str}")

    def create_copy(self):
        copied_allies: List[Player | NPC] = jsonpickle.decode(jsonpickle.encode(self._allies, make_refs=False)) # type: ignore
        copied_enemies: List[Player | NPC] = jsonpickle.decode(jsonpickle.encode(self._enemies, make_refs=False)) # type: ignore

        duel_view: DuelView = DuelView(
            self._bot,
            self._database,
            self._guild_id,
            self._users,
            copied_allies,
            copied_enemies,
            skip_init_updates=True
        )

        duel_view._turn_index = self._turn_index

        return duel_view

# -----------------------------------------------------------------------------
# PvP DUEL VIEW AND GUI
# -----------------------------------------------------------------------------

class AcceptButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Accept")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerOrNPCDuelView = self.view

        if interaction.user not in view.get_opponents() and len(view.get_non_npc_opponents()) > 0:
            await interaction.response.edit_message(content="Error: You can't accept this request!", view=view)
            return
        
        response: Embed = view.accept_request(interaction.user)
        if not view.all_accepted():
            await interaction.response.edit_message(embed=response, view=view, content=None)
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel. This duel has been cancelled.")
                return
            
            users: List[discord.User] = [view.get_challenger(), *view.get_non_npc_opponents()]
            challenger_player: Player = view.get_challenger_player()
            opponents_players_and_npcs: List[Player | NPC] = view.get_opponents_players_and_npcs()
            
            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), users, [challenger_player], opponents_players_and_npcs)
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class DeclineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Decline")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: PlayerVsPlayerOrNPCDuelView = self.view

        if interaction.user not in view.get_opponents():
            await interaction.response.edit_message(content="Error: You can't decline this request!", view=view)
            return

        view.clear_items()
        await interaction.response.edit_message(content="The duel was declined.", view=view, embed=None)


class PlayerVsPlayerOrNPCDuelView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, challenger: discord.User, opponents: List[discord.User | NPC]):
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

    def get_non_npc_opponents(self) -> List[discord.User]:
        return list(filter(lambda x: isinstance(x, discord.User), self._opponents))

    def get_info_embed(self):
        not_accepted = list(filter(lambda x: x not in self._acceptances, self.get_non_npc_opponents()))
        not_accepted_names = "\n".join(list(map(lambda x: x.display_name, not_accepted)))
        acceptance_str = f"\n\n**Waiting on acceptances from:**\n\n{not_accepted_names}" if len(not_accepted_names) > 0 else ""

        npc_introduction_strs = []
        for opponent in self._opponents:
            if isinstance(opponent, NPC):
                if opponent.get_name() == "Yenna":
                    npc_introduction_strs.append("Yenna greets you in the dueling grounds, her robe billowing in the wind. \"I hope you've prepared for this moment. I won't be holding back.\"")
                elif opponent.get_name() == "Copperbroad":
                    npc_introduction_strs.append("Copperbroad stands at the ready with his trusty iron pan. \"Ah, aye love me a good rammy! Bring it on.\"")
                elif opponent.get_name() == "Abarra":
                    npc_introduction_strs.append("Abarra arrives at the dueling grounds in rather moderate gear, but a powerful greatsword by his side. \"Hm? Hm.\"")
                elif opponent.get_name() == "Mr. Bones":
                    npc_introduction_strs.append("The air itself seems to dim as shadows gather where Mr. Bones stands in the dueling grounds. The world fills with raspy laughter and a sense of dread as a bony, almost skeletal hand beckons you forth.")
                elif opponent.get_name() == "Viktor":
                    npc_introduction_strs.append("Viktor comes bounding into the dueling grounds, a wild look in his eye. You can't help but wonder what he's got flailing around in his hand. \"A KNIFE!\" he says, confirming your worst fear.")
                elif opponent.get_name() == "Galos":
                    npc_introduction_strs.append("Galos, as usual, is ready and practicing against the training dummy at the dueling grounds. As you approach, he looks towards you and smiles. \"Practice makes perfect. Here for a spar?\"")
        npc_intro_str = ("\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n" + "\n\n".join(npc_introduction_strs) + "\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆") if len(npc_introduction_strs) > 0 else ""

        return Embed(title="PvP Duel", description=(
            "Players will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The duel will begin when all challenged players accept the invitation to duel.{npc_intro_str}{acceptance_str}"
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
        return all(user in self._acceptances for user in self.get_non_npc_opponents())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in [*self.get_non_npc_opponents(), self._challenger])

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

    def get_opponents_players_and_npcs(self):
        return [(self._get_player(opponent.id) if isinstance(opponent, discord.User) else opponent) for opponent in self.get_opponents()]

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
            initial_info: Embed = duel_view.get_initial_embed()

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
            f"The duel will begin when all players have selected a team and at least 1 person is on each team.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 1:**\n\n{team_1_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 2:**\n\n{team_2_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
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

# -----------------------------------------------------------------------------
# COMPANION BATTLE VIEW AND GUI
# -----------------------------------------------------------------------------

class StartCompanionBattleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: CompanionBattleView = self.view

        if interaction.user.id != view.get_duel_starter().id:
            await interaction.response.edit_message(embed=view.get_info_embed(), content="Error: You can't start this companion battle!", view=view)
            return
        
        if not view.all_accepted():
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="All players choose a team before the companion battle can start.")
        elif len(view.get_team_1()) == 0 or len(view.get_team_2()) == 0:
            await interaction.response.edit_message(embed=view.get_info_embed(), view=view, content="At least one player must be on each team.")
        else:
            if view.any_in_duels_currently():
                await interaction.response.edit_message(embed=None, view=None, content="At least one person is already in a duel or companion battle. This duel has been cancelled.")
                return

            view.set_players_in_combat()

            duel_view: DuelView = DuelView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_team_1_players(), view.get_team_2_players(), companion_battle=True)
            initial_info: Embed = duel_view.get_initial_embed()

            await interaction.response.edit_message(embed=initial_info, view=duel_view, content=None)


class CompanionBattleView(discord.ui.View):
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
        self.add_item(StartCompanionBattleButton())

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_info_embed(self):
        team_1_names = "\n".join(list(map(lambda x: x.display_name, self._team_1)))
        team_2_names = "\n".join(list(map(lambda x: x.display_name, self._team_2)))
        return Embed(title="Companion Battle", description=(
            "Companions will enter combat in turn order according to their Dexterity attribute. Each turn, you will choose an action to take: "
            "Attacking using their main hand weapon, using an ability, or using an item.\n\n"
            "The duel ends when all opponents have been reduced to 0 HP. Following the duel, all players will be restored to full HP and mana.\n\n"
            f"The companion battle will begin when all players have selected a team and at least 1 person is on each team.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 1:**\n\n{team_1_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n**Team 2:**\n\n{team_2_names}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
        ))

    def add_to_team_1(self, user: discord.User):
        if self._get_player(user.id).get_dueling().is_in_combat:
            self.clear_items()
            return Embed(
                title="Companion Battle Cancelled",
                description=f"{user.display_name} is in a duel or companion battle and can't accept this one!"
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
                title="Companion Battle Cancelled",
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
        team_1: List[NPC] = []

        for user in self._team_1:
            player = self._get_player(user.id)
            companions = player.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                team_1.append(companions.companions[companion_key].get_pet_battle_entity())
        
        return team_1

    def get_team_2_players(self):
        team_2: List[NPC] = []

        for user in self._team_2:
            player = self._get_player(user.id)
            companions = player.get_companions()
            companion_key = companions.current_companion
            if companion_key is not None:
                team_2.append(companions.companions[companion_key].get_pet_battle_entity())
        
        return team_2
    
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

    def set_players_in_combat(self):
        for user in self._users:
            player = self._get_player(user.id)
            player.get_dueling().is_in_combat = True
