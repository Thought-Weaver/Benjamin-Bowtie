from __future__ import annotations

import itertools
import logging
import jsonpickle

from math import ceil
from random import choice, random

from dataclasses import dataclass
from features.npcs.summons.waveform import Waveform
from features.npcs.summons.crab_servant import CrabServant
from features.shared.ability import Ability
from features.shared.constants import DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.enums import ClassTag, Summons
from features.shared.item import WeaponStats
from features.shared.statuseffect import *

from typing import Dict, List, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from features.dueling import Dueling
    from features.npcs.npc import NPC
    from features.shared.item import Item


class Intent(StrEnum):
    Attack = "Attack"
    Ability = "Ability"
    Item = "Item"

class SimulationDuel():
    # Using a data class instead of a tuple to make the code more readable
    @dataclass
    class DuelResult():
        game_won: bool
        winners: List[NPC] | None

    def __init__(self, allies: List[NPC], enemies: List[NPC], logger: logging.Logger | None, max_turns: int, skip_init_updates: bool=False):
        self._allies: List[NPC] = allies
        for ally in self._allies:
            self.add_summons(ally.get_equipment().get_summons_enums(ally), self._allies)

        self._enemies: List[NPC] = enemies
        for enemy in self._enemies:
            self.add_summons(enemy.get_equipment().get_summons_enums(enemy), self._enemies)

        self._turn_order: List[NPC] = sorted(self._allies + self._enemies, key=lambda x: x.get_combined_attributes().dexterity, reverse=True)
        self._turn_index: int = 0

        self._selected_targets: List[NPC] = []
        self._targets_remaining = 1
        self._selected_ability: (Ability | None) = None
        self._selected_ability_index: int = -1
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1
        self._target_own_group: bool = False
        self._current_target: NPC | None = None # For passing along to the confirmation
        self._current_target_index: int = -1

        self.turns_taken: int = 0
        self._MAX_TURNS: int = max_turns

        self._logger: logging.Logger | None = logger

        self._additional_info_string_data = ""

        if not skip_init_updates:
            for entity in allies + enemies:
                entity.get_dueling().is_in_combat = True
                entity.get_dueling().armor = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
                # Make sure stats are correct.
                entity.get_expertise().update_stats(entity.get_combined_attributes())

            while self.turns_taken < self._MAX_TURNS:
                should_continue: bool = self.take_npc_turn()
                if not should_continue:
                    break

    def get_name(self, entity: NPC):
        return entity.get_name()

    def get_turn_index(self, entity: NPC):
        for i, other_entity in enumerate(self._turn_order):
            if other_entity == entity:
                return i
        return -1

    def get_entities_by_ids(self, ids: List[str]):
        entities: List[NPC] = []
        for entity_id in ids:
            for entity in self._turn_order:
                if entity.get_id() == entity_id:
                    entities.append(entity)
        return entities

    def add_summons(self, summons: List[Summons], entity_list: List[NPC]):
        for summon in summons:
            if summon == Summons.Waveform:
                entity_list.append(Waveform())
            elif summon == Summons.CrabServant:
                entity_list.append(CrabServant())
    
    def check_for_win(self) -> DuelResult:
        allies_alive: List[NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._allies))
        enemies_alive: List[NPC] = list(filter(lambda x: x.get_expertise().hp != 0, self._enemies))
        
        if len(allies_alive) == 0 and len(enemies_alive) == 0: # Tie, which may happen due to reflected damage
            return self.DuelResult(True, None)
        if len(enemies_alive) == 0:
            return self.DuelResult(True, self._allies)
        if len(allies_alive) == 0:
            return self.DuelResult(True, self._enemies)
        
        return self.DuelResult(False, None)

    def _reset_turn_variables(self):
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

    def set_next_turn(self, init_info_str: str=""):
        self.turns_taken += 1
        
        previous_entity: NPC = self._turn_order[self._turn_index]
        
        item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnEnd, previous_entity, previous_entity, 0, 0, True)
        
        self._additional_info_string_data = init_info_str

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
                    self._additional_info_string_data += result_str + "\n"

        self._turn_index = (self._turn_index + 1) % len(self._turn_order)
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        entity: NPC = self._turn_order[self._turn_index]

        start_item_status_effects: List[str] = previous_entity.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnTurnStart, entity, entity, 0, 0, True)
        
        for result_str in start_item_status_effects:
            formatted_str = result_str.format(self.get_name(previous_entity))
            self._additional_info_string_data += formatted_str + "\n"

        for item in entity.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is None:
                continue
            for item_effect in item_effects.on_turn_start:
                result_str = entity.get_dueling().apply_on_turn_start_or_end_effects(item, item_effect, entity, self.get_name(entity), is_turn_start=True, source_str=item.get_full_name())
                if result_str != "":
                    self._additional_info_string_data += result_str + "\n"
        
        start_percent_damage: int = 0
        start_damage: int = 0
        start_heals: int = 0
        start_armor_restore: int = 0
        max_should_skip_chance: float = 0
        heals_from_poison: bool = any(se.key == StatusEffectKey.PoisonHeals for se in entity.get_dueling().status_effects)
        max_sleeping_chance: float = 0

        max_armor: int = entity.get_equipment().get_total_reduced_armor(entity.get_expertise().level, entity.get_expertise().get_all_attributes() + entity.get_equipment().get_total_attribute_mods())
    
        for se in entity.get_dueling().status_effects:
            if se.turns_remaining > 0 or se.turns_remaining == -1:
                if se.key == StatusEffectKey.FixedDmgTick:
                    start_damage += int(se.value)
                if se.key == StatusEffectKey.Bleeding:
                    start_percent_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.Poisoned:
                    if heals_from_poison:
                        start_heals += ceil(entity.get_expertise().max_hp * se.value)
                    else:
                        start_percent_damage += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.RegenerateHP:
                    start_heals += ceil(entity.get_expertise().max_hp * se.value)
                if se.key == StatusEffectKey.RegenerateArmor:
                    start_armor_restore += ceil(max_armor * se.value)
                # Only take the largest chance to skip the turn
                if se.key == StatusEffectKey.TurnSkipChance:
                    max_should_skip_chance = max(se.value, max_should_skip_chance)
                if se.key == StatusEffectKey.Sleeping:
                    max_sleeping_chance = max(se.value, max_sleeping_chance)
            
        # Fixed damage is taken directly, no reduction, but still goes through armor
        if start_damage > 0:
            entity.get_expertise().damage(start_damage, entity.get_dueling(), percent_reduct=0, ignore_armor=False)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_damage} damage! "

        # Percent damage is taken directly, no reduction and ignoring armor
        if start_percent_damage > 0:
            entity.get_expertise().damage(start_percent_damage, entity.get_dueling(), percent_reduct=0, ignore_armor=True)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_percent_damage} damage! "

        decaying_adjustment: float = 0
        for se in entity.get_dueling().status_effects:
            if se.key == StatusEffectKey.Decaying:
                decaying_adjustment += se.value

        if decaying_adjustment != 0:
            start_heals += ceil(start_heals * -decaying_adjustment)

        entity.get_expertise().heal(start_heals)
        if start_heals > 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} had {start_heals} health restored! "
        elif start_heals < 0:
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} took {start_heals} damage due to Decaying! "

        if start_armor_restore != 0:
            pre_armor: int = entity.get_dueling().armor
            entity.get_dueling().armor = min(entity.get_dueling().armor + start_armor_restore, max_armor)
            armor_restore_diff: int = entity.get_dueling().armor - pre_armor
            if armor_restore_diff != 0:
                if self._additional_info_string_data != "":
                    self._additional_info_string_data += "\n"
                self._additional_info_string_data += f"{self.get_name(entity)} had {armor_restore_diff} armor restored! "

        turn_skipped: bool = False
        if random() < max_should_skip_chance:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)}'s turn was skipped!"
            # This is a special case to make sure that Faltering doesn't always skip the entity; if it triggers,
            # then it has to be decremented to avoid potentially skipping their turn forever
            entity.get_dueling().decrement_all_ability_cds()
            entity.get_dueling().decrement_statuses_time_remaining()
            entity.get_expertise().update_stats(entity.get_combined_attributes())

        if random() < max_sleeping_chance and not turn_skipped:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)
            if self._additional_info_string_data != "":
                self._additional_info_string_data += "\n"
            self._additional_info_string_data += f"{self.get_name(entity)} is Sleeping and their turn was skipped!"
            # This is a special case to make sure that Sleeping doesn't always skip the entity; if it triggers,
            # then it has to be decremented to avoid potentially skipping their turn forever
            entity.get_dueling().decrement_all_ability_cds()
            entity.get_dueling().decrement_statuses_time_remaining()
            entity.get_expertise().update_stats(entity.get_combined_attributes())

        duel_result = self.check_for_win()
        if duel_result.game_won:
            return duel_result

        # Continue to iterate if the fixed damage killed the current entity
        while self._turn_order[self._turn_index].get_expertise().hp == 0:
            self._turn_index = (self._turn_index + 1) % len(self._turn_order)

        self._reset_turn_variables()

        return duel_result

    def _is_ally(self, entity: NPC):
        cur_turn_player = self._turn_order[self._turn_index]
        
        self_charmed: bool = any(se.key == StatusEffectKey.Charmed for se in cur_turn_player.get_dueling().status_effects)
        entity_charmed: bool = any(se.key == StatusEffectKey.Charmed for se in entity.get_dueling().status_effects)

        if cur_turn_player in self._allies and not self_charmed:
            return entity in self._allies if not entity_charmed else entity in self._enemies
        else:
            return entity in self._enemies if not entity_charmed else entity in self._allies

    def get_victory_screen(self, duel_result: DuelResult):
        if duel_result.winners is None:
            for entity in self._turn_order:
                entity.get_dueling().status_effects = []
                entity.get_dueling().is_in_combat = False
                entity.get_dueling().reset_ability_cds()

                entity.get_expertise().update_stats(entity.get_combined_attributes())
                entity.get_expertise().hp = entity.get_expertise().max_hp
                entity.get_expertise().mana = entity.get_expertise().max_mana

                entity.get_stats().companions.companion_battles_fought += 1
                entity.get_stats().companions.companion_battles_tied += 1

                entity.get_expertise().level_up_check()

            if self._logger is not None:
                self._logger.log(level=logging.INFO, msg="Result: Tie")

            return
        
        losers = self._allies if duel_result.winners == self._enemies else self._enemies

        for winner in duel_result.winners:
            winner.get_stats().dueling.duels_fought += 1
            winner.get_stats().dueling.duels_won += 1
        for loser in losers:
            loser.get_stats().dueling.duels_fought += 1

        winner_str = ""
        for winner in duel_result.winners:
            winner_expertise = winner.get_expertise()
            winner_dueling = winner.get_dueling()
                        
            winner_dueling.reset_ability_cds()
            winner_dueling.status_effects = []
            winner_dueling.is_in_combat = False

            winner_expertise.update_stats(winner.get_combined_attributes())
            winner_expertise.hp = winner_expertise.max_hp
            winner_expertise.mana = winner_expertise.max_mana

            winner_expertise.level_up_check()

            winner_str += f"{self.get_name(winner)}\n"

        loser_str = ""
        for loser in losers:
            loser_expertise = loser.get_expertise()
            loser_dueling = loser.get_dueling()
            
            loser_dueling.reset_ability_cds()
            loser_dueling.status_effects = []
            loser_dueling.is_in_combat = False

            loser_expertise.update_stats(loser.get_combined_attributes())
            loser_expertise.hp = loser_expertise.max_hp
            loser_expertise.mana = loser_expertise.max_mana

            loser_expertise.level_up_check()

            loser_str += f"{self.get_name(loser)}\n"

        if self._logger is not None:
            self._logger.log(level=logging.INFO, msg=f"To those victorious:\n\n{winner_str}\nAnd to those who were vanquished:\n\n{loser_str}")

    def attack_selected_targets(self):
        attacker = self._turn_order[self._turn_index]
        attacker_name = self.get_name(attacker)
        attacker_attrs = attacker.get_combined_attributes()
        attacker_equipment = attacker.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = attacker_equipment.get_dmg_buff_effect_totals(attacker)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * attacker.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * attacker.get_expertise().hp)

        generating_value = 0
        tarnished_value = 0
        bonus_damage: int = 0
        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        chance_status_effect: List[Tuple[StatusEffect, float]] = []
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
            elif isinstance(se, AttackingChanceToApplyStatus):
                chance_status_effect.append((se.status_effect, se.value))
        cursed_coins_damage = 0

        main_hand_item = attacker_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        level_req: int = main_hand_item.get_level_requirement() if main_hand_item is not None else 0
        # Base possible damage is [1, 2], basically fist fighting
        unarmed_strength_bonus = int(attacker_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        splash_dmg: int = 0
        splash_percent_dmg: float = 0
        piercing_dmg: int = 0
        piercing_percent_dmg: float = 0
        for item in attacker_equipment.get_all_equipped_items():
            other_item_effects = item.get_item_effects()
            if other_item_effects is not None:
                for item_effect in other_item_effects.permanent:
                    if not item_effect.meets_conditions(attacker, item):
                        continue

                    if item_effect.effect_type == EffectType.SplashDmg:
                        splash_dmg += int(item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.SplashPercentMaxDmg:
                        splash_percent_dmg += ceil(weapon_stats.get_max_damage() * item_effect.effect_value) # type: ignore
                    elif item_effect.effect_type == EffectType.PiercingDmg:
                        piercing_dmg += int(item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.PiercingPercentDmg:
                        piercing_percent_dmg = min(piercing_percent_dmg + item_effect.effect_value, 1)

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
 
            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1 
            base_damage = weapon_stats.get_random_damage(attacker_attrs, item_effects, max(0, level_req - attacker.get_expertise().level)) # type: ignore

            stacking_damage: float = 1
            poison_buff_applied: bool = False
            bleeding_buff_applied: bool = False
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.StackingDamage:
                    assert(isinstance(se, StackingDamage))
                    if main_hand_item is not None and se.caster == attacker and se.source_str == main_hand_item.get_full_name():
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
            damage = ceil(damage * critical_hit_final * bonus_percent_damage) 
            damage += bonus_damage + target_hp_dmg_buff + self_hp_dmg_buff

            final_piercing_dmg = piercing_dmg + ceil(piercing_percent_dmg * base_damage)
            damage = max(damage - final_piercing_dmg, 0)

            # Doing these after damage computation because the player doesn't get an indication the effect occurred
            # until the Continue screen, so it feels slightly more natural to have them not affect damage dealt. I
            # may reverse this decision later.
            result_strs += [s.format(target_name, attacker_name) for s in attacker.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, attacker, 0, 1, self._is_ally(target))]
            for se, chance in chance_status_effect:
                if random() < chance:
                    result_strs += target.get_dueling().add_status_effect_with_resist(se, target, 0).format(target_name)

            for item in attacker_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_successful_attack:
                    damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, attacker, target, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAttacked, attacker, target, 0, 1, self._is_ally(target))]

            for item in target_equipment.get_all_equipped_items():
                other_item_effects = item.get_item_effects()
                if other_item_effects is None:
                    continue
                for item_effect in other_item_effects.on_attacked:
                    damage, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, damage, item.get_full_name())
                    if result_str != "":
                        result_strs.append(result_str.format(attacker_name, target_name))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct(target.get_combined_req_met_effects())

            org_armor = target_dueling.armor
            actual_damage_dealt = target_expertise.damage(damage, target_dueling, percent_dmg_reduct, ignore_armor=False)
            piercing_damage_dealt = target_expertise.damage(final_piercing_dmg, target_dueling, percent_dmg_reduct, ignore_armor=True)

            if (actual_damage_dealt > 0 or piercing_damage_dealt > 0) and target.get_expertise().hp > 0:
                result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, attacker, target, 0, 1, self._is_ally(target))]
                for item in target_equipment.get_all_equipped_items():
                    other_item_effects = item.get_item_effects()
                    if other_item_effects is None:
                        continue
                    for item_effect in other_item_effects.on_damaged:
                        _, result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, attacker, 1, actual_damage_dealt, item.get_full_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

            attacker.get_stats().dueling.damage_dealt += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt + piercing_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt + final_piercing_dmg - piercing_damage_dealt

            dmg_reflect: float = 0
            for se in target_dueling.status_effects:
                if se.key == StatusEffectKey.AttrBuffOnDamage:
                    assert(isinstance(se, AttrBuffOnDamage))
                    target_dueling.status_effects += list(map(lambda s: s.set_trigger_first_turn(target != attacker), se.on_being_hit_buffs))
                    result_strs.append(f"{target_name} gained {se.get_buffs_str()}")
                elif se.key == StatusEffectKey.DmgReflect:
                    dmg_reflect += se.value
            
            for effect in target.get_combined_req_met_effects().permanent:
                if effect.effect_type == EffectType.DmgReflect:
                    dmg_reflect += effect.effect_value

            if dmg_reflect > 0:
                reflected_damage: int = ceil(damage * dmg_reflect)
                attacker_dmg_reduct = attacker.get_dueling().get_total_percent_dmg_reduct(attacker.get_combined_req_met_effects())

                attacker_org_armor = attacker.get_dueling().armor
                actual_reflected_damage = attacker.get_expertise().damage(reflected_damage, attacker.get_dueling(), attacker_dmg_reduct, ignore_armor=False)
                attacker_cur_armor = attacker.get_dueling().armor
                
                attacker_dmg_reduct_str = f" ({abs(attacker_dmg_reduct) * 100}% {'Reduction' if attacker_dmg_reduct > 0 else 'Increase'})" if attacker_dmg_reduct != 0 else ""
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
            percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
            armor_str = f" ({target_dueling.armor - org_armor} Armor)" if target_dueling.armor - org_armor < 0 else ""
            piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

            result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}{generating_string}")
        
            attacker.get_stats().dueling.attacks_done += 1
        
        if cursed_coins_damage != 0:
            if attacker in self._enemies:
                for other in self._allies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct(other.get_combined_req_met_effects())
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")
            elif attacker in self._allies:
                for other in self._enemies:
                    org_armor = other.get_dueling().armor
                    percent_dmg_reduct = other.get_dueling().get_total_percent_dmg_reduct(other.get_combined_req_met_effects())
                    actual_cc_damage = other.get_expertise().damage(cursed_coins_damage, other.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    armor_str = f" ({other.get_dueling().armor - org_armor} Armor)" if other.get_dueling().armor - org_armor < 0 else ""

                    attacker.get_stats().dueling.damage_dealt += actual_cc_damage
                    other.get_stats().dueling.damage_taken += actual_cc_damage

                    result_strs.append(f"{attacker_name} dealt {actual_cc_damage}{armor_str} damage to {self.get_name(other)} using Cursed Coins")

        if splash_dmg > 0 or splash_percent_dmg > 0:
            if attacker in self._enemies:
                for target in self._allies:
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt} splash damage to {self.get_name(target)}")
            else:
                for target in self._enemies:
                    percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct(target.get_combined_req_met_effects())
                    damage_dealt = target.get_expertise().damage(splash_dmg + splash_percent_dmg, target.get_dueling(), percent_dmg_reduct, ignore_armor=False)

                    attacker.get_stats().dueling.damage_dealt += damage_dealt
                    target.get_stats().dueling.damage_taken += damage_dealt

                    result_strs.append(f"{attacker_name} dealt {damage_dealt} splash damage to {self.get_name(target)}")

        return "\n".join(result_strs)

    def use_ability_on_selected_targets(self):
        assert(self._selected_ability is not None)

        caster = self._turn_order[self._turn_index]

        # Avoid the player targeting and getting multiple triggers on enemies that are already dead -- this should
        # only be relevant for abilities that target all enemies or everyone, since the abilities that ask you to
        # select targets already filter out dead enemies
        if not self._selected_ability.get_target_own_group():
            self._selected_targets = list(filter(lambda entity: entity.get_expertise().hp > 0, self._selected_targets))

        names = [self.get_name(caster), *list(map(lambda x: self.get_name(x), self._selected_targets))]
        result_str = self._selected_ability.use_ability(caster, self._selected_targets) # type: ignore

        self._selected_ability.set_turn_after_lapsed(False)

        caster.get_stats().dueling.abilities_used += 1
        xp_str: str = ""

        return result_str.format(*names) + xp_str

    def use_item_on_selected_targets(self):
        assert(self._selected_item is not None)

        applicator = self._turn_order[self._turn_index]
        applicator_dueling = applicator.get_dueling()
        applicator_name = self.get_name(applicator)

        potion_effect_mod: float = 1.0
        if ClassTag.Consumable.Potion in self._selected_item.get_class_tags():
            for se in applicator.get_dueling().status_effects:
                if se.key == StatusEffectKey.PotionBuff:
                    potion_effect_mod += se.value
            for item in applicator.get_equipment().get_all_equipped_items():
                for item_effect in item.get_item_effects().permanent:
                    if item_effect.effect_type == EffectType.PotionMod:
                        potion_effect_mod += item_effect.effect_value

        result_strs = []
        for target in self._selected_targets:
            target_name = self.get_name(target)
            result_strs += [s.format(target_name, applicator_name) for s in target.get_dueling().apply_chance_status_effect_from_item(ItemEffectCategory.Permanent, self._selected_item, target, applicator, 0, 1, self._is_ally(target), potion_effect_mod)]
            item_effects = self._selected_item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    result_str = applicator_dueling.apply_consumable_item_effect(self._selected_item, effect, applicator, target, potion_effect_mod)
                    result_strs.append(result_str.format(applicator_name, self.get_name(target)))

        applicator.get_inventory().remove_item(self._selected_item_index, 1)
        applicator.get_stats().dueling.items_used += 1
        
        return "\n".join(result_strs)

    def set_targets_remaining_based_on_weapon(self):
        cur_entity: NPC = self._turn_order[self._turn_index]
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
        cur_entity: NPC = self._turn_order[self._turn_index]

        # Check here before setting next turn, just in case
        duel_result = self.check_for_win()
        if duel_result.game_won:
            self.get_victory_screen(duel_result)
            return False

        dueling: Dueling = cur_entity.get_dueling()
        dueling.actions_remaining = max(0, dueling.actions_remaining - 1)
        if dueling.actions_remaining == 0 or skip_turn:
            init_info_str: str = ""

            is_charmed = any(se.key == StatusEffectKey.Charmed for se in cur_entity.get_dueling().status_effects)
            if dueling.actions_remaining > 0 and skip_turn and is_charmed:
                damage = ceil(0.5 * cur_entity.get_expertise().max_hp)
                cur_entity.get_expertise().damage(damage, cur_entity.get_dueling(), 0, True)
                init_info_str += f"{self.get_name(cur_entity)} took {damage} damage for skipping their turn while Charmed!\n\n"

            # CDs and status effect time remaining decrement at the end of the turn,
            # so they actually last a turn
            dueling.decrement_all_ability_cds()
            dueling.decrement_statuses_time_remaining()
            cur_entity.get_expertise().update_stats(cur_entity.get_combined_attributes())
            duel_result = self.set_next_turn(init_info_str)
            if duel_result.game_won:
                self.get_victory_screen(duel_result)
                return False
        
        next_entity: NPC = self._turn_order[self._turn_index]
        if next_entity != cur_entity:
            next_entity_dueling: Dueling = next_entity.get_dueling()
            next_entity_dueling.actions_remaining = next_entity_dueling.init_actions_remaining

        return True
        
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

        selected_targets: List[NPC] = []

        def update_optimal_fitness(fitness_score: float, intent: Intent, ability: Ability | None, ability_index: int, item: Item | None, item_index: int, targets: List[NPC]):
            nonlocal optimal_fitness_score, chosen_action, selected_ability, selected_ability_index, selected_item, selected_item_index, selected_targets

            if optimal_fitness_score is None or fitness_score > optimal_fitness_score:
                optimal_fitness_score = fitness_score
                chosen_action = intent
                
                selected_ability = ability
                selected_ability_index = ability_index

                selected_item = item
                selected_item_index = item_index

                selected_targets = targets

        def get_target_ids(targets: List[NPC], cannot_target_ids: List[str], is_targeting_own_group: bool):
            # To allow healing abilities and buffs to target your own group, even if they're not alive, but not continue
            # to damage dead enemies, this conditionally filters based on whether the NPC is targeting its own group
            alive_targets = filter(lambda x: x.get_expertise().hp > 0, targets) if not is_targeting_own_group else targets
            target_ids = map(lambda x: x.get_id(), alive_targets)
            return list(filter(lambda x: x != "" and x not in cannot_target_ids, target_ids))

        restricted_to_items: bool = any(se.key == StatusEffectKey.RestrictedToItems for se in npc_dueling.status_effects)
        cannot_attack: bool = any(se.key == StatusEffectKey.CannotAttack for se in npc_dueling.status_effects)
        taunt_targets: List[NPC] = [se.forced_to_attack for se in npc_dueling.status_effects if isinstance(se, Taunted)]  # type: ignore

        cannot_use_abilities: bool = any(se.key == StatusEffectKey.CannotUseAbilities for se in npc_dueling.status_effects) or len(taunt_targets) > 0
        cannot_use_items: bool = len(taunt_targets) > 0

        charmed: bool = any(se.key == StatusEffectKey.Charmed for se in npc_dueling.status_effects)

        enemies = self._allies if ((cur_npc in self._enemies and not charmed) or (cur_npc in self._allies and charmed)) else self._enemies

        cannot_target_ids: List[str] = []
        for se in npc_dueling.status_effects:
            if se.key == StatusEffectKey.CannotTarget:
                assert(isinstance(se, CannotTarget))
                if se.cant_target in enemies:
                    cannot_target_ids.append(se.cant_target.get_id())

        if all(enemy.get_id() in cannot_target_ids for enemy in enemies):
            if self._logger is not None:
                additional_info_str = f"{self._additional_info_string_data}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if self._additional_info_string_data != "" else "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆"
                self._logger.log(level=logging.INFO, msg=f"{cur_npc.get_name()} skips their turn!: {cur_npc.get_name()} had no available targets!\n\n{additional_info_str}")

            return self.continue_turn()

        # Step 1: Try attacking all enemies
        if not restricted_to_items:
            if not cannot_attack:
                self.set_targets_remaining_based_on_weapon()

                if self._targets_remaining == 0:
                    # Who knows, maybe I'll make something that can attack itself.
                    dueling_copy: SimulationDuel = self.create_copy()
                    dueling_copy._selected_targets = [dueling_copy._turn_order[dueling_copy._turn_index]]
                    dueling_copy.attack_selected_targets()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                    update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, [cur_npc])
                elif self._targets_remaining < 0:
                    dueling_copy: SimulationDuel = self.create_copy()

                    targets = []
                    if self._targets_remaining == -1:
                        targets = enemies
                    elif self._targets_remaining == -2:
                        targets = self._turn_order
                    
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)

                    if len(target_ids) > 0:
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.attack_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore
                        
                        update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, enemies)
                else:
                    if len(taunt_targets) > 0:
                        targets = [choice(taunt_targets)]
                        dueling_copy: SimulationDuel = self.create_copy()
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.attack_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                        update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))
                    elif len(enemies) > 0:
                        combinations = list(itertools.combinations(enemies, min(self._targets_remaining, len(enemies))))
                        for targets in combinations:
                            dueling_copy: SimulationDuel = self.create_copy()
                            
                            target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, False)
                            if len(target_ids) == 0:
                                continue

                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.attack_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                            update_optimal_fitness(fitness_score, Intent.Attack, None, -1, None, -1, list(targets))

            if not cannot_use_abilities:
                # Step 2: Try using all abilities
                for i, ability in enumerate(npc_dueling.abilities + npc_dueling.temp_abilities):
                    if cur_npc.get_expertise().mana < ability.get_mana_cost() or ability.get_cur_cooldown() != 0:
                        continue

                    # Special casing for the Underworld final boss, so it doesn't waste its main ability
                    if ability.get_name() == "Annihilation Beam":
                        can_use = any(se.key == StatusEffectKey.Marked and se.source_str == "\uD83D\uDD3B Ruby Eyes Begin to Glow" for en in self._enemies for se in en.get_dueling().status_effects)
                        if not can_use:
                            continue

                    self._targets_remaining = ability.get_num_targets()

                    if self._targets_remaining < 0:
                        dueling_copy: SimulationDuel = self.create_copy()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                        dueling_copy._selected_ability_index = i

                        targets = []
                        target_own_group = dueling_copy._selected_ability.get_target_own_group()
                        if self._targets_remaining == -1:
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
                        
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)

                        if len(target_ids) > 0:
                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.use_ability_on_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                            update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    elif self._targets_remaining == 0:
                        dueling_copy: SimulationDuel = self.create_copy()

                        copy_cur_npc = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0]
                        dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                        dueling_copy._selected_ability_index = i

                        targets = [cur_npc]
                        target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, True)
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_ability_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                        update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, targets)
                    else:
                        targets = []
                        target_own_group = ability.get_target_own_group()
                        if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                            if not charmed:
                                targets = [entity for entity in self._enemies if entity.get_id() != cur_npc.get_id()]
                            else:
                                targets = [entity for entity in self._allies if entity.get_id() != cur_npc.get_id()]
                        elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                            if not charmed:
                                targets = [entity for entity in self._allies if entity.get_id() != cur_npc.get_id()]
                            else:
                                targets = [entity for entity in self._enemies if entity.get_id() != cur_npc.get_id()]

                        if len(targets) > 0:
                            combinations = list(itertools.combinations(targets, min(self._targets_remaining, len(enemies))))
                            for targets in combinations:
                                dueling_copy: SimulationDuel = self.create_copy()

                                copy_cur_npc = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0]
                                dueling_copy._selected_ability = (copy_cur_npc.get_dueling().abilities + copy_cur_npc.get_dueling().temp_abilities)[i]
                                dueling_copy._selected_ability_index = i

                                target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)
                                if len(target_ids) == 0:
                                    continue

                                dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                                dueling_copy.use_ability_on_selected_targets()

                                copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                                dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                                dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                                fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                                update_optimal_fitness(fitness_score, Intent.Ability, ability, i, None, -1, list(targets))

        if not cannot_use_items:
            # Step 3: Try using all items
            inventory_slots = npc_inventory.get_inventory_slots()
            filtered_indices = npc_inventory.filter_inventory_slots([ClassTag.Consumable.UsableWithinDuels]) # type: ignore
            filtered_items = [inventory_slots[i] for i in filtered_indices]
            for i, item in enumerate(filtered_items):
                consumable_stats = item.get_consumable_stats()
                if consumable_stats is None:
                    continue
                
                self._targets_remaining = consumable_stats.get_num_targets()

                if self._targets_remaining < 0:
                    dueling_copy: SimulationDuel = self.create_copy()

                    npc_in_copy = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0]
                    dueling_copy._selected_item = npc_in_copy.get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = []
                    target_own_group = consumable_stats.get_target_own_group()
                    if self._targets_remaining == -1:
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
                        
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)

                    if len(target_ids) > 0:
                        dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                        dueling_copy.use_item_on_selected_targets()

                        copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                        dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                        dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                        fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                        update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                elif self._targets_remaining == 0:
                    dueling_copy: SimulationDuel = self.create_copy()

                    npc_in_copy = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0]
                    dueling_copy._selected_item = npc_in_copy.get_inventory().get_inventory_slots()[i]
                    dueling_copy._selected_item_index = i

                    targets = [cur_npc]
                    target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, True)
                    dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                    dueling_copy.use_item_on_selected_targets()

                    copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                    dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                    dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                    fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore

                    update_optimal_fitness(fitness_score, Intent.Item, None, -1, item, i, targets)
                else:
                    targets = []
                    target_own_group = consumable_stats.get_target_own_group()
                    if (cur_npc in self._enemies and target_own_group) or (cur_npc in self._allies and not target_own_group):
                        if not charmed:
                            targets = [entity for entity in self._enemies if entity.get_id() != cur_npc.get_id()]
                        else:
                            targets = [entity for entity in self._allies if entity.get_id() != cur_npc.get_id()]
                    elif (cur_npc in self._enemies and not target_own_group) or (cur_npc in self._allies and target_own_group):
                        if not charmed:
                            targets = [entity for entity in self._allies if entity.get_id() != cur_npc.get_id()]
                        else:
                            targets = [entity for entity in self._enemies if entity.get_id() != cur_npc.get_id()]

                    if len(targets) > 0:
                        combinations = list(itertools.combinations(enemies, min(self._targets_remaining, len(enemies))))
                        for targets in combinations:
                            dueling_copy: SimulationDuel = self.create_copy()

                            npc_in_copy = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0]
                            dueling_copy._selected_item = npc_in_copy.get_inventory().get_inventory_slots()[i]
                            dueling_copy._selected_item_index = i

                            target_ids: List[str] = get_target_ids(list(targets), cannot_target_ids, target_own_group)
                            if len(target_ids) == 0:
                                continue

                            dueling_copy._selected_targets = dueling_copy.get_entities_by_ids(target_ids)
                            dueling_copy.use_item_on_selected_targets()

                            copy_cur_npc: NPC = dueling_copy.get_entities_by_ids([cur_npc.get_id()])[0] # type: ignore
                            dueling_copy_allies = dueling_copy._allies if copy_cur_npc in dueling_copy._allies else dueling_copy._enemies
                            dueling_copy_enemies = dueling_copy._enemies if copy_cur_npc in dueling_copy._allies else dueling_copy._allies
                            fitness_score = copy_cur_npc.get_fitness_for_persona(cur_npc, dueling_copy_allies, dueling_copy_enemies) # type: ignore
                            
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

        additional_info_str = f"{self._additional_info_string_data}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if self._additional_info_string_data != "" else ""
        
        if self._logger is not None:
            self._logger.log(level=logging.INFO, msg=f"{cur_npc.get_name()} {action_str}: {additional_info_str}{optimal_result_str}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆")

        return self.continue_turn()

    def create_copy(self):
        copied_allies: List[NPC] = jsonpickle.decode(jsonpickle.encode(self._allies, make_refs=False)) # type: ignore
        copied_enemies: List[NPC] = jsonpickle.decode(jsonpickle.encode(self._enemies, make_refs=False)) # type: ignore

        duel_view: SimulationDuel = SimulationDuel(
            copied_allies,
            copied_enemies,
            None,
            self._MAX_TURNS,
            skip_init_updates=True
        )

        duel_view._turn_index = self._turn_index

        return duel_view