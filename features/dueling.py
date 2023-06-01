from __future__ import annotations

from math import ceil
from random import random

from features.shared.ability import Ability
from features.shared.attributes import Attributes
from features.shared.constants import POISONED_PERCENT_HP, BLEED_PERCENT_HP
from features.shared.effect import Effect, EffectType, ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.statuseffect import *

from typing import Dict, List, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
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

        # Special NPCs are regarded as legendary
        self.is_legendary: bool = False

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
        armor_num_squares = ceil(self.armor / max_reduced_armor * 10) if max_reduced_armor > 0 else 10
        armor_squares_string = ""

        for i in range(1, 11):
            armor_squares_string += "⬜" if i <= armor_num_squares else "⬛"

        return f"Armor: {armor_squares_string} ({self.armor}/{max_reduced_armor})"

    def get_total_percent_dmg_reduct(self, item_effects: ItemEffects):
        total_percent_reduction = 0
        
        for status_effect in self.status_effects:
            if status_effect.key == StatusEffectKey.DmgReduction:
                total_percent_reduction = min(0.75, total_percent_reduction + status_effect.value)
            elif status_effect.key == StatusEffectKey.DmgVulnerability:
                total_percent_reduction = max(-0.5, total_percent_reduction - status_effect.value)

        for effect in item_effects.permanent:
            if effect.effect_type == EffectType.DmgResist:
                total_percent_reduction = min(0.75, total_percent_reduction + effect.effect_value)
        
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

    def add_status_effect_with_resist(self, status_effect: StatusEffect, target: Player | NPC, target_index: int) -> str:
        # The first element in the tuple is the percent chance of resisting the effect and the
        # second element is the list of item names that contributed to resisting.
        resist_status_effect = {}
    
        for item in target.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                # Resistance effects should always be in the permanent category
                for item_effect in item_effects.permanent:
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
        
        self.is_legendary = state.get("is_legendary", False)

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
        if item is not None and (not item_effect.meets_conditions(self_entity, item) or not item.meets_requirements(self_entity.get_expertise().level, self_entity.get_non_status_combined_attributes())):
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
            additional_dmg = ceil(item_effect.effect_value * self_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffSelfRemainingHealth:
            additional_dmg = ceil(item_effect.effect_value * self_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )

        if item_effect.effect_type == EffectType.DmgBuffOtherMaxHealth:
            additional_dmg = ceil(item_effect.effect_value * other_entity.get_expertise().max_hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )
        
        if item_effect.effect_type == EffectType.DmgBuffOtherRemainingHealth:
            additional_dmg = ceil(item_effect.effect_value * other_entity.get_expertise().hp)
            return (
                damage_dealt + additional_dmg,
                f"+{additional_dmg} damage from {source_str}"
            )

        if item_effect.effect_type == EffectType.DmgBuffPoisoned:
            if any(status_effect.key == StatusEffectKey.Poisoned for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = ceil(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage on Poisoned target from {source_str}"
                )

        if item_effect.effect_type == EffectType.DmgBuffBleeding:
            if any(status_effect.key == StatusEffectKey.Bleeding for status_effect in other_entity.get_dueling().status_effects):
                additional_dmg = ceil(damage_dealt * item_effect.effect_value)
                return (
                    damage_dealt + additional_dmg,
                    f"+{additional_dmg} damage on Bleeding target from {source_str}"
                )

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{0}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
            armor_from_effect: int = ceil(max_reduced_armor * item_effect.effect_value)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{0}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = ceil(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, other_entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            return (damage_dealt, "{0}" + f" stole {health_steal} HP from " + "{" + f"{other_entity_index}" + "}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = ceil(item_effect.effect_value * other_entity.get_expertise().mana)
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
                healing += ceil(healing * -decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{0}" + f" healed {healing} HP from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += ceil(healing * -decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{0}" + f" healed {healing} HP from {source_str}")

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{0}" + f" restored {restoration} mana from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = ceil(item_effect.effect_value * self_entity.get_expertise().max_mana)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{0}" + f" restored {restoration} mana from {source_str}")

        return (damage_dealt, "")

    def apply_on_attacked_or_damaged_effects(self, item: Item | None, item_effect: Effect, self_entity: Player | NPC, other_entity: Player | NPC, self_entity_index: int, damage_dealt: int, source_str: str):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if item is not None and (not item_effect.meets_conditions(self_entity, item) or not item.meets_requirements(self_entity.get_expertise().level, self_entity.get_non_status_combined_attributes())):
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
            damage_to_reflect = ceil(damage_dealt * item_effect.effect_value)

            org_armor = other_entity.get_dueling().armor
            damage_done = other_entity.get_expertise().damage(damage_to_reflect, other_entity.get_dueling(), percent_reduct=0, ignore_armor=False)
            cur_armor = other_entity.get_dueling().armor

            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" reflected {damage_done}{armor_str} damage back to " + "{0}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.RestoreArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
            armor_from_effect: int = ceil(max_reduced_armor * item_effect.effect_value)
            to_restore = min(armor_from_effect, max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {to_restore} Armor using {source_str}")

        if item_effect.effect_type == EffectType.HealthSteal:
            health_steal = ceil(item_effect.effect_value * other_entity.get_expertise().hp)
            self_entity.get_expertise().heal(health_steal)
            other_entity.get_expertise().damage(health_steal, other_entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" stole {health_steal} HP from " + "{0}" + f" using {source_str}")

        if item_effect.effect_type == EffectType.ManaSteal:
            mana_steal = ceil(item_effect.effect_value * other_entity.get_expertise().mana)
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
                healing += ceil(healing * -decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" healed {healing} HP from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += ceil(healing * -decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" healed {healing} HP from {source_str}")

        if item_effect.effect_type == EffectType.RestoreMana:
            restoration = int(item_effect.effect_value)
            self_entity.get_expertise().restore_mana(restoration)
            return (damage_dealt, "{" + f"{self_entity_index}" + "}" + f" restored {restoration} mana from {source_str}")
        
        if item_effect.effect_type == EffectType.RestorePercentMana:
            restoration = ceil(item_effect.effect_value * self_entity.get_expertise().max_mana)
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

    def apply_chance_status_effect_from_total_item_effects(self, item_effect_cat: ItemEffectCategory, target: Player | NPC, self_entity: Player | NPC, target_index: int, self_index: int, target_is_ally: bool):
        # The reason this is abstracted is because we should only ever apply status effect conditions like this
        # once. If we were to do the aggregate repeatedly for each item that contributes that'd be too powerful,
        # and if we were to do each item separately, then it wouldn't actually be the sum of the probability which
        # is intuitive to the player.

        # TODO: There's actually no way for abilities to indicate which among the targets is a friend or ally, so
        # it's based off the target_own_group parameter. This fails to correctly indicate that there may be allies
        # in the mix if num_targets = -2. Passing the is_ally function could fix this.
        
        # The first element in the tuple is the percent chance of receiving the effect and the
        # second element is the time it'll last.
        chance_status_effect: Dict[StatusEffectKey, Tuple[float, int]] = {}

        for item in self_entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                item_effects_arr: List[Effect] = self.map_item_effect_cat_to_arr(item_effects, item_effect_cat)

                for item_effect in item_effects_arr:
                    if not item_effect.meets_conditions(self_entity, item) or not item.meets_requirements(self_entity.get_expertise().level, self_entity.get_non_status_combined_attributes()):
                        continue

                    if item_effect.effect_type == EffectType.ChanceStatusEffect:
                        se_key: StatusEffectKey | None = item_effect.associated_status_effect
                        if se_key is not None:
                            current_effect_info = chance_status_effect.get(se_key, (0, 0))
                            chance_status_effect[se_key] = (item_effect.effect_value + current_effect_info[0], max(item_effect.effect_time, current_effect_info[1]))

        return self._apply_status_effect_results([], chance_status_effect, target, self_entity, target_index, self_index, target_is_ally)

    def apply_chance_status_effect_from_item(self, item_effect_cat: ItemEffectCategory, item: Item, target: Player | NPC, self_entity: Player | NPC, target_index: int, self_index: int, target_is_ally: bool):
        # The first element in the tuple is the percent chance of receiving the effect and the
        # second element is the time it'll last.
        chance_status_effect: Dict[StatusEffectKey, Tuple[float, int]] = {}

        item_effects = item.get_item_effects()
        if item_effects is not None:
            item_effects_arr: List[Effect] = self.map_item_effect_cat_to_arr(item_effects, item_effect_cat)

            for item_effect in item_effects_arr:
                if not item_effect.meets_conditions(self_entity, item) or not item.meets_requirements(self_entity.get_expertise().level, self_entity.get_non_status_combined_attributes()):
                    continue

                if item_effect.effect_type == EffectType.ChanceStatusEffect:
                    se_key: StatusEffectKey | None = item_effect.associated_status_effect
                    if se_key is not None:
                        current_effect_info = chance_status_effect.get(se_key, (0, 0))
                        chance_status_effect[se_key] = (item_effect.effect_value + current_effect_info[0], max(item_effect.effect_time, current_effect_info[1]))

        return self._apply_status_effect_results([], chance_status_effect, target, self_entity, target_index, self_index, target_is_ally)

    def _apply_status_effect_results(self, result_strs: List[str], chance_status_effect: Dict[StatusEffectKey, Tuple[float, int]], target: Player | NPC, self_entity: Player | NPC, target_index: int, self_index: int, target_is_ally: bool):
        chance_poisoned, turns_poisoned = chance_status_effect.get(StatusEffectKey.Poisoned, (0, 0))
        if random() < chance_poisoned:
            status_effect = Poisoned(
                turns_remaining=turns_poisoned,
                value=POISONED_PERCENT_HP,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_bleeding, turns_bleeding = chance_status_effect.get(StatusEffectKey.Bleeding, (0, 0))
        if random() < chance_bleeding:
            status_effect = Bleeding(
                turns_remaining=turns_bleeding,
                value=BLEED_PERCENT_HP,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_faltering, turns_faltering = chance_status_effect.get(StatusEffectKey.TurnSkipChance, (0, 0))
        if random() < chance_faltering:
            status_effect = TurnSkipChance(
                turns_remaining=turns_faltering,
                value=1,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_taunted, turns_taunted = chance_status_effect.get(StatusEffectKey.Taunted, (0, 0))
        if random() < chance_taunted:
            status_effect = Taunted(
                turns_remaining=turns_taunted,
                forced_to_attack=self_entity,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_convinced, turns_convinced = chance_status_effect.get(StatusEffectKey.CannotTarget, (0, 0))
        if random() < chance_convinced:
            status_effect = CannotTarget(
                turns_remaining=turns_convinced,
                cant_target=self_entity,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_charmed, turns_charmed = chance_status_effect.get(StatusEffectKey.Charmed, (0, 0))
        if random() < chance_charmed:
            status_effect = Charmed(
                turns_remaining=turns_charmed,
                value=1,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_atrophied, turns_atrophied = chance_status_effect.get(StatusEffectKey.CannotAttack, (0, 0))
        if random() < chance_atrophied:
            status_effect = CannotAttack(
                turns_remaining=turns_atrophied,
                value=1,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_sleeping, turns_sleeping = chance_status_effect.get(StatusEffectKey.Sleeping, (0, 0))
        if random() < chance_sleeping:
            status_effect = Sleeping(
                turns_remaining=turns_sleeping,
                value=1,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        # Decaying is a special case because the amount of the effect varies, so the first
        # element in the tuple represents the percent of decay.
        percent_decaying, turns_decaying = chance_status_effect.get(StatusEffectKey.Decaying, (0, 0))
        if percent_decaying != 0:
            status_effect = Decaying(
                turns_remaining=turns_decaying,
                value=percent_decaying,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        chance_undying, turns_undying = chance_status_effect.get(StatusEffectKey.Undying, (0, 0))
        if random() < chance_undying:
            status_effect = Undying(
                turns_remaining=turns_undying,
                value=1,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        chance_enfeebled, turns_enfeebled = chance_status_effect.get(StatusEffectKey.CannotUseAbilities, (0, 0))
        if random() < chance_enfeebled:
            status_effect = CannotUseAbilities(
                turns_remaining=turns_enfeebled,
                value=1,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        # Special case, similar to Decaying.
        percent_protected, turns_protected = chance_status_effect.get(StatusEffectKey.DmgReduction, (0, 0))
        if percent_protected != 0:
            status_effect = DmgReduction(
                turns_remaining=turns_protected,
                value=percent_protected,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))
        
        # Special case, similar to Decaying.
        percent_vulnerable, turns_vulnerable = chance_status_effect.get(StatusEffectKey.DmgVulnerability, (0, 0))
        if percent_vulnerable != 0:
            status_effect = DmgVulnerability(
                turns_remaining=turns_vulnerable,
                value=percent_vulnerable,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        # Special case, similar to Decaying.
        damage_per_turn, turns_echoing = chance_status_effect.get(StatusEffectKey.FixedDmgTick, (0, 0))
        if damage_per_turn != 0:
            status_effect = FixedDmgTick(
                turns_remaining=turns_echoing,
                value=int(damage_per_turn),
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        # Special case, similar to Decaying.
        coins_generated, turns_generating = chance_status_effect.get(StatusEffectKey.Generating, (0, 0))
        if coins_generated != 0:
            status_effect = Generating(
                turns_remaining=turns_generating,
                value=int(coins_generated),
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))
        
        # Special case, similar to Decaying.
        percent_tarnished, turns_tarnished = chance_status_effect.get(StatusEffectKey.Tarnished, (0, 0))
        if percent_tarnished != 0:
            status_effect = Tarnished(
                turns_remaining=turns_tarnished,
                value=percent_tarnished,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))
        
        chance_sanguinated, turns_sanguinated = chance_status_effect.get(StatusEffectKey.ManaToHP, (0, 0))
        if random() < chance_sanguinated:
            status_effect = ManaToHP(
                turns_remaining=turns_sanguinated,
                value=1,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))
        
        chance_absorbing, turns_absorbing = chance_status_effect.get(StatusEffectKey.PoisonHeals, (0, 0))
        if random() < chance_absorbing:
            status_effect = PoisonHeals(
                turns_remaining=turns_absorbing,
                value=1,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))
        
        # Special case, similar to Decaying.
        percent_empowered, turns_empowered = chance_status_effect.get(StatusEffectKey.DmgBuff, (0, 0))
        if percent_empowered != 0:
            status_effect = DmgBuff(
                turns_remaining=turns_empowered,
                value=percent_empowered,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        # Special case, similar to Decaying.
        percent_diminished, turns_diminished = chance_status_effect.get(StatusEffectKey.DmgDebuff, (0, 0))
        if percent_diminished != 0:
            status_effect = DmgDebuff(
                turns_remaining=turns_diminished,
                value=percent_diminished,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        # Special case, similar to Decaying.
        # TODO: Need to pass the source str into this function and then to the StackingDamage instance.
        percent_reverberating, turns_reverberating = chance_status_effect.get(StatusEffectKey.StackingDamage, (0, 0))
        if percent_reverberating != 0:
            status_effect = StackingDamage(
                turns_remaining=turns_reverberating,
                value=percent_reverberating,
                caster=self_entity,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        con_buff, turns_con_buff = chance_status_effect.get(StatusEffectKey.ConBuff, (0, 0))
        if con_buff != 0:
            status_effect = ConBuff(
                turns_remaining=turns_con_buff,
                value=con_buff,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        con_debuff, turns_con_debuff = chance_status_effect.get(StatusEffectKey.ConDebuff, (0, 0))
        if con_debuff != 0:
            status_effect = ConDebuff(
                turns_remaining=turns_con_debuff,
                value=con_debuff,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        str_buff, turns_str_buff = chance_status_effect.get(StatusEffectKey.StrBuff, (0, 0))
        if str_buff != 0:
            status_effect = StrBuff(
                turns_remaining=turns_str_buff,
                value=str_buff,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        str_debuff, turns_str_debuff = chance_status_effect.get(StatusEffectKey.StrDebuff, (0, 0))
        if str_debuff != 0:
            status_effect = StrDebuff(
                turns_remaining=turns_str_debuff,
                value=str_debuff,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        dex_buff, turns_dex_buff = chance_status_effect.get(StatusEffectKey.DexBuff, (0, 0))
        if dex_buff != 0:
            status_effect = DexBuff(
                turns_remaining=turns_dex_buff,
                value=dex_buff,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        dex_debuff, turns_dex_debuff = chance_status_effect.get(StatusEffectKey.DexDebuff, (0, 0))
        if dex_debuff != 0:
            status_effect = DexDebuff(
                turns_remaining=turns_dex_debuff,
                value=dex_debuff,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        int_buff, turns_int_buff = chance_status_effect.get(StatusEffectKey.IntBuff, (0, 0))
        if int_buff != 0:
            status_effect = IntBuff(
                turns_remaining=turns_int_buff,
                value=int_buff,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        int_debuff, turns_int_debuff = chance_status_effect.get(StatusEffectKey.IntDebuff, (0, 0))
        if int_debuff != 0:
            status_effect = IntDebuff(
                turns_remaining=turns_int_debuff,
                value=int_debuff,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        lck_buff, turns_lck_buff = chance_status_effect.get(StatusEffectKey.LckBuff, (0, 0))
        if lck_buff != 0:
            status_effect = LckBuff(
                turns_remaining=turns_lck_buff,
                value=lck_buff,
                trigger_first_turn=False
            )
            if target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))
            else:
                result_strs.append(self_entity.get_dueling().add_status_effect_with_resist(status_effect, self_entity, self_index))

        lck_debuff, turns_lck_debuff = chance_status_effect.get(StatusEffectKey.LckDebuff, (0, 0))
        if lck_debuff != 0:
            status_effect = LckDebuff(
                turns_remaining=turns_lck_debuff,
                value=lck_debuff,
                trigger_first_turn=False
            )
            if not target_is_ally:
                result_strs.append(target.get_dueling().add_status_effect_with_resist(status_effect, target, target_index))

        return result_strs

    def apply_on_turn_start_or_end_effects(self, item: Item | None, item_effect: Effect, entity: Player | NPC, entity_name: str, is_turn_start: bool, source_str: str):
        # Note: Not all effects are listed here, since not all make sense to trigger
        # in this scenario.
        if item is not None and (not item_effect.meets_conditions(entity, item) or not item.meets_requirements(entity.get_expertise().level, entity.get_non_status_combined_attributes())):
            return ""

        if item_effect.effect_type == EffectType.CleanseStatusEffects:
            entity.get_dueling().status_effects = []
            return f"{entity_name} has had their status effects removed"

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
                healing += ceil(healing * -decaying_adjustment)

            entity.get_expertise().heal(healing)
            return f"{entity_name} healed {healing} HP from {source_str}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += ceil(healing * -decaying_adjustment)

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
            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
            to_restore = min(int(item_effect.effect_value), max(0, max_reduced_armor - entity.get_dueling().armor))
            entity.get_dueling().armor += to_restore
            return f" {entity_name} restored {to_restore} Armor using {source_str}"

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
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
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
            to_restore = min(ceil(item_effect.effect_value * potion_effect_mod), max(0, max_reduced_armor - self_entity.get_dueling().armor))
            self_entity.get_dueling().armor += to_restore
            return "{1}" + f" restored {to_restore} Armor using {item.get_full_name()}"

        if item_effect.effect_type == EffectType.RestorePercentArmor:
            max_reduced_armor: int = self_entity.get_equipment().get_total_reduced_armor(self_entity.get_expertise().level, self_entity.get_expertise().get_all_attributes() + self_entity.get_equipment().get_total_attribute_mods())
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
                healing += ceil(healing * -decaying_adjustment)

            self_entity.get_expertise().heal(healing)
            return "{1}" + f" healed {healing} HP from {item.get_full_name()}"
        
        if item_effect.effect_type == EffectType.RestorePercentHealth:
            healing = ceil(item_effect.effect_value * potion_effect_mod * self_entity.get_expertise().max_hp)

            decaying_adjustment: float = 0
            for se in self_entity.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            if decaying_adjustment != 0:
                healing += ceil(healing * -decaying_adjustment)

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

        if item_effect.effect_type == EffectType.Damage:
            result_strs: List[str] = []

            damage: int = int(item_effect.effect_value)
            target_dueling: Dueling = target_entity.get_dueling()

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct(target_entity.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_entity.get_expertise().damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)

            self_entity.get_stats().dueling.damage_dealt += actual_damage_dealt
            target_entity.get_stats().dueling.damage_taken += actual_damage_dealt
            target_entity.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(self_entity != target_entity), se.on_being_hit_buffs))
                    result_strs.append("{1}" + f" gained {se.get_buffs_str()}")

                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value

            for effect in target_entity.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                attacker_dmg_reduct = self_entity.get_dueling().get_total_percent_dmg_reduct(self_entity.get_combined_req_met_effects())

                attacker_org_armor = self_entity.get_dueling().armor
                actual_reflected_damage = self_entity.get_expertise().damage(reflected_damage, self_entity.get_dueling(), attacker_dmg_reduct, ignore_armor=False)
                attacker_cur_armor = self_entity.get_dueling().armor
                
                attacker_dmg_reduct_str = f" ({abs(attacker_dmg_reduct) * 100}% {'Reduction' if attacker_dmg_reduct > 0 else 'Increase'})" if attacker_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({attacker_cur_armor - attacker_org_armor} Armor)" if attacker_cur_armor - attacker_org_armor < 0 else ""

                result_strs.append("{1}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{attacker_dmg_reduct_str} back to " + "{0}")

            target_entity.get_expertise().update_stats(target_entity.get_combined_attributes())

            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({target_dueling.armor - org_armor} Armor)" if target_dueling.armor - org_armor < 0 else ""

            result_strs.append("{0}" + f" dealt {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str} damage to " + "{1}" + f" from {item.get_full_name()}")

            return "\n".join(result_strs)
        
        return ""
