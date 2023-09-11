from __future__ import annotations

import random

from math import ceil
from uuid import uuid4

from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.inventory import Inventory
from features.npcs.npc import NPC, NPCDuelingPersonas, NPCRoles
from features.shared.ability import Ability
from features.shared.constants import BLEED_PERCENT_HP, DEX_DODGE_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE
from features.shared.effect import EffectType, ItemEffectCategory
from features.shared.enums import ClassTag
from features.shared.item import LOADED_ITEMS, ItemKey, WeaponStats
from features.shared.statuseffect import AttrBuffOnDamage, Bleeding, DmgReflect, StackingDamage, StatusEffectKey
from features.stats import Stats

from typing import Dict, List, TYPE_CHECKING
if TYPE_CHECKING:
    from features.player import Player
    from features.shared.ability import NegativeAbilityResult

# -----------------------------------------------------------------------------
# ABILITIES
# -----------------------------------------------------------------------------

class Pierce(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Pierce",
            class_key=ExpertiseClass.Guardian,
            description="Deal your max weapon damage to an enemy and cause Bleeding for 5 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=1,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        main_hand_item = targets[0].get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        damage = 1 if main_hand_item is None else main_hand_item.get_weapon_stats().get_max_damage() # type: ignore

        debuff = Bleeding(
            turns_remaining=5,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(damage, damage), [debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Parry(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2694\uFE0F",
            name="Parry",
            class_key=ExpertiseClass.Guardian,
            description="Gain 75% damage reflection for 4 turns.",
            flavor_text="",
            mana_cost=0,
            cooldown=6,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        buff = DmgReflect(
            turns_remaining=4,
            value=0.75,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [buff])
        result_str += "\n".join(results)

        caster.get_stats().dueling.guardian_abilities_used += 1

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class Onslaught(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE1\uFE0F",
            name="Onslaught",
            class_key=ExpertiseClass.Guardian,
            description="Attack an enemy 5 times.",
            flavor_text="",
            mana_cost=0,
            cooldown=4,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=0,
            scaling=[]
        )

    def use_ability(self, caster: Player | NPC, targets: List[Player | NPC]) -> str:
        attacker = caster
        attacker_name = caster.get_name() # type: ignore
        attacker_attrs = attacker.get_combined_attributes()
        attacker_equipment = attacker.get_equipment()

        dmg_buff_effect_totals: Dict[EffectType, float] = attacker_equipment.get_dmg_buff_effect_totals(attacker)
        critical_hit_dmg_buff: float = min(max(dmg_buff_effect_totals[EffectType.CritDmgBuff] - dmg_buff_effect_totals[EffectType.CritDmgReduction], 1), 0)
        self_hp_dmg_buff: int = ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfMaxHealth] * attacker.get_expertise().max_hp) + ceil(dmg_buff_effect_totals[EffectType.DmgBuffSelfRemainingHealth] * attacker.get_expertise().hp)

        bonus_damage: int = 0
        bonus_percent_damage: float = 1 + dmg_buff_effect_totals[EffectType.DmgBuff]
        for se in attacker.get_dueling().status_effects:
            if se.key == StatusEffectKey.BonusDamageOnAttack:
                bonus_damage += int(se.value)
            elif se.key == StatusEffectKey.DmgBuff:
                bonus_percent_damage += se.value
            elif se.key == StatusEffectKey.DmgDebuff:
                bonus_percent_damage -= se.value

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
                    elif item_effect.effect_type == EffectType.SplashPercentMaxDmg and weapon_stats is not None:
                        splash_percent_dmg += ceil(weapon_stats.get_max_damage() * item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.PiercingDmg:
                        piercing_dmg += int(item_effect.effect_value)
                    elif item_effect.effect_type == EffectType.PiercingPercentDmg:
                        piercing_percent_dmg = min(piercing_percent_dmg + item_effect.effect_value, 1)

        result_strs = [f"{attacker_name} attacked using {main_hand_item.get_full_name() if main_hand_item is not None else 'a good slap'}!\n"]
        for _ in range(5):
            for i, target in enumerate(targets):
                target_expertise = target.get_expertise()
                target_equipment = target.get_equipment()
                target_dueling = target.get_dueling()
                target_attrs = target.get_combined_attributes()

                target_name = "{" + f"{i + 1}" + "}"
                target_dodged = random.random() < target_attrs.dexterity * DEX_DODGE_SCALE
                
                if target_dodged:
                    target.get_stats().dueling.attacks_dodged += 1
                    result_strs.append(f"{target_name} dodged the attack")
                    continue

                critical_hit_boost = LUCK_CRIT_DMG_BOOST if random.random() < attacker_attrs.luck * LUCK_CRIT_SCALE else 1

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
                result_strs += [s.format(target_name, attacker_name) for s in attacker.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnSuccessfulAttack, target, attacker, 0, 1, False)]

                for item in attacker_equipment.get_all_equipped_items():
                    other_item_effects = item.get_item_effects()
                    if other_item_effects is None:
                        continue
                    for item_effect in other_item_effects.on_successful_attack:
                        damage, result_str = attacker.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, attacker, target, 1, damage, item.get_full_name())
                        if result_str != "":
                            result_strs.append(result_str.format(attacker_name, target_name))

                result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnAttacked, attacker, target, 0, 1, False)]

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
                    result_strs += [s.format(attacker_name, target_name) for s in target.get_dueling().apply_chance_status_effect_from_total_item_effects(ItemEffectCategory.OnDamaged, attacker, target, 0, 1, False)]
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

                critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
                percent_dmg_reduct_str = f" ({abs(percent_dmg_reduct) * 100}% {'Reduction' if percent_dmg_reduct > 0 else 'Increase'})" if percent_dmg_reduct != 0 else ""
                armor_str = f" ({target_dueling.armor - org_armor} Armor)" if target_dueling.armor - org_armor < 0 else ""
                piercing_str = f" ({piercing_damage_dealt} Piercing)" if piercing_damage_dealt > 0 else ""

                result_strs.append(f"{attacker_name} dealt {actual_damage_dealt}{piercing_str}{armor_str}{percent_dmg_reduct_str}{critical_hit_str} damage to {target_name}")
            
                attacker.get_stats().dueling.attacks_done += 1

        return "{0}" + f" used {self.get_icon_and_name()}!\n\n" + "\n".join(result_strs)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class AssailingTombGuardian(NPC):
    def __init__(self, name_suffix: str=""):
        # Balance Simulation Results:
        # 13% chance of 4 player party (Lvl. 80-90) victory against 1 + Defending Tomb Guardian
        # Avg Number of Turns (per entity): 22

        super().__init__("Assailing Tomb Guardian" + name_suffix, NPCRoles.DungeonEnemy, NPCDuelingPersonas.Bruiser, {})

        self._setup_npc_params()

    def _setup_inventory(self):
        if self._inventory is None:
            self._inventory = Inventory()

    def _setup_xp(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()
        
        self._expertise.add_xp_to_class_until_level(200, ExpertiseClass.Guardian)
        self._expertise.constitution = 97
        self._expertise.strength = 50
        self._expertise.dexterity = 50
        self._expertise.intelligence = 0
        self._expertise.luck = 0
        self._expertise.memory = 3

    def _setup_equipment(self):
        if self._expertise is None:
            self._expertise = Expertise()
        if self._equipment is None:
            self._equipment = Equipment()

        self._equipment.equip_item_to_slot(ClassTag.Equipment.MainHand, LOADED_ITEMS.get_new_item(ItemKey.StoneLance))
        self._equipment.equip_item_to_slot(ClassTag.Equipment.ChestArmor, LOADED_ITEMS.get_new_item(ItemKey.StoneForm))

        self._expertise.update_stats(self.get_combined_attributes())

    def _setup_abilities(self):
        if self._dueling is None:
            self._dueling = Dueling()
        
        self._dueling.abilities = [Pierce(), Parry(), Onslaught()]

    def _setup_npc_params(self):
        self._setup_inventory()
        self._setup_equipment()
        self._setup_xp()
        self._setup_abilities()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._id = state.get("_id", str(uuid4()))
        self._name = "Assailing Tomb Guardian"
        self._role = NPCRoles.DungeonEnemy
        self._dueling_persona = NPCDuelingPersonas.Bruiser
        self._dueling_rewards = {}
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()
            self._setup_inventory()

        self._equipment: Equipment | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()
            self._setup_equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()
            self._setup_xp()

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()
            self._setup_abilities()

        self._stats: Stats | None = state.get("_stats")
        if self._stats is None:
            self._stats = Stats()
