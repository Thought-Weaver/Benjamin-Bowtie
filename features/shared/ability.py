from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from math import ceil
from random import randint, random

from typing import List, TYPE_CHECKING
from features.dueling import Dueling
from features.equipment import Equipment

from features.expertise import ExpertiseClass
from features.shared.constants import DEX_DODGE_SCALE, INT_DMG_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, STR_DMG_SCALE
from features.shared.effect import EffectType
from features.shared.enums import ClassTag
from features.shared.item import WeaponStats
from features.shared.statuseffect import *

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
    def __init__(self, icon: str, name: str, class_key: ExpertiseClass, description: str, flavor_text: str, mana_cost: int, cooldown: int, num_targets: int, level_requirement: int, target_own_group: bool, purchase_cost: int):
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

        # Turns remaining until it can be used again
        # If this is -1, then it's a once-per-duel ability that's already been used
        self._cur_cooldown = 0

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

    def reset_cd(self):
        self._cur_cooldown = 0

    def decrement_cd(self):
        if self._cur_cooldown != -1:
            self._cur_cooldown = max(0, self._cur_cooldown - 1)

    @abstractmethod
    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        pass

    def remove_mana_and_set_cd(self, caster: Player | NPC):
        mana_to_blood_percent = 0
        for se in caster.get_dueling().status_effects:
            if se.key == StatusEffectKey.ManaToHP:
                mana_to_blood_percent = se.value
                break

        mana_cost_adjustment = 0
        cd_adjustment = 0
        for item in caster.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    if effect.effect_type == EffectType.AdjustedManaCosts:
                        mana_cost_adjustment = max(mana_cost_adjustment + effect.effect_value, -1)
                    if effect.effect_type == EffectType.AdjustedCDs:
                        cd_adjustment += int(effect.effect_value)
        
        final_mana_cost = self.get_mana_cost() + int(self.get_mana_cost() * mana_cost_adjustment)
        if mana_to_blood_percent == 0:
            caster.get_expertise().remove_mana(final_mana_cost)
        else:
            damage = int(mana_to_blood_percent * final_mana_cost)
            if damage > 0:
                caster.get_expertise().damage(damage, 0, 0, caster.get_equipment())
                return f"You took {damage} damage to cast this from Contract: Mana to Blood"
            
        if self._cooldown >= 0:
            self._cur_cooldown = max(self._cooldown + cd_adjustment, 0)
        else:
            # Can't adjust -1 time cooldowns
            self._cur_cooldown = self._cooldown

    def _use_damage_ability(self, caster: Player, targets: List[Player | NPC], dmg_range: range) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(dmg_range.start, dmg_range.stop)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    damage, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, damage)
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            if actual_damage_dealt > 0:
                for item in target_equipment.get_all_equipped_items():
                    item_effects = item.get_item_effects()
                    if item_effects is None:
                        continue
                    for item_effect in item_effects.on_damaged:
                        result_str = target.get_dueling().apply_on_attacked_or_damaged_effects(item, item_effect, target, caster, i + 1, actual_damage_dealt)
                        if result_str != "":
                            results.append(NegativeAbilityResult(result_str, False))

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))

        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        return results

    def _use_negative_status_effect_ability(self, caster: Player, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    _, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, 0)
                    if result_str != "":
                        results.append(NegativeAbilityResult(result_str, False))

            target.get_dueling().status_effects += list(map(lambda se: se.set_trigger_first_turn(target != caster), status_effects))
            target.get_expertise().update_stats(target.get_combined_attributes())

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" is now {status_effects_str}", False))
        
        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(NegativeAbilityResult(result_str, False))

        return results

    def _use_damage_and_effect_ability(self, caster: Player, targets: List[Player | NPC], dmg_range: range, status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results = self._use_damage_ability(caster, targets, dmg_range)
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects += list(map(lambda se: se.set_trigger_first_turn(targets[i] != caster), status_effects))
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
                results[i].target_str += f" and is now {status_effects_str}"
        
        return results

    def _use_positive_status_effect_ability(self, caster: Player, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[str]:
        results: List[str] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is None:
                    continue
                for item_effect in item_effects.on_successful_ability_used:
                    _, result_str = caster.get_dueling().apply_on_successful_attack_or_ability_effects(item, item_effect, caster, target, i + 1, 0)
                    if result_str != "":
                        results.append(result_str)

            target.get_dueling().status_effects += list(map(lambda se: se.set_trigger_first_turn(target != caster), status_effects))
            target.get_expertise().update_stats(target.get_combined_attributes())
            results.append("{" + f"{i + 1}" + "}" + f" is now {status_effects_str}")
        
        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(result_str)

        return results

    def _use_heal_ability(self, caster: Player, targets: List[Player | NPC], heal_range: range) -> List[str]:
        results: List[str] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        healing_adjustment = 0
        for item in caster.get_equipment().get_all_equipped_items():
            item_effects = item.get_item_effects()
            if item_effects is not None:
                for effect in item_effects.permanent:
                    if effect.effect_type == EffectType.HealingAbilityBuff:
                        healing_adjustment = max(healing_adjustment + effect.effect_value, -1)

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()

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
            heal_amount = int(base_heal * critical_hit_final)
            heal_amount += int(heal_amount * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            heal_amount += int(heal_amount * healing_adjustment)

            target_expertise.heal(heal_amount)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"

            results.append("{" + f"{i + 1}" + "}" + f" was healed for {heal_amount}{critical_hit_str} HP")
        
        result_str = self.remove_mana_and_set_cd(caster)
        if result_str is not None:
            results.append(result_str)

        return results

    def __str__(self):
        target_str: str = ""
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

        return (
            f"{self._icon} **{self._name}**\n"
            f"{self._mana_cost} Mana / {target_str} / {cooldown_str}\n\n"
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
            description="Summon a rush of water that deals 1-3 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=2,
            target_own_group=False,
            purchase_cost=50
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 3))
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
            description="Summon a rush of water that deals 2-5 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4,
            target_own_group=False,
            purchase_cost=100
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 5))
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
            description="Summon a rush of water that deals 3-6 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=6,
            target_own_group=False,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 6))
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
            description="Summon a rush of water that deals 4-7 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=8,
            target_own_group=False,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 7))
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
            description="Summon a rush of water that deals 5-8 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=10,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 8))
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
            description="Curse an enemy to lose -1 Constitution, -1 Strength, and -1 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=5,
            target_own_group=False,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-1,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-1,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
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
            description="Curse an enemy to lose -2 Constitution, -2 Strength, and -2 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-2,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-2,
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
            description="Curse an enemy to lose -3 Constitution, -3 Strength, and -3 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=13,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-3,
            source_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
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
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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

# -----------------------------------------------------------------------------
# WRATH OF THE WAVES
# -----------------------------------------------------------------------------

class WrathOfTheWavesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves I",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 5-10 damage each. They take 50% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=10,
            target_own_group=False,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.5 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            damage = int(randint(5, 10) * bonus_dmg_boost * critical_hit_boost)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 6-12 damage each. They take 80% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.8 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            damage = int(randint(6, 12) * bonus_dmg_boost * critical_hit_boost)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 10-15 damage each. They take 110% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=14,
            target_own_group=False,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 2.1 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            damage = int(randint(10, 15) * bonus_dmg_boost * critical_hit_boost)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            cooldown=2,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Raise a protective wall of water, reducing all damage you take next turn by 35%.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=0,
            level_requirement=15,
            target_own_group=True,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.35,
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
            description="Raise a protective wall of water, reducing all damage you take next turn by 45%.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=3200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            cooldown=1,
            num_targets=2,
            level_requirement=14,
            target_own_group=False,
            purchase_cost=500
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(10, 15)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Conjure a raging current against up to 2 enemies, dealing 12-18 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=2,
            level_requirement=16,
            target_own_group=False,
            purchase_cost=1000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(12, 18)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Conjure a raging current against up to 2 enemies, dealing 15-20 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=2,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=2000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(15, 20)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Drag up to 3 enemies into the depths, dealing each (1 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((1 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            actual_damage_dealt = target_expertise.damage(damage, 0, 0, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Drag up to 3 enemies into the depths, dealing each (1.5 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((1.5 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            actual_damage_dealt = target_expertise.damage(damage, 0, 0, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Drag up to 3 enemies into the depths, dealing each (2 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=4800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((2 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)

            actual_damage_dealt = target_expertise.damage(damage, 0, 0, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

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
            description="Summon a vortex that deals 10-20 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=1000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_dueling = target.get_dueling()
            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(10, 20)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
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
            description="Summon a vortex that deals 15-25 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_dueling = target.get_dueling()
            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(10, 15)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
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
            description="Summon a vortex that deals 20-30 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=4000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_attrs = caster.get_combined_attributes()
        caster_equipment = caster.get_equipment()

        for i, target in enumerate(targets):
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                target.get_stats().dueling.abilities_dodged += 1
                results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + " dodged the ability.", True))
                continue

            target_dueling = target.get_dueling()
            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            critical_hit_dmg_buff = 0
            for item in caster_equipment.get_all_equipped_items():
                item_effects = item.get_item_effects()
                if item_effects is not None:
                    for item_effect in item_effects.permanent:
                        if not item_effect.meets_conditions(caster, item):
                            continue

                        if item_effect.effect_type == EffectType.CritDmgBuff:
                            critical_hit_dmg_buff = min(int(critical_hit_dmg_buff + item_effect.effect_value), 1)
                        if item_effect.effect_type == EffectType.CritDmgReduction:
                            critical_hit_dmg_buff = max(int(critical_hit_dmg_buff - item_effect.effect_value), 0)

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            if critical_hit_boost > 1:
                caster.get_stats().dueling.critical_hit_successes += 1

            critical_hit_final = max(critical_hit_boost + critical_hit_dmg_buff, 1) if critical_hit_boost > 1 else 1
            base_damage = randint(10, 15)
            damage = int(base_damage * critical_hit_final)
            damage += min(int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0)), damage)
            
            target_armor = target_equipment.get_total_reduced_armor(target_expertise.level)
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct, caster.get_equipment())

            caster.get_stats().dueling.damage_dealt += actual_damage_dealt
            target.get_stats().dueling.damage_taken += actual_damage_dealt
            target.get_stats().dueling.damage_blocked_or_reduced += damage - actual_damage_dealt

            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 1 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)" if percent_dmg_reduct != 0 else ""

            results.append(NegativeAbilityResult("{" + f"{i + 1}" + "}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        mana_and_cd_str = self.remove_mana_and_set_cd(caster)
        if mana_and_cd_str is not None:
            results.append(NegativeAbilityResult(mana_and_cd_str, False))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
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
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 15% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=5000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.15,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
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
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 25% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=10000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.25,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
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
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 35% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=20000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.35,
            source_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
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
            cooldown=3,
            num_targets=-1,
            level_requirement=2,
            target_own_group=False,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = ceil(base_damage * 0.5)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            cooldown=3,
            num_targets=-1,
            level_requirement=5,
            target_own_group=False,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = ceil(base_damage * 0.6)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            cooldown=3,
            num_targets=-1,
            level_requirement=8,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = ceil(base_damage * 0.7)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            purchase_cost=300
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Restore 50% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.5)

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
            description="Restore 75% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=13,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        heal_amount = ceil((caster.get_expertise().max_hp - caster.get_expertise().hp) * 0.75)

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
            description="Prepare your attack, gaining +2 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=4,
            target_own_group=True,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=3,
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
            description="Prepare your attack, gaining +4 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=7,
            target_own_group=True,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=4,
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
            description="Prepare your attack, gaining +5 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=4,
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
            description="Whenever you're attacked over the next 3 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=5,
            target_own_group=True,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Whenever you're attacked over the next 6 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=15,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=2400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Strike back at an enemy dealing 75% of your weapon damage + 10% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=700
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(0.75 * base_damage + 0.1 * (caster_expertise.max_hp - caster_expertise.hp))
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            description="Strike back at an enemy dealing 80% of your weapon damage + 20% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=1400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(0.8 * base_damage + 0.2 * (caster_expertise.max_hp - caster_expertise.hp))
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            description="Strike back at an enemy dealing 85% of your weapon damage + 30% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=2800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(0.85 * base_damage + 0.3 * (caster_expertise.max_hp - caster_expertise.hp))
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            name="Taunt",
            class_key=ExpertiseClass.Guardian,
            description="Force an enemy to attack you next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=2500
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Lunge forward at an enemy, dealing 110% of your weapon damage with a 20% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=1000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(1.1 * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.2:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {bleed.name}"
                
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
            description="Lunge forward at an enemy, dealing 120% of your weapon damage with a 25% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=2000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(1.2 * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.25:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {bleed.name}"
                
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
            description="Lunge forward at an enemy, dealing 130% of your weapon damage with a 30% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=4000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int(1.3 * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.3:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {bleed.name}"
                
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
            description="Gain 2 actions this turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=8000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        # Adding one because actions_remaining are reduced when pressing Continue
        caster.get_dueling().actions_remaining += 3
        caster.get_stats().dueling.guardian_abilities_used += 1

        return "{0}" + f" used {self.get_icon_and_name()}!\n\nYou now have 2 actions available."

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
            description="Gain +200 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=20,
            target_own_group=True,
            purchase_cost=2000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=200,
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
            description="Gain +300 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=22,
            target_own_group=True,
            purchase_cost=4000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=300,
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
            description="Gain +400 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=24,
            target_own_group=True,
            purchase_cost=8000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=400,
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
            description="Power forward with your weapon, dealing 40% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=2500
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int((0.4 + 0.05 * caster_attrs.constitution) * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            description="Power forward with your weapon, dealing 60% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=24,
            target_own_group=False,
            purchase_cost=5000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int((0.6 + 0.05 * caster_attrs.constitution) * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            description="Power forward with your weapon, dealing 80% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=26,
            target_own_group=False,
            purchase_cost=10000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()

        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        unarmed_strength_bonus = int(caster_attrs.strength / 2)
        weapon_stats = WeaponStats(1 + unarmed_strength_bonus, 2 + unarmed_strength_bonus) if main_hand_item is None else main_hand_item.get_weapon_stats()
        item_effects = main_hand_item.get_item_effects() if main_hand_item is not None else None

        base_damage = weapon_stats.get_random_damage(caster_attrs, item_effects)
        damage = int((0.8 + 0.05 * caster_attrs.constitution) * base_damage)
        damage += min(int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0)), damage)

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
            description="Summon a binding contract, exchanging 50 coins for +1 Intelligence, +1 Strength, and +1 Dexterity until the end of the duel. If you can't pay, you instead receive -1 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=-1,
            num_targets=0,
            level_requirement=2,
            target_own_group=True,
            purchase_cost=50
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
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
            cooldown=-1,
            num_targets=0,
            level_requirement=6,
            target_own_group=True,
            purchase_cost=100
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Summon a binding contract, exchanging 50 coins for +5 Intelligence, +5 Strength, and +5 Dexterity until the end of the duel. If you can't pay, you instead receive -3 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=-1,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
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
            description="Gain +10 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=4,
            target_own_group=True,
            purchase_cost=100
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
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
            description="Gain +30 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=6,
            target_own_group=True,
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
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
            description="Gain +50 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
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
            purchase_cost=1000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Whenever you attack for the next 3 turns, part of the enemy struck turns into coins, awarding you 5 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=0,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=300
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=3,
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
            description="Whenever you attack for the next 3 turns, part of the enemy struck turns into coins, awarding you 10 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=3,
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
            description="Whenever you attack for the next 3 turns, part of the enemy struck turns into coin, awarding you 15 coins per successful attack.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=3,
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
            description="For the next 3 turns, whenever you gain coins, deal 0.25 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=10,
            target_own_group=True,
            purchase_cost=300
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.25,
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
            description="For the next 3 turns, whenever you gain coins, deal 0.5 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=12,
            target_own_group=True,
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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


class CursedCoinsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins III",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain coins, deal 0.75 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=14,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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

# -----------------------------------------------------------------------------
# UNSEEN RICHES
# -----------------------------------------------------------------------------

class UnseenRichesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches I",
            class_key=ExpertiseClass.Merchant,
            description="Gain coins equal to 0.25 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=11,
            target_own_group=True,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(int(0.25 * coins_to_add))
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

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
            description="Gain coins equal to 0.5 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=13,
            target_own_group=True,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(int(0.5 * coins_to_add))
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

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
            description="Gain coins equal to 0.75 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=15,
            target_own_group=True,
            purchase_cost=3200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(int(0.75 * coins_to_add))
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

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
            description="All of your abilities that use Mana instead take 70% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=14,
            target_own_group=True,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
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


class ContractManaToBloodII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood II",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 50% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=16,
            target_own_group=True,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
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


class ContractManaToBloodIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood III",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 30% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=0,
            level_requirement=18,
            target_own_group=True,
            purchase_cost=3200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
            value=0.3,
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
            description="Create a binding contract that exchanges 15% of your current health and deals 0.5 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=16,
            target_own_group=False,
            purchase_cost=1500
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(0.15 * 0.5 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            description="Create a binding contract that exchanges 10% of your current health and deals 1 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=18,
            target_own_group=False,
            purchase_cost=3000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(0.1 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            description="Create a binding contract that exchanges 5% of your current health and deals 3 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=6000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(3 * 0.05 * current_health)

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
            purchase_cost=8000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(100, int(0.01 * caster.get_inventory().get_coins()))

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
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=22,
            target_own_group=False,
            purchase_cost=16000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(150, int(0.01 * caster.get_inventory().get_coins()))

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
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=25,
            target_own_group=False,
            purchase_cost=32000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(200, int(0.01 * caster.get_inventory().get_coins()))

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
            purchase_cost=100
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(7, 9))
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
            purchase_cost=150
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=150
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=150
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Take 15% of your max health as damage and restore that much of an ally's health.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=5,
            target_own_group=True,
            purchase_cost=300
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.15)
        caster.get_expertise().damage(damage_amount, 0, 0, caster.get_equipment())

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
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
            description="Take 25% of your max health as damage and restore that much of an ally's health.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=8,
            target_own_group=True,
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.25)
        caster.get_expertise().damage(damage_amount, 0, 0, caster.get_equipment())

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
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
            description="Take 35% of your max health as damage and restore that much of an ally's health.",
            flavor_text="",
            mana_cost=10,
            cooldown=3,
            num_targets=1,
            level_requirement=11,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage_amount = ceil(caster.get_expertise().max_hp * 0.35)
        caster.get_expertise().damage(damage_amount, 0, 0, caster.get_equipment())

        heal_amount = damage_amount

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
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
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[str] = []
        for i, target in enumerate(targets):
            target.get_dueling().status_effects = []
            target.get_expertise().update_stats(target.get_combined_attributes())
            results.append("{" + f"{i + 1}" + "}" + f" has had their status effects removed")
        result_str += "\n".join(results)

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
            description="Create a miasma that deals 1-3 damage to all enemies with a 30% chance to Poison them for 1% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=-1,
            level_requirement=9,
            target_own_group=False,
            purchase_cost=400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(1, 3))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.3:
                targets[i].get_dueling().status_effects.append(poisoned)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {poisoned.name}"
        
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
            description="Create a miasma that deals 2-4 damage to all enemies with a 50% chance to Poison them for 1% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=-1,
            level_requirement=12,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.5:
                targets[i].get_dueling().status_effects.append(poisoned)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {poisoned.name}"
        
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
            description="Create a miasma that deals 3-5 damage to all enemies with a 70% chance to Poison them for 1% of their max health taken as damage every turn for the next 2 turns.",
            flavor_text="",
            mana_cost=5,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=1600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        poisoned = Poisoned(
            turns_remaining=2,
            value=POISONED_PERCENT_HP,
            source_str=self.get_icon_and_name()
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.7:
                targets[i].get_dueling().status_effects.append(poisoned)
                targets[i].get_expertise().update_stats(targets[i].get_combined_attributes())
            results[i].target_str += f" and is now {poisoned.name}"
        
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
            purchase_cost=600
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=2400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=2800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"

        results: List[str] = []
        for i, target in enumerate(targets):
            mana_to_restore: int = target.get_expertise().intelligence
            target.get_expertise().restore_mana(mana_to_restore)
            results.append("{" + f"{i + 1}" + "}" + f" regained {mana_to_restore} mana")
        result_str += "\n".join(results)

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
            mana_cost=15,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            mana_cost=15,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            mana_cost=15,
            cooldown=3,
            num_targets=-1,
            level_requirement=15,
            target_own_group=False,
            purchase_cost=800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            purchase_cost=3000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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
            description="Choose up to 3 allies. For the next 2 turns, they regain 5% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=3,
            num_targets=3,
            level_requirement=19,
            target_own_group=True,
            purchase_cost=1200
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.05,
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
            description="Choose up to 3 allies. For the next 2 turns, they regain 8% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=3,
            num_targets=3,
            level_requirement=21,
            target_own_group=True,
            purchase_cost=2400
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        regenerating = RegenerateHP(
            turns_remaining=2,
            value=0.08,
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
            description="Choose up to 3 allies. For the next 2 turns, they regain 10% of their max health at the start of each turn.",
            flavor_text="",
            mana_cost=75,
            cooldown=3,
            num_targets=3,
            level_requirement=23,
            target_own_group=True,
            purchase_cost=4800
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
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

# -----------------------------------------------------------------------------
# PARALYZING FUMES
# -----------------------------------------------------------------------------

class ParalyzingFumesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCAB",
            name="Paralyzing Fumes I",
            class_key=ExpertiseClass.Alchemist,
            description="Apply Faltering to all enemies, giving them a 50% chance to lose their next turn.",
            flavor_text="",
            mana_cost=40,
            cooldown=6,
            num_targets=-1,
            level_requirement=20,
            target_own_group=False,
            purchase_cost=5000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        faltering = TurnSkipChance(
            turns_remaining=1,
            value=0.5,
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
            description="With deft hands, you are able to use 3 items this turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=22,
            target_own_group=True,
            purchase_cost=8000
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        # Adding one because actions_remaining are reduced when pressing Continue
        caster.get_dueling().actions_remaining += 4
        caster.get_stats().dueling.alchemist_abilities_used += 1

        restriction = RestrictedToItems(
            turns_remaining=3,
            value=0,
            source_str=self.get_icon_and_name()
        )
        self._use_positive_status_effect_ability(caster, targets, [restriction])

        return "{0}" + f" used {self.get_icon_and_name()}!\n\nYou may now use up to 3 items from your inventory."

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore
