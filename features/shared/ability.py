from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from math import ceil
from random import randint, random

from features.equipment import Equipment
from features.expertise import Attribute, ExpertiseClass
from features.shared.constants import BLEED_PERCENT_HP, DEX_DMG_SCALE, DEX_DODGE_SCALE, INT_DMG_SCALE, LCK_DMG_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, POISONED_PERCENT_HP, STR_DMG_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.item import ItemKey, WeaponStats
from features.shared.statuseffect import *

from typing import Dict, List, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player

# -----------------------------------------------------------------------------
# BASE CLASS
# -----------------------------------------------------------------------------

# Using a data class instead of a tuple to make the code more readable
@dataclass
class NegativeAbilityResult():
    target_str: str
    dodged: bool


class Ability():
    def __init__(self, icon: str, name: str, class_key: ExpertiseClass, description: str, flavor_text: str, mana_cost: int, cooldown: int, num_targets: int, level_requirement: int, target_own_group: bool, purchase_cost: int, scaling: List[Attribute]):
        # TODO: Handle whether ability status effects stack with a new param
        self._icon = icon
        self._name = name
        self._class_key = class_key
        self._description = description
        self._flavor_text = flavor_text
        # This is here for display even though all logic using it should be
        # in the use_ability method.
        self._mana_cost = mana_cost
        self._cooldown = cooldown
        self._num_targets = num_targets
        self._level_requirement = level_requirement
        self._target_own_group = target_own_group
        self._purchase_cost = purchase_cost
        self._scaling = scaling

        # Turns remaining until it can be used again
        # If this is -1, then it's a once-per-duel ability that's already been used
        self._cur_cooldown = 0
        # For the player, it makes more sense for CDs to be in terms of "turns after you end your current turn"
        # so this accounts for displaying CDs correctly in code and to the player.
        self._turn_after_lapsed = False

    def get_icon_and_name(self):
        return f"{self._icon} {self._name}"

    def get_name(self):
        return self._name

    def get_icon(self):
        return self._icon

    def get_mana_cost(self):
        return self._mana_cost

    def get_num_targets(self):
        return self._num_targets

    def get_level_requirement(self):
        return self._level_requirement

    def get_target_own_group(self):
        return self._target_own_group

    def get_cur_cooldown(self):
        return self._cur_cooldown

    def get_purchase_cost(self):
        return self._purchase_cost

    def get_class_key(self):
        return self._class_key

    def get_scaling(self):
        return self._scaling

    def get_turn_after_lapsed(self):
        return self._turn_after_lapsed
    
    def set_turn_after_lapsed(self, value: bool):
        self._turn_after_lapsed = value

    def reset_cd(self):
        self._cur_cooldown = 0
        self._turn_after_lapsed = True

    def decrement_cd(self):
        if self._turn_after_lapsed and self._cur_cooldown != -1:
            self._cur_cooldown = max(0, self._cur_cooldown - 1)

        if not self._turn_after_lapsed:
            self._turn_after_lapsed = True

    @abstractmethod
    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        pass

    def remove_mana_and_set_cd(self, caster: Player | NPC):
        mana_to_blood_percent = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.ManaToHP:
                mana_to_blood_percent = se.value
                break

        mana_cost_adjustment = 0
        cd_adjustment = 0
        for effect in caster.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.AdjustedManaCosts:
                mana_cost_adjustment = max(mana_cost_adjustment + effect.effect_value, -1)
            if effect.effect_type == EffectType.AdjustedCDs:
                cd_adjustment += int(effect.effect_value)

        if self._cooldown >= 0:
            self._cur_cooldown = max(self._cooldown + cd_adjustment, 0)
        else:
            # Can't adjust -1 time cooldowns
            self._cur_cooldown = self._cooldown

        final_mana_cost = self.get_mana_cost() + int(self.get_mana_cost() * mana_cost_adjustment)
        if mana_to_blood_percent == 0:
            caster.get_expertise().remove_mana(final_mana_cost)
        else:
            damage = int(mana_to_blood_percent * final_mana_cost)
            if damage > 0:
                caster.get_expertise().damage(damage, caster.get_dueling(), percent_reduct=0, ignore_armor=True)
                
                result_str = ""
                for se in caster.get_dueling().status_effects:
                    if se.key == StatusEffectKey.AttrBuffOnDamage:
                        assert(isinstance(se, AttrBuffOnDamage))
                        caster.get_dueling().status_effects += list(map(lambda s: s.set_trigger_first_turn(False), se.on_being_hit_buffs))
                        result_str = "\n{0}" + f" gained {se.get_buffs_str()}"
                caster.get_expertise().update_stats(caster.get_combined_attributes())

                return f"You took {damage} damage to cast this from Contract: Mana to Blood" + result_str

    def _use_damage_ability(self, caster: Player | NPC, targets: List[Player | NPC], dmg_range: range) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for effect in caster.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.PiercingDmg:
                piercing_dmg += int(effect.effect_value)
            elif effect.effect_type == EffectType.PiercingPercentDmg:
                piercing_percent_dmg = min(piercing_percent_dmg + effect.effect_value, 1)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(dmg_range.start, dmg_range.stop)

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            damage = ceil(base_damage * stacking_damage)
            if Attribute.Intelligence in self._scaling:
                damage += min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            if Attribute.Strength in self._scaling:
                damage += min(ceil(base_damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), base_damage)
            if Attribute.Dexterity in self._scaling:
                damage += min(ceil(base_damage * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), base_damage)
            if Attribute.Luck in self._scaling:
                damage += min(ceil(base_damage * LCK_DMG_SCALE * max(caster_attrs.luck, 0)), base_damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)
            
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_taken += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, se_on_damage_str, on_ability_used_against_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(result_str, True))

        return results

    def _use_negative_status_effect_ability(self, caster: Player | NPC, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []

        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            se_on_ability_used_str: str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group))
            on_attack_or_ability_effects_str: str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    _, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effects_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    _, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            mapped_ses = list(map(lambda se: se.set_trigger_first_turn(target != caster), status_effects))
            final_se_strs = []
            for se in mapped_ses:
                final_se_strs.append(target.get_dueling().add_status_effect_with_resist(se, target, i + 1))
            target.get_expertise().update_stats(target.get_combined_attributes())

            non_empty_strs = list(filter(lambda s: s != "", [se_on_ability_used_str, on_attack_or_ability_effects_str, se_ability_used_against_str, on_ability_used_against_str, *final_se_strs]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        return results

    def _use_damage_and_effect_ability(self, caster: Player | NPC, targets: List[Player | NPC], dmg_range: range, status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results = self._use_damage_ability(caster, targets, dmg_range)

        for i in range(len(results)):
            if not results[i].dodged:
                mapped_ses = list(map(lambda se: se.set_trigger_first_turn(targets[i] != caster), status_effects))
                for se in mapped_ses:
                    se_str = targets[i].get_dueling().add_status_effect_with_resist(se, targets[i], i + 1)
                    results[i].target_str += f" and {se_str}"

                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
        
        return results

    def _use_positive_status_effect_ability(self, caster: Player | NPC, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[str]:
        results: List[str] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            se_on_ability_used_str: str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group))
            on_attack_or_ability_effects_str: str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    _, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effects_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    _, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"

            target.get_dueling().status_effects += list(map(lambda se: se.set_trigger_first_turn(target != caster), status_effects))
            target.get_expertise().update_stats(target.get_combined_attributes())

            se_result_str = "{" + f"{i + 1}" + "}" + f" is now {status_effects_str}"
            non_empty_strs = list(filter(lambda s: s != "", [se_result_str, se_on_ability_used_str, on_attack_or_ability_effects_str, se_ability_used_against_str, on_ability_used_against_str]))
            results.append("\n".join(non_empty_strs))
        
        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(result_str)

        return results

    def _use_heal_ability(self, caster: Player | NPC, targets: List[Player | NPC], heal_range: range, max_heal_amount: int | None=None) -> List[str]:
        results: List[str] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        healing_adjustment = 0
        for item in caster.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    if not effect.meets_conditions(caster, item):
                        continue

                    if effect.effect_type == EffectType.HealingAbilityBuff:
                        healing_adjustment += effect.effect_value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()

            decaying_adjustment: float = 0
            for se in caster.get_dueling().status_effects:
                if se.key == StatusEffectKey.Decaying:
                    decaying_adjustment += se.value

            critical_hit_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_buff = min(int(critical_hit_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_buff = max(int(critical_hit_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_buff, 1) if critical_hit_boost > 1 else 1

            base_heal = randint(heal_range.start, heal_range.stop)

            heal_amount = base_heal
            if Attribute.Intelligence in self._scaling:
                heal_amount += min(ceil(base_heal * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_heal)
            if Attribute.Strength in self._scaling:
                heal_amount += min(ceil(base_heal * STR_DMG_SCALE * max(caster_attrs.strength, 0)), base_heal)
            if Attribute.Dexterity in self._scaling:
                heal_amount += min(ceil(base_heal * DEX_DMG_SCALE * max(caster_attrs.dexterity, 0)), base_heal)
            if Attribute.Luck in self._scaling:
                heal_amount += min(ceil(base_heal * LCK_DMG_SCALE * max(caster_attrs.luck, 0)), base_heal)

            heal_amount = ceil(heal_amount * critical_hit_final)
            heal_amount += ceil(heal_amount * healing_adjustment)

            if decaying_adjustment != 0:
                heal_amount *= -decaying_adjustment

            if max_heal_amount is not None:
                heal_amount = min(heal_amount, max_heal_amount)

            se_on_ability_used_str: str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group))
            on_attack_or_ability_effects_str: str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    _, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effects_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    _, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, 0, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"

            target_expertise.heal(int(heal_amount))

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"

            heal_str = "{" + f"{i + 1}" + "}" + f" was healed for {heal_amount}{critical_hit_str} HP"
            non_empty_strs = list(filter(lambda s: s != "", [heal_str, se_on_ability_used_str, on_attack_or_ability_effects_str, se_ability_used_against_str, on_ability_used_against_str]))
            results.append("\n".join(non_empty_strs))
        
        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(result_str)

        return results

    def __str__(self):
        target_str: str = ""
        if self._num_targets == -2:
            target_str = "Targets All"
        if self._num_targets == -1:
            target_str = "Targets All"
        if self._num_targets == 0:
            target_str = "Targets Self"
        if self._num_targets == 1:
            target_str = "1 Target"
        if self._num_targets > 1:
            target_str = f"1-{self._num_targets} Targets"
        
        cooldown_str: str = ""
        if self._cooldown == -1:
            cooldown_str = "Once per Duel"
        if self._cooldown == 0:
            cooldown_str = "No CD"
        if self._cooldown > 0:
            cooldown_str = f"{self._cooldown} Turn CD"

        flavor_text: str = f"*{self._flavor_text}*\n\n" if self._flavor_text != "" else ""

        cur_cooldown_str: str = ""
        if self._cur_cooldown == -1:
            cur_cooldown_str = "\n\n**Already used once this duel**"
        if self._cur_cooldown > 0:
            cur_cooldown_str = f"\n\n**CD Remaining: {self._cur_cooldown}**"

        attr_short_strs = ", ".join(Attribute.get_short_strs(self._scaling))
        scaling_str = f"Scales with {attr_short_strs}\n\n" if len(self._scaling) > 0 else ""

        return (
            f"{self._icon} **{self._name}**\n"
            f"{self._mana_cost} Mana / {target_str} / {cooldown_str}\n\n"
            f"{scaling_str}"
            f"{self._description}\n\n"
            f"{flavor_text}"
            f"*Requires {self._class_key} Level {self._level_requirement}*"
            f"{cur_cooldown_str}"
        )

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._icon = state.get("_icon", "")
        self._name = state.get("_name", "")
        self._class_key = state.get("_class_key", ExpertiseClass.Unknown)
        self._description = state.get("_description", "")
        self._flavor_text = state.get("_flavor_text", "")
        self._mana_cost = state.get("_mana_cost", 0)
        self._cooldown = state.get("_cooldown", 0)
        self._num_targets = state.get("_num_targets", 0)
        self._level_requirement = state.get("_level_requirement", 0)
        self._cur_cooldown = state.get("_cur_cooldown", 0)
        self._target_own_group = state.get("_target_own_group", False)
        self._purchase_cost = state.get("_purchase_cost", 0)
        self._scaling = state.get("_scaling", [])
        self._turn_after_lapsed = state.get("_turn_after_lapsed", False)

# -----------------------------------------------------------------------------
# FISHER ABILITIES
# -----------------------------------------------------------------------------
# SEA SPRAY
# -----------------------------------------------------------------------------

class SeaSprayI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray I",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 2-4 + 25% of your Intelligence damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=2,
            target_own_group=False,
            purchase_cost=50,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        bonus_damage: int = ceil(0.25 * caster.get_expertise().intelligence)
        damage = range(2 + bonus_damage, 4 + bonus_damage)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class SeaSprayII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray II",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 4-7 + 35% of your Intelligence damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4,
            target_own_group=False,
            purchase_cost=100,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        bonus_damage: int = ceil(0.35 * caster.get_expertise().intelligence)
        damage = range(4 + bonus_damage, 7 + bonus_damage)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SeaSprayIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray III",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 6-9 + 45% of your Intelligence damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=6,
            target_own_group=False,
            purchase_cost=200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        bonus_damage: int = ceil(0.45 * caster.get_expertise().intelligence)
        damage = range(6 + bonus_damage, 9 + bonus_damage)

        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SeaSprayIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray IV",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 8-11 + 55% of your Intelligence damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=8,
            target_own_group=False,
            purchase_cost=400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        bonus_damage: int = ceil(0.55 * caster.get_expertise().intelligence)
        damage = range(8 + bonus_damage, 11 + bonus_damage)
        
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SeaSprayV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray V",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 10-13 + 65% of your Intelligence damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=10,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        bonus_damage: int = ceil(0.65 * caster.get_expertise().intelligence)
        damage = range(10 + bonus_damage, 13 + bonus_damage)
        
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, damage)
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CRABNADO
# -----------------------------------------------------------------------------

class CrabnadoI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="Crabnado I",
            class_key=ExpertiseClass.Fisher,
            description="If you have a Crab in your off-hand, deal 1-8 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-2,
            level_requirement=3,
            target_own_group=False,
            purchase_cost=75,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        off_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.OffHand)
        if off_hand_item is None or off_hand_item.get_key() != ItemKey.Crab:
            mana_and_cd_str = self.remove_mana_and_set_cd(caster)
            fail_str = "You don't have a crab equipped!"
            if mana_and_cd_str is not None:
                fail_str += f"\n\n{mana_and_cd_str}"
            
            caster.get_stats().dueling.fisher_abilities_used += 1
            return fail_str

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CrabnadoII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="Crabnado II",
            class_key=ExpertiseClass.Fisher,
            description="If you have a Crab in your off-hand, deal 2-10 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-2,
            level_requirement=6,
            target_own_group=False,
            purchase_cost=150,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        off_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.OffHand)
        if off_hand_item is None or off_hand_item.get_key() != ItemKey.Crab:
            mana_and_cd_str = self.remove_mana_and_set_cd(caster)
            fail_str = "You don't have a crab equipped!"
            if mana_and_cd_str is not None:
                fail_str += f"\n\n{mana_and_cd_str}"
            
            caster.get_stats().dueling.fisher_abilities_used += 1
            return fail_str

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 10))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CrabnadoIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            name="Crabnado III",
            class_key=ExpertiseClass.Fisher,
            description="If you have a Crab in your off-hand, deal 3-12 damage to EVERYONE (including yourself)",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=-2,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=300,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        off_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.OffHand)
        if off_hand_item is None or off_hand_item.get_key() != ItemKey.Crab:
            mana_and_cd_str = self.remove_mana_and_set_cd(caster)
            fail_str = "You don't have a crab equipped!"
            if mana_and_cd_str is not None:
                fail_str += f"\n\n{mana_and_cd_str}"
            
            caster.get_stats().dueling.fisher_abilities_used += 1
            return fail_str

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 12))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CURSE OF THE SEA
# -----------------------------------------------------------------------------

class CurseOfTheSeaI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea I",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -1 Constitution, -1 Strength, and -1 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=5,
            target_own_group=False,
            purchase_cost=200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=3,
            value=-1,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-1,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CurseOfTheSeaII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea II",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -3 Constitution, -3 Strength, and -3 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=3,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CurseOfTheSeaIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea III",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -5 Constitution, -5 Strength, and -5 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=13,
            target_own_group=False,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CurseOfTheSeaIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea IV",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -7 Constitution, -7 Strength, and -7 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=17,
            target_own_group=False,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=3,
            value=-7,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=3,
            value=-7,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-7,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HOOK
# -----------------------------------------------------------------------------

class HookI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook I",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 3-5 damage and causing them to lose -5 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=8,
            target_own_group=False,
            purchase_cost=200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(3, 5), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HookII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook II",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 4-7 damage and causing them to lose -10 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=10,
            target_own_group=False,
            purchase_cost=400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(4, 7), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HookIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook III",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 5-8 damage and causing them to lose -15 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 8), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HookIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook IV",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 6-9 damage and causing them to lose -20 Dexterity for 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=14,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=3,
            value=-20,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(6, 9), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WRATH OF THE WAVES
# -----------------------------------------------------------------------------

class WrathOfTheWavesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves I",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 5-10 damage each. They take 30% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=10,
            target_own_group=False,
            purchase_cost=400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for effect in caster.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.PiercingDmg:
                piercing_dmg += int(effect.effect_value)
            elif effect.effect_type == EffectType.PiercingPercentDmg:
                piercing_percent_dmg = min(piercing_percent_dmg + effect.effect_value, 1)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.3 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            base_damage = randint(5, 10)
            damage = min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage += ceil(damage * bonus_dmg_boost * stacking_damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrathOfTheWavesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves II",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 6-12 damage each. They take 60% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for effect in caster.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.PiercingDmg:
                piercing_dmg += int(effect.effect_value)
            elif effect.effect_type == EffectType.PiercingPercentDmg:
                piercing_percent_dmg = min(piercing_percent_dmg + effect.effect_value, 1)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.6 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            base_damage = randint(6, 12)
            damage = min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage += ceil(damage * bonus_dmg_boost * stacking_damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_taken += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WrathOfTheWavesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves III",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 10-15 damage each. They take 90% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=14,
            target_own_group=False,
            purchase_cost=1600,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for effect in caster.get_combined_req_met_effects().permanent:
            if effect.effect_type == EffectType.PiercingDmg:
                piercing_dmg += int(effect.effect_value)
            elif effect.effect_type == EffectType.PiercingPercentDmg:
                piercing_percent_dmg = min(piercing_percent_dmg + effect.effect_value, 1)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.9 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True

            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            base_damage = randint(10, 15)
            damage = min(ceil(base_damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage += ceil(damage * bonus_dmg_boost * stacking_damage)

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))

            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_taken += actual_damage_dealt + final_piercing_dmg
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HIGH TIDE
# -----------------------------------------------------------------------------

class HighTideI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide I",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 25%.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HighTideII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide II",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 45%.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=0,
            level_requirement=15,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.45,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HighTideIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide III",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 65%.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=3200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.65,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HighTideIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide IV",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 85%.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=0,
            level_requirement=21,
            target_own_group=True,
            purchase_cost=6400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.85,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# THUNDERING TORRENT
# -----------------------------------------------------------------------------

class ThunderingTorrentI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent I",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 10-15 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=2,
            level_requirement=14,
            target_own_group=False,
            purchase_cost=500,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(10, 15)
            
            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
            
            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(base_damage * stacking_damage)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=ceil(damage / 2),
                source_str=self.get_icon_and_name()
            ))

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThunderingTorrentII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent II",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 15-20 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=2,
            level_requirement=16,
            target_own_group=False,
            purchase_cost=1000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(15, 20)
            
            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
            
            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(base_damage * stacking_damage)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=ceil(damage / 2),
                source_str=self.get_icon_and_name()
            ))

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThunderingTorrentIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent III",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 20-25 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=2,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=2000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(20, 25)
            
            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
            
            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(base_damage * stacking_damage)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff
            
            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=ceil(damage / 2),
                source_str=self.get_icon_and_name()
            ))

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))
        
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ThunderingTorrentIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent IV",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 25-30 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=4000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = caster_equipment.get_dmg_buff_effect_totals(caster)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * caster.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * caster.get_expertise().hp)

        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(25, 30)
            
            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if se.caster == caster and se.source_str == self.get_icon_and_name():
                        stacking_damage += se.value
                elif se.key == StatusEffectKey.Poisoned and not poison_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffPoisoned]
                    poison_buff_applied = True
                elif se.key == StatusEffectKey.Bleeding and not bleeding_buff_applied:
                    bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffBleeding]
                    bleeding_buff_applied = True
            
            if target_dueling.is_legendary:
                bonus_percent_damage += dmg_buff_effect_totals[EffectType.DmgBuffLegends]

            target_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherMaxHealth] * target.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffOtherRemainingHealth] * target.get_expertise().hp)

            damage = ceil(base_damage * stacking_damage)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), base_damage)
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) + target_hp_dmg_buff + self_hp_dmg_buff
            
            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            cur_armor = target_dueling.armor

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=ceil(damage / 2),
                source_str=self.get_icon_and_name()
            ))

            se_str: str = ""
            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target_dueling != caster), se.on_being_hit_buffs))
                    se_str += "\n{" + f"{i + 1}" + "}" + f" gained {se.get_buffs_str()}"
                if se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                caster_dmg_reduct = caster.get_dueling().get_total_percent_dmg_reduct(caster.get_combined_req_met_effects())

                caster_org_armor = caster.get_dueling().armor
                actual_reflected_damage = caster.get_expertise().damage(reflected_damage, caster.get_dueling(), caster_dmg_reduct, ignore_armor=False)
                caster_cur_armor = caster.get_dueling().armor
                
                caster_dmg_reduct_str = f" ({abs(caster_dmg_reduct) * 100}% {'Reduction' if caster_dmg_reduct > 0 else 'Increase'})" if caster_dmg_reduct != 0 else ""
                reflect_armor_str = f" ({caster_cur_armor - caster_org_armor} Armor)" if caster_cur_armor - caster_org_armor < 0 else ""

                se_str += "\n{" + f"{i + 1}" + "}" + f" reflected {actual_reflected_damage}{reflect_armor_str}{caster_dmg_reduct_str} back to " + "{0}"

            target.get_expertise().update_stats(target.get_combined_attributes())

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({cur_armor - org_armor} Armor)" if cur_armor - org_armor < 0 else ""

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))
        
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DROWN IN THE DEEP
# -----------------------------------------------------------------------------

class DrownInTheDeepI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep I",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 2 enemies into the depths, dealing each (1 * # of status effects)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=4,
            num_targets=2,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=1200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_statuses = len(target_dueling.status_effects)

            damage = ceil((1 * num_statuses) / 100 * target_max_hp)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, 0, ignore_armor=True)

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DrownInTheDeepII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep II",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 2 enemies into the depths, dealing each (1.5 * # of status effects)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=4,
            num_targets=2,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_statuses = len(target_dueling.status_effects)

            damage = ceil((1.5 * num_statuses) / 100 * target_max_hp)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, 0, ignore_armor=True)

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DrownInTheDeepIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep III",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 2 enemies into the depths, dealing each (2 * # of status effects)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=4,
            num_targets=2,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=4800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_statuses = len(target_dueling.status_effects)

            damage = ceil((2 * num_statuses) / 100 * target_max_hp)
            damage += min(ceil(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            se_ability_use_str = "\n".join(caster.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAbilityUsed, target, caster, i + 1, 0, self._target_own_group)) 
            on_attack_or_ability_effect_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_attack_or_ability_effect_str += f"\n{result_str}"

            se_ability_used_against_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAbilityUsedAgainst, caster, target, 0, i + 1, self._target_own_group))
            on_ability_used_against_str = ""
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_ability_used_against:
                    damage, result_str = caster.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, caster, target, i + 1, damage, self.get_icon_and_name())
                    if result_str != "":
                        on_ability_used_against_str += f"\n{result_str}"
            
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, 0, ignore_armor=True)

            se_on_damage_str = ""
            on_attack_damage_effect_str = ""
            if actual_damage_dealt > 0 and target.get_expertise().hp > 0:
                se_on_damage_str = "\n".join(target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, caster, target, 0, i + 1, self._target_own_group))
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt, self.get_icon_and_name())
                        if result_str != "":
                            on_attack_damage_effect_str += f"\n{result_str}"

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            final_dmg_str = "{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage"
            non_empty_strs = list(filter(lambda s: s != "", [final_dmg_str, se_ability_use_str, on_attack_or_ability_effect_str, se_ability_used_against_str, on_ability_used_against_str, se_on_damage_str, on_attack_damage_effect_str]))
            results.append(NegativeAbilityResult("\n".join(non_empty_strs), False))

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            # Set dodged to true to ignore it in any computations that depend on dodge
            # Realistically, I think this should just be at the ability level, not here in the abstracted computation on a target.
            results.append(NegativeAbilityResult(mana_and_cd_str, True))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# WHIRLPOOL
# -----------------------------------------------------------------------------

class WhirlpoolI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool I",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 10-20 damage to all enemies and removes their attribute status effect buffs.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=1000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(10, 20))

        se_buffs = [StatusEffectKey.ConBuff, StatusEffectKey.StrBuff, StatusEffectKey.DexBuff, StatusEffectKey.IntBuff, StatusEffectKey.LckBuff]
        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects = list(filter(lambda x: x.key not in se_buffs, targets[i].get_dueling().status_effects))
                results[i].target_str += " and had their attribute buffs removed"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlpoolII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool II",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 15-25 damage to all enemies and removes their attribute status effect buffs.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(15, 25))

        se_buffs = [StatusEffectKey.ConBuff, StatusEffectKey.StrBuff, StatusEffectKey.DexBuff, StatusEffectKey.IntBuff, StatusEffectKey.LckBuff]
        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects = list(filter(lambda x: x.key not in se_buffs, targets[i].get_dueling().status_effects))
                results[i].target_str += " and had their attribute buffs removed"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlpoolIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool III",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 20-30 damage to all enemies and removes attribute status effect buffs from them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=4000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(20, 30))

        se_buffs = [StatusEffectKey.ConBuff, StatusEffectKey.StrBuff, StatusEffectKey.DexBuff, StatusEffectKey.IntBuff, StatusEffectKey.LckBuff]
        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects = list(filter(lambda x: x.key not in se_buffs, targets[i].get_dueling().status_effects))
                results[i].target_str += " and had their attribute buffs removed"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlpoolIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool IV",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 25-35 damage to all enemies and removes their attribute status effect buffs.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=8000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(25, 35))

        se_buffs = [StatusEffectKey.ConBuff, StatusEffectKey.StrBuff, StatusEffectKey.DexBuff, StatusEffectKey.IntBuff, StatusEffectKey.LckBuff]
        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects = list(filter(lambda x: x.key not in se_buffs, targets[i].get_dueling().status_effects))
                results[i].target_str += " and had their attribute buffs removed"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SHATTERING STORM 
# -----------------------------------------------------------------------------

class ShatteringStormI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm I",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 4 enemies, dealing 40-50 damage with a 20% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=4,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=5000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 50), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShatteringStormII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm II",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 4 enemies, dealing 50-60 damage with a 40% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=4,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=10000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.4,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(50, 60), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ShatteringStormIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm III",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 4 enemies, dealing 60-70 damage with a 60% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=4,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=20000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(60, 70), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.fisher_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# GUARDIAN ABILITIES
# -----------------------------------------------------------------------------
# WHIRLWIND
# -----------------------------------------------------------------------------

class WhirlwindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind I",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 50% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=2,
            target_own_group=False,
            purchase_cost=200,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(base_damage * 0.5)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlwindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind II",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 60% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=5,
            target_own_group=False,
            purchase_cost=400,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(base_damage * 0.6)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlwindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind III",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 70% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=8,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(base_damage * 0.7)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class WhirlwindIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind IV",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 80% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=-1,
            level_requirement=11,
            target_own_group=False,
            purchase_cost=1600,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(base_damage * 0.8)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SECOND WIND
# -----------------------------------------------------------------------------

class SecondWindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind I",
            class_key=ExpertiseClass.Guardian,
            description="Restore 25% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=3,
            target_own_group=True,
            purchase_cost=300,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.25)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SecondWindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind II",
            class_key=ExpertiseClass.Guardian,
            description="Restore 45% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.45)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SecondWindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind III",
            class_key=ExpertiseClass.Guardian,
            description="Restore 65% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=13,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.65)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BIDED ATTACK
# -----------------------------------------------------------------------------

class BidedAttackI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Bided Attack I",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +5 Strength for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=4,
            target_own_group=True,
            purchase_cost=200,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=2,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BidedAttackII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Bided Attack II",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +10 Strength for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=7,
            target_own_group=True,
            purchase_cost=800,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=2,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BidedAttackIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Bided Attack III",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +15 Strength for 2 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=2,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SCAR ARMOR
# -----------------------------------------------------------------------------

class ScarArmorI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Scar Armor I",
            class_key=ExpertiseClass.Guardian,
            description="Whenever you're damaged over the next 3 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=5,
            target_own_group=True,
            purchase_cost=400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        on_damage_buff = AttrBuffOnDamage(
            turns_remaining=3,
            on_being_hit_buffs=[ConBuff(
                turns_remaining=-1,
                value=1,
                source_str=self.get_icon_and_name()
            )],
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [on_damage_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScarArmorII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Scar Armor II",
            class_key=ExpertiseClass.Guardian,
            description="Whenever you're damaged over the next 6 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=15,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        on_damage_buff = AttrBuffOnDamage(
            turns_remaining=6,
            on_being_hit_buffs=[ConBuff(
                turns_remaining=-1,
                value=1,
                source_str=self.get_icon_and_name()
            )],
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [on_damage_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# UNBREAKING
# -----------------------------------------------------------------------------

class UnbreakingI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Unbreaking I",
            class_key=ExpertiseClass.Guardian,
            description="Gain +1 Constitution for each slot of armor you don't have equipped until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=caster.get_equipment().get_num_slots_unequipped(),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnbreakingII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Unbreaking II",
            class_key=ExpertiseClass.Guardian,
            description="Gain +2 Constitution for each slot of armor you don't have equipped until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=16,
            target_own_group=True,
            purchase_cost=2400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=2 * caster.get_equipment().get_num_slots_unequipped(),
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# COUNTERSTRIKE
# -----------------------------------------------------------------------------

class CounterstrikeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Counterstrike I",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 75% of your weapon damage + 10% of your missing health as damage (up to your base weapon damage).",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=700,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(0.75 * base_damage)
        damage += ceil(min(0.1 * (caster_expertise.max_hp - caster_expertise.hp), damage))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CounterstrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Counterstrike II",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 80% of your weapon damage + 20% of your missing health as damage (up to your 2x weapon damage).",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=1400,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(0.8 * base_damage)
        damage += ceil(min(0.2 * (caster_expertise.max_hp - caster_expertise.hp), 2 * base_damage))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CounterstrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Counterstrike III",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 85% of your weapon damage + 30% of your missing health as damage (up to 3x base weapon damage).",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=2800,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(0.85 * base_damage)
        damage += ceil(min(0.3 * (caster_expertise.max_hp - caster_expertise.hp), 3 * base_damage))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# TAUNT
# -----------------------------------------------------------------------------

class TauntI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDCCF",
            name="Taunt I",
            class_key=ExpertiseClass.Guardian,
            description="Force an enemy to attack you on their next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=6,
            target_own_group=False,
            purchase_cost=500,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        taunt = Taunted(
            turns_remaining=1,
            forced_to_attack=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [taunt])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TauntII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDCCF",
            name="Taunt II",
            class_key=ExpertiseClass.Guardian,
            description="Force up to 2 enemies to attack you on their next turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=2,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=1000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        taunt = Taunted(
            turns_remaining=1,
            forced_to_attack=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [taunt])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class TauntIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDCCF",
            name="Taunt III",
            class_key=ExpertiseClass.Guardian,
            description="Force up to 3 enemies to attack you on their next turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=3,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=2000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        taunt = Taunted(
            turns_remaining=1,
            forced_to_attack=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [taunt])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PIERCING STRIKE
# -----------------------------------------------------------------------------

class PiercingStrikeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Piercing Strike I",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 110% of your weapon damage with a 20% chance to set Bleeding for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=1000,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(1.1 * base_damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.2:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PiercingStrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Piercing Strike II",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 120% of your weapon damage with a 50% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=2000,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(1.2 * base_damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PiercingStrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Piercing Strike III",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 130% of your weapon damage with a 80% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=4000,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(1.3 * base_damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.8:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(bleed, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PRESS THE ADVANTAGE
# -----------------------------------------------------------------------------

class PressTheAdvantageI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD3A",
            name="Press the Advantage I",
            class_key=ExpertiseClass.Guardian,
            description="Gain a 45% damage buff for 3 turns and increase the time remaining on all your positive status effects by 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=8000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        se_results: Set[str] = set()
        for se in caster.get_dueling().status_effects:
            if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF:
                se.turns_remaining += 1
                se_results.add(se.name)
        se_result_str: str = "\n{0}'s " + ", ".join(se_results) + " status effects have been increased by 1 turn."
        result_str += se_result_str

        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

class PressTheAdvantageII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD3A",
            name="Press the Advantage II",
            class_key=ExpertiseClass.Guardian,
            description="Gain a 60% damage buff for 3 turns and increase the time remaining on all your positive status effects by 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=22,
            target_own_group=True,
            purchase_cost=16000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=3,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        se_results: Set[str] = set()
        for se in caster.get_dueling().status_effects:
            if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF:
                se.turns_remaining += 1
                se_results.add(se.name)
        se_result_str: str = "\n{0}'s " + ", ".join(se_results) + " status effects have been increased by 1 turn."
        result_str += se_result_str

        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PressTheAdvantageIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD3A",
            name="Press the Advantage III",
            class_key=ExpertiseClass.Guardian,
            description="Gain a 75% damage buff for 3 turns and increase the time remaining on all your positive status effects by 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=26,
            target_own_group=True,
            purchase_cost=32000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgBuff(
            turns_remaining=3,
            value=0.6,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        se_results: Set[str] = set()
        for se in caster.get_dueling().status_effects:
            if se.key in POSITIVE_STATUS_EFFECTS_ON_SELF:
                se.turns_remaining += 1
                se_results.add(se.name)
        se_result_str: str = "\n{0}'s " + ", ".join(se_results) + " status effects have been increased by 1 turn."
        result_str += se_result_str

        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# EVADE
# -----------------------------------------------------------------------------

class EvadeI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Evade I",
            class_key=ExpertiseClass.Guardian,
            description="Gain +100 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=2000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=100,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EvadeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Evade II",
            class_key=ExpertiseClass.Guardian,
            description="Gain +175 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=22,
            target_own_group=True,
            purchase_cost=4000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=175,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EvadeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Evade III",
            class_key=ExpertiseClass.Guardian,
            description="Gain +250 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=24,
            target_own_group=True,
            purchase_cost=8000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=250,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HEAVY SLAM
# -----------------------------------------------------------------------------

class HeavySlamI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Heavy Slam I",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 75% of your weapon damage + 25% of your Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2500,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(0.75 * base_damage + 0.25 * caster_attrs.strength)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavySlamII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Heavy Slam II",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 100% of your weapon damage + 50% of your Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=5000,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(1 * base_damage + 0.5 * caster_attrs.strength)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavySlamIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Heavy Slam III",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 125% of your weapon damage + 75% of your Strength.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=10000,
            scaling=[Attribute.Strength]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0        

        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()

        assert(weapon_stats is not None)
        base_damage = weapon_stats.get_random_base_damage(max(0, level_req - caster.get_expertise().level))
        damage = ceil(1.25 * base_damage + 0.75 * caster_attrs.strength)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# MERCHANT ABILITIES
# -----------------------------------------------------------------------------
# CONTRACT: WEALTH FOR POWER
# -----------------------------------------------------------------------------

class ContractWealthForPowerI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCDC",
            name="Contract: Wealth for Power I",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 25 coins for +1 Intelligence, +1 Strength, and +1 Dexterity until the end of the duel. If you can't pay, you instead receive -1 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=2,
            target_own_group=True,
            purchase_cost=50,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 25:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-1,
                source_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-1,
                source_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-1,
                source_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=1,
                source_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=1,
                source_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=1,
                source_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractWealthForPowerII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCDC",
            name="Contract: Wealth for Power II",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 50 coins for +3 Intelligence, +3 Strength, and +3 Dexterity until the end of the duel. If you can't pay, you instead receive -3 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=6,
            target_own_group=True,
            purchase_cost=100,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-3,
                source_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-3,
                source_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-3,
                source_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=3,
                source_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=3,
                source_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=3,
                source_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractWealthForPowerIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCDC",
            name="Contract: Wealth for Power III",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 75 coins for +5 Intelligence, +5 Strength, and +5 Dexterity until the end of the duel. If you can't pay, you instead receive -3 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 75:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-5,
                source_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-5,
                source_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-5,
                source_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=5,
                source_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=5,
                source_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=5,
                source_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# BOUND TO GET LUCKY
# -----------------------------------------------------------------------------

class BoundToGetLuckyI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky I",
            class_key=ExpertiseClass.Merchant,
            description="Gain +10 Luck for the next 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=4,
            target_own_group=True,
            purchase_cost=100,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=3,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky II",
            class_key=ExpertiseClass.Merchant,
            description="Gain +30 Luck for the next 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=6,
            target_own_group=True,
            purchase_cost=200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=3,
            value=30,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky III",
            class_key=ExpertiseClass.Merchant,
            description="Gain +50 Luck for the next 3 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=3,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky IV",
            class_key=ExpertiseClass.Merchant,
            description="Gain +50 Luck for the next 4 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=4,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky V",
            class_key=ExpertiseClass.Merchant,
            description="Gain +50 Luck for the next 5 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=5,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=5,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SILKSPEAKING
# -----------------------------------------------------------------------------

class SilkspeakingI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE3\uFE0F",
            name="Silkspeaking",
            class_key=ExpertiseClass.Merchant,
            description="Convince an enemy not to attack, use an ability, or target you with an item next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=3,
            num_targets=1,
            level_requirement=6,
            target_own_group=False,
            purchase_cost=1000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        cannot_target = CannotTarget(
            turns_remaining=1,
            cant_target=caster,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [cannot_target])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# A TIDY SUM
# -----------------------------------------------------------------------------

class ATidySumI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="A Tidy Sum I",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 4 turns, part of the enemy struck turns into generated coins, awarding you 5 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=300,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=4,
            value=5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ATidySumII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="A Tidy Sum II",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 4 turns, part of the enemy struck turns into generated coins, awarding you 10 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=4,
            value=10,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ATidySumIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="A Tidy Sum III",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 4 turns, part of the enemy struck turns into generated coins, awarding you 15 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=4,
            value=15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CURSED COINS
# -----------------------------------------------------------------------------

class CursedCoinsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins I",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain generated coins, deal 50% of that as damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=300,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CursedCoinsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins II",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain generated coins, deal 75% of that as damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CursedCoinsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins III",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain generated coins, deal 100% of that as damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=14,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CursedCoinsIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins IV",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain generated coins, deal 125% of that as damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=16,
            target_own_group=True,
            purchase_cost=2400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=1.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# UNSEEN RICHES
# -----------------------------------------------------------------------------

class UnseenRichesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches I",
            class_key=ExpertiseClass.Merchant,
            description="Generate coins equal to 25% of your total Luck. 25% of those coins are added to your inventory.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=-1,
            level_requirement=11,
            target_own_group=False,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        adjusted_coins: int = int(0.25 * coins_to_add)
        caster.get_inventory().add_coins(int(0.25 * adjusted_coins))

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str
        
        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnseenRichesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches II",
            class_key=ExpertiseClass.Merchant,
            description="Generate coins equal to 50% of your total Luck. 25% of those coins are added to your inventory.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=-1,
            level_requirement=13,
            target_own_group=False,
            purchase_cost=1600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        adjusted_coins: int = int(0.5 * coins_to_add)
        caster.get_inventory().add_coins(int(0.25 * adjusted_coins))

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou generated {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnseenRichesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches III",
            class_key=ExpertiseClass.Merchant,
            description="Generate coins equal to 75% of your total Luck. 25% of those coins are added to your inventory.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=3200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        adjusted_coins: int = int(0.75 * coins_to_add)
        caster.get_inventory().add_coins(int(0.25 * adjusted_coins))

        tarnished_value = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.Tarnished:
                tarnished_value = se.value
        
        cursed_coins_damage = 0
        if tarnished_value != 0:
            cursed_coins_damage += int(tarnished_value * adjusted_coins)

        result_str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou generated {adjusted_coins} coins."

        if cursed_coins_damage != 0:
            for i, target in enumerate(targets):
                org_armor = target.get_dueling().armor
                percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                actual_cc_damage = target.get_expertise().damage(cursed_coins_damage, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                armor_str = f" ({target.get_dueling().armor - org_armor} Armor)" if target.get_dueling().armor - org_armor < 0 else ""

                caster.get_stats().dueling.damage_dealt += actual_cc_damage
                target.get_stats().dueling.damage_taken += actual_cc_damage

                result_str += "\n{0}" + f" dealt {actual_cc_damage}{armor_str} damage to " + "{" + f"{i + 1}" + "} using Cursed Coins"

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CONTRACT: MANA TO BLOOD
# -----------------------------------------------------------------------------

class ContractManaToBloodI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood I",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 90% of their cost in HP for the next 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=14,
            target_own_group=True,
            purchase_cost=800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=3,
            value=0.9,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractManaToBloodII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood II",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 70% of their cost in HP for the next 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=16,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=3,
            value=0.7,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractManaToBloodIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood III",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 50% of their cost in HP for the next 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=3200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=3,
            value=0.5,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CONTRACT: BLOOD FOR BLOOD
# -----------------------------------------------------------------------------

class ContractBloodForBloodI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Contract: Blood for Blood I",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 15% of your current health and deals 50% of that damage against up to 2 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=2,
            level_requirement=16,
            target_own_group=False,
            purchase_cost=1500,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        percent_health: int = ceil(0.15 * current_health)
        damage: int = int(0.15 * 0.5 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        damage_dealt = caster.get_expertise().damage(percent_health, caster.get_dueling(), percent_reduct=0, ignore_armor=True)
        result_str += "\n{0} took " + f"{damage_dealt} damage to cast Blood for Blood"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractBloodForBloodII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Contract: Blood for Blood II",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 10% of your current health and deals 100% of that damage against up to 2 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=2,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=3000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        percent_health: int = ceil(0.1 * current_health)
        damage: int = int(percent_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        damage_dealt = caster.get_expertise().damage(percent_health, caster.get_dueling(), percent_reduct=0, ignore_armor=True)
        result_str += "\n{0} took " + f"{damage_dealt} damage to cast Blood for Blood"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractBloodForBloodIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Contract: Blood for Blood III",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 5% of your current health and deals 300% of that damage against up to 2 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=2,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=6000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        percent_health: int = ceil(0.05 * current_health)
        damage: int = int(3 * percent_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        damage_dealt = caster.get_expertise().damage(percent_health, caster.get_dueling(), percent_reduct=0, ignore_armor=True)
        result_str += "\n{0} took " + f"{damage_dealt} damage to cast Blood for Blood"

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# DEEP POCKETS
# -----------------------------------------------------------------------------

class DeepPocketsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Deep Pockets I",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=19,
            target_own_group=False,
            purchase_cost=8000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = min(100, int(0.01 * caster.get_inventory().get_coins()))
        caster.get_inventory().remove_coins(damage)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeepPocketsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Deep Pockets II",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 150 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=16000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = min(150, int(0.01 * caster.get_inventory().get_coins()))
        caster.get_inventory().remove_coins(damage)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class DeepPocketsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Deep Pockets III",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 200 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=25,
            target_own_group=False,
            purchase_cost=32000,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage: int = min(200, int(0.01 * caster.get_inventory().get_coins()))
        caster.get_inventory().remove_coins(damage)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.merchant_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# ALCHEMIST ABILITIES
# -----------------------------------------------------------------------------
# INCENSE
# -----------------------------------------------------------------------------

class IncenseI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2601\uFE0F",
            name="Incense I",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 2-4 health to all allies.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=1,
            target_own_group=True,
            purchase_cost=100,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(2, 4))
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IncenseII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2601\uFE0F",
            name="Incense II",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 5-7 health to all allies.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=4,
            target_own_group=True,
            purchase_cost=200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(5, 7))
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IncenseIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2601\uFE0F",
            name="Incense III",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 7-9 health to all allies.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=7,
            target_own_group=True,
            purchase_cost=400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(7, 9))
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IncenseIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2601\uFE0F",
            name="Incense IV",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 9-11 health to all allies.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(9, 11))
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class IncenseV(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2601\uFE0F",
            name="Incense V",
            class_key=ExpertiseClass.Alchemist,
            description="Restore 11-13 health to all allies.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=-1,
            level_requirement=13,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(11, 13))
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PREPARE POTIONS
# -----------------------------------------------------------------------------

class PreparePotionsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2697\uFE0F",
            name="Prepare Potions I",
            class_key=ExpertiseClass.Alchemist,
            description="Potions you use are 15% more effective for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=3,
            target_own_group=True,
            purchase_cost=150,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        prep_potions_buff = PotionBuff(
            turns_remaining=3,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [prep_potions_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PreparePotionsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2697\uFE0F",
            name="Prepare Potions II",
            class_key=ExpertiseClass.Alchemist,
            description="Potions you use are 25% more effective for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=5,
            target_own_group=True,
            purchase_cost=150,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        prep_potions_buff = PotionBuff(
            turns_remaining=3,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [prep_potions_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PreparePotionsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2697\uFE0F",
            name="Prepare Potions III",
            class_key=ExpertiseClass.Alchemist,
            description="Potions you use are 35% more effective for 3 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=7,
            target_own_group=True,
            purchase_cost=150,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        prep_potions_buff = PotionBuff(
            turns_remaining=3,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [prep_potions_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# VITALITY TRANSFER
# -----------------------------------------------------------------------------

class VitalityTransferI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC9E",
            name="Vitality Transfer I",
            class_key=ExpertiseClass.Alchemist,
            description="Take 15% of your max health as damage and restore that much health to an ally.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=5,
            target_own_group=True,
            purchase_cost=300,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.15)
        caster.get_expertise().damage(damage_amount, caster.get_dueling(), percent_reduct=0, ignore_armor=True)

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and took {damage_amount} damage to cast it!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount), max_heal_amount=heal_amount)
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VitalityTransferII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC9E",
            name="Vitality Transfer II",
            class_key=ExpertiseClass.Alchemist,
            description="Take 25% of your max health as damage and restore that much health to an ally.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.25)
        caster.get_expertise().damage(damage_amount, caster.get_dueling(), percent_reduct=0, ignore_armor=True)

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and took {damage_amount} damage to cast it!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount), max_heal_amount=heal_amount)
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class VitalityTransferIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC9E",
            name="Vitality Transfer III",
            class_key=ExpertiseClass.Alchemist,
            description="Take 35% of your max health as damage and restore that much health to an ally.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=11,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.35)
        caster.get_expertise().damage(damage_amount, caster.get_dueling(), percent_reduct=0, ignore_armor=True)

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()} and took {damage_amount} damage to cast it!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount), max_heal_amount=heal_amount)
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# CLEANSE
# -----------------------------------------------------------------------------

class CleanseI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Cleanse I",
            class_key=ExpertiseClass.Alchemist,
            description="Remove all status effects from an ally.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=1,
            level_requirement=7,
            target_own_group=True,
            purchase_cost=1600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[str] = []
        for i, target in enumerate(targets):
            target.get_dueling().status_effects = []
            target.get_expertise().update_stats(target.get_combined_attributes())
            results.append("{" + f"{i + 1}" + "}" + f" has had their status effects removed")
        result_str += "\n".join(results)

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# TOXIC CLOUD
# -----------------------------------------------------------------------------

class ToxicCloudI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Toxic Cloud I",
            class_key=ExpertiseClass.Alchemist,
            description="Create a miasma that deals 1-3 damage to all enemies with a 30% chance to Poison them for 5% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=400,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 3))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.3:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class ToxicCloudII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Toxic Cloud II",
            class_key=ExpertiseClass.Alchemist,
            description="Create a miasma that deals 2-4 damage to all enemies with a 50% chance to Poison them for 5% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.5:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class ToxicCloudIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Toxic Cloud III",
            class_key=ExpertiseClass.Alchemist,
            description="Create a miasma that deals 3-5 damage to all enemies with a 70% chance to Poison them for 5% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=1600,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 5))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.7:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"

        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class ToxicCloudIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2B",
            name="Toxic Cloud IV",
            class_key=ExpertiseClass.Alchemist,
            description="Create a miasma that deals 4-6 damage to all enemies with a 90% chance to Poison them for 5% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=2,
            num_targets=-1,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=3200,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 6))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.9:
                se_str = targets[i].get_dueling().add_status_effect_with_resist(poisoned, targets[i], i + 1)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and {se_str}"
        
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        
        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SMOKESCREEN
# -----------------------------------------------------------------------------

class SmokescreenI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA3",
            name="Smokescreen I",
            class_key=ExpertiseClass.Alchemist,
            description="All allies gain +25 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=5,
            num_targets=-1,
            level_requirement=11,
            target_own_group=True,
            purchase_cost=600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SmokescreenII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA3",
            name="Smokescreen II",
            class_key=ExpertiseClass.Alchemist,
            description="All allies gain +50 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=5,
            num_targets=-1,
            level_requirement=14,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=50,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SmokescreenIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA3",
            name="Smokescreen III",
            class_key=ExpertiseClass.Alchemist,
            description="All allies gain +75 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=5,
            num_targets=-1,
            level_requirement=17,
            target_own_group=True,
            purchase_cost=2400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# EMPOWERMENT
# -----------------------------------------------------------------------------

class EmpowermentI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Empowerment I",
            class_key=ExpertiseClass.Alchemist,
            description="Choose an ally. They regain Mana equal to their Intelligence.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=1,
            level_requirement=13,
            target_own_group=True,
            purchase_cost=2800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[str] = []
        for i, target in enumerate(targets):
            mana_to_restore: int = target.get_expertise().intelligence
            target.get_expertise().restore_mana(mana_to_restore)
            results.append("{" + f"{i + 1}" + "}" + f" regained {mana_to_restore} mana")
        result_str += "\n".join(results)

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EmpowermentII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Empowerment II",
            class_key=ExpertiseClass.Alchemist,
            description="Choose an ally. They regain Mana equal to double their Intelligence.",
            flavor_text="",
            mana_cost=25,
            cooldown=2,
            num_targets=1,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=5600,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[str] = []
        for i, target in enumerate(targets):
            mana_to_restore: int = 2 * target.get_expertise().intelligence
            target.get_expertise().restore_mana(mana_to_restore)
            results.append("{" + f"{i + 1}" + "}" + f" regained {mana_to_restore} mana")
        result_str += "\n".join(results)

        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            result_str += "\n" + mana_and_cd_str

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# FESTERING VAPOR
# -----------------------------------------------------------------------------

class FesteringVaporI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Festering Vapor I",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 10-20 damage to all enemies that are Poisoned.",
            flavor_text="",
            mana_cost=40,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        filtered_targets = [target for target in targets if any(se.key == StatusEffectKey.Poisoned for se in target.get_dueling().status_effects)]

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, filtered_targets, range(10, 20))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class FesteringVaporII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Festering Vapor II",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 20-30 damage to all enemies that are Poisoned.",
            flavor_text="",
            mana_cost=40,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        filtered_targets = [target for target in targets if any(se.key == StatusEffectKey.Poisoned for se in target.get_dueling().status_effects)]

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, filtered_targets, range(20, 30))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore


class FesteringVaporIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Festering Vapor III",
            class_key=ExpertiseClass.Alchemist,
            description="Deal 30-40 damage to all enemies that are Poisoned.",
            flavor_text="",
            mana_cost=40,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800,
            scaling=[Attribute.Intelligence]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        filtered_targets = [target for target in targets if any(se.key == StatusEffectKey.Poisoned for se in target.get_dueling().status_effects)]

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, filtered_targets, range(30, 40))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # This is a bit of a hack to ignore the state being passed in and
        # use the defaults in init since no state vars are ever needed.
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# POISONOUS SKIN
# -----------------------------------------------------------------------------

class PoisonousSkinI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD8E",
            name="Poisonous Skin I",
            class_key=ExpertiseClass.Alchemist,
            description="Poison damage instead heals you until the end of the fight.",
            flavor_text="",
            mana_cost=25,
            cooldown=-1,
            num_targets=0,
            level_requirement=17,
            target_own_group=True,
            purchase_cost=3000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        poison_heals_buff = PoisonHeals(
            turns_remaining=-1,
            value=1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [poison_heals_buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# REGENERATION
# -----------------------------------------------------------------------------

class RegenerationI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u267B\uFE0F",
            name="Regeneration I",
            class_key=ExpertiseClass.Alchemist,
            description="Choose up to 2 allies. For the next 2 turns, they regain 10% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=6,
            num_targets=2,
            level_requirement=19,
            target_own_group=True,
            purchase_cost=1200,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.1,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [regenerating])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RegenerationII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u267B\uFE0F",
            name="Regeneration II",
            class_key=ExpertiseClass.Alchemist,
            description="Choose up to 2 allies. For the next 2 turns, they regain 15% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=6,
            num_targets=2,
            level_requirement=21,
            target_own_group=True,
            purchase_cost=2400,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [regenerating])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class RegenerationIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u267B\uFE0F",
            name="Regeneration III",
            class_key=ExpertiseClass.Alchemist,
            description="Choose up to 2 allies. For the next 2 turns, they regain 20% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=6,
            num_targets=2,
            level_requirement=23,
            target_own_group=True,
            purchase_cost=4800,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.2,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [regenerating])
        result_str += "\n".join(results)

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# PARALYZING FUMES
# -----------------------------------------------------------------------------

class ParalyzingFumesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Paralyzing Fumes I",
            class_key=ExpertiseClass.Alchemist,
            description="Release a dangerous gas that has a 75% chance to Falter all enemies at the start of their next turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=5,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=5000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        faltering = TurnSkipChance(
            turns_remaining=1,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [faltering])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ParalyzingFumesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Paralyzing Fumes I",
            class_key=ExpertiseClass.Alchemist,
            description="Release a dangerous gas that has a 75% chance to Falter all enemies at the start of their next 2 turns.",
            flavor_text="",
            mana_cost=40,
            cooldown=5,
            num_targets=-1,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=10000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        faltering = TurnSkipChance(
            turns_remaining=2,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [faltering])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.alchemist_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# QUICK ACCESS
# -----------------------------------------------------------------------------

class QuickAccessI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCBC",
            name="Quick Access I",
            class_key=ExpertiseClass.Alchemist,
            description="With deft hands, you're able to use 3 items this turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=22,
            target_own_group=True,
            purchase_cost=8000,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        caster.get_dueling().actions_remaining += 3
        caster.get_stats().dueling.alchemist_abilities_used += 1

        restriction = RestrictedToItems(
            turns_remaining=1,
            value=0,
            source_str=self.get_icon_and_name()
        )
        self._use_positive_status_effect_ability(caster, targets, [restriction])

        return "{0}" + f" used {self.get_icon_and_name()}!\n\nYou may now use up to 3 items from your inventory."

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore
