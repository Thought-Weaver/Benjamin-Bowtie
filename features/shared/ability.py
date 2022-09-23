from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from math import ceil
from random import randint, random

from typing import List, TYPE_CHECKING
from features.dueling import Dueling
from features.equipment import Equipment

from features.expertise import DEX_DODGE_SCALE, INT_DMG_SCALE, LUCK_CRIT_DMG_BOOST, LUCK_CRIT_SCALE, STR_DMG_SCALE, ExpertiseClass
from features.shared.item import ClassTag, WeaponStats
from features.shared.statuseffect import ConDebuff, DexDebuff, DmgReduction, FixedDmgTick, StatusEffect, StatusEffectKey, StrDebuff, TurnSkipChance

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
    def __init__(self, icon: str, name: str, class_key: ExpertiseClass, description: str, flavor_text: str, mana_cost: int, cooldown: int, num_targets: int, level_requirement: int):
        # TODO: Handle whether ability status effects stack with a new param
        # TODO: Handle "once per duel" case with a param like "already_cast" that gets reset at the end of duels
        #       This will also need to be reset, like cur_cooldown, at the beginning of duels for all entities
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

        self._cur_cooldown = 0 # Turns remaining until it can be used again

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

    def get_cur_cooldown(self):
        return self._cur_cooldown

    def reset_cd(self):
        self._cur_cooldown = 0

    def decrement_cd(self):
        self._cur_cooldown = max(0, self._cur_cooldown - 1)

    @abstractmethod
    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        pass

    def _use_damage_ability(self, caster: Player, targets: List[Player | NPC], dmg_range: range) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(dmg_range.start, dmg_range.stop) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            target_armor = target_equipment.get_total_reduced_armor()
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()

            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        return results

    def _use_negative_status_effect_ability(self, caster: Player, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results: List[NegativeAbilityResult] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_expertise = caster.get_expertise()

        for target in targets:
            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            target.get_dueling().status_effects += status_effects
            
            results.append(NegativeAbilityResult("{1}" + f" is now {status_effects_str}", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        return results

    def _use_damage_and_effect_ability(self, caster: Player, targets: List[Player | NPC], dmg_range: range, status_effects: List[StatusEffect]) -> List[NegativeAbilityResult]:
        results = self._use_damage_ability(caster, targets, dmg_range)
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        for i in range(len(results)):
            if not results[i].dodged:
                targets[i].get_dueling().status_effects += status_effects
            results[i].target_str += f" and is now {status_effects_str}"
        
        return results

    def _use_positive_status_effect_ability(self, caster: Player, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[str]:
        results: List[str] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_expertise = caster.get_expertise()

        for target in targets:
            target.get_dueling().status_effects += status_effects
            results.append("{1}" + f" is now {status_effects_str}")
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

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

        return (
            f"{self._icon} **{self._name}**\n"
            f"{self._mana_cost} Mana / {target_str} / {cooldown_str}\n\n"
            f"{self._description}\n\n"
            f"*{self._flavor_text}*\n\n"
            f"Requires {self._class_key} level {self._level_requirement}"
        )

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._num_targets = state.get("_num_targets", 0)

# -----------------------------------------------------------------------------
# FISHER ABILITIES
# -----------------------------------------------------------------------------
# SEA SPRAY
# -----------------------------------------------------------------------------

class SeaSprayI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 2-4 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=2
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(2, 4))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class SeaSprayII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 3-6 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(3, 6))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class SeaSprayIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 4-8 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(4, 8))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class SeaSprayIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 5-10 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(5, 10))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class SeaSprayV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA6",
            name="Sea Spray",
            class_key=ExpertiseClass.Fisher,
            description="Summon a rush of water that deals 6-12 damage to an enemy.",
            flavor_text="",
            mana_cost=5,
            cooldown=0,
            num_targets=1,
            level_requirement=4
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(6, 12))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# CURSE OF THE SEA
# -----------------------------------------------------------------------------

class CurseOfTheSeaI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -1 Constitution, -1 Strength, and -1 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=5
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-1,
            source_ability_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-1,
            source_ability_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-1,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class CurseOfTheSeaII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -2 Constitution, -2 Strength, and -2 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=9
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-2,
            source_ability_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-2,
            source_ability_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-2,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class CurseOfTheSeaIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Curse of the Sea",
            class_key=ExpertiseClass.Fisher,
            description="Curse an enemy to lose -3 Constitution, -3 Strength, and -3 Dexterity for 2 turns.",
            flavor_text="",
            mana_cost=10,
            cooldown=0,
            num_targets=1,
            level_requirement=13
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_debuff = ConDebuff(
            turns_remaining=2,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        str_debuff = StrDebuff(
            turns_remaining=2,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        dex_debuff = DexDebuff(
            turns_remaining=2,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [con_debuff, str_debuff, dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# HOOK
# -----------------------------------------------------------------------------

class HookI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 5-10 damage and causing them to lose -3 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=1,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(5, 10), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class HookII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 6-12 damage and causing them to lose -3 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=1,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(6, 12), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class HookIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE9D",
            name="Hook",
            class_key=ExpertiseClass.Fisher,
            description="Hook an enemy on the line, dealing 7-14 damage and causing them to lose -3 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=15,
            cooldown=1,
            num_targets=1,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_debuff = DexDebuff(
            turns_remaining=1,
            value=-3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(7, 14), [dex_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# WRATH OF THE WAVES
# -----------------------------------------------------------------------------

class WrathOfTheWavesI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 5-10 damage each. They take 50% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.5 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            damage = int(randint(5, 10) * bonus_dmg_boost * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            target_armor = target_equipment.get_total_reduced_armor()
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WrathOfTheWavesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 6-12 damage each. They take 80% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 1.8 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            damage = int(randint(8, 12) * bonus_dmg_boost * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            target_armor = target_equipment.get_total_reduced_armor()
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WrathOfTheWavesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="Wrath of the Waves",
            class_key=ExpertiseClass.Fisher,
            description="Call forth tidal waves to crash against up to 3 enemies, dealing 10-15 damage each. They take 110% more damage if they have a Dexterity debuff.",
            flavor_text="",
            mana_cost=35,
            cooldown=1,
            num_targets=3,
            level_requirement=14
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability.", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1
            bonus_dmg_boost = 2.1 if any(se.key == StatusEffectKey.DexDebuff for se in target.get_dueling().status_effects) else 1

            damage = int(randint(10, 15) * bonus_dmg_boost * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            percent_dmg_reduct = target.get_dueling().get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# HIGH TIDE
# -----------------------------------------------------------------------------

class HighTideI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 25%.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=0,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.25,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        return result_str

class HighTideII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 35%.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=0,
            level_requirement=15
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.35,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        return result_str


class HighTideIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF0A",
            name="High Tide",
            class_key=ExpertiseClass.Fisher,
            description="Raise a protective wall of water, reducing all damage you take next turn by 45%.",
            flavor_text="",
            mana_cost=20,
            cooldown=2,
            num_targets=0,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dmg_reduction = DmgReduction(
            turns_remaining=1,
            value=0.45,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dmg_reduction])
        result_str += "\n".join(results)

        return result_str

# -----------------------------------------------------------------------------
# THUNDERING TORRENT
# -----------------------------------------------------------------------------

class ThunderingTorrentI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 10-15 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=2,
            level_requirement=14
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(10, 15) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_ability_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class ThunderingTorrentII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 12-18 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=2,
            level_requirement=16
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(12, 18) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_ability_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class ThunderingTorrentIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
            name="Thundering Torrent",
            class_key=ExpertiseClass.Fisher,
            description="Conjure a raging current against up to 2 enemies, dealing 15-20 damage and half that again next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=1,
            num_targets=2,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(15, 20) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()
            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            target_dueling.status_effects.append(FixedDmgTick(
                turns_remaining=1,
                value=int(actual_damage_dealt / 2),
                source_ability_str=self.get_icon_and_name()
            ))

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# DROWN IN THE DEEP
# -----------------------------------------------------------------------------

class DrownInTheDeepI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 3 enemies into the depths, dealing each (1.5 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((1.5 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            actual_damage_dealt = target_expertise.damage(damage, 0, 0)

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class DrownInTheDeepII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 3 enemies into the depths, dealing each (2 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((2 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            actual_damage_dealt = target_expertise.damage(damage, 0, 0)

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class DrownInTheDeepIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2693",
            name="Drown in the Deep",
            class_key=ExpertiseClass.Fisher,
            description="Drag up to 3 enemies into the depths, dealing each (2.5 * # of status effects reducing their Dexterity)% of their max health as damage.",
            flavor_text="",
            mana_cost=70,
            cooldown=3,
            num_targets=3,
            level_requirement=26
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_dueling = target.get_dueling()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            target_max_hp = target_expertise.max_hp
            num_dex_reduce_effects = sum(list(map(lambda x: x.key == StatusEffectKey.DexDebuff, target_dueling.status_effects)))

            damage = int((2.5 * num_dex_reduce_effects) / 100 * target_max_hp)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            actual_damage_dealt = target_expertise.damage(damage, 0, 0)

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# WHIRLPOOL
# -----------------------------------------------------------------------------

class WhirlpoolI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 10-20 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=20
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(10, 20) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()

            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WhirlpoolII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 15-25 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(15, 25) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()

            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WhirlpoolIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF00",
            name="Whirlpool",
            class_key=ExpertiseClass.Fisher,
            description="Summon a vortex that deals 20-30 damage to all enemies and removes the Protected status effect from all of them.",
            flavor_text="",
            mana_cost=50,
            cooldown=2,
            num_targets=-1,
            level_requirement=24
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        results: List[NegativeAbilityResult] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()
            target_equipment = target.get_equipment()

            target_dodged = random() < target.get_combined_attributes().dexterity * DEX_DODGE_SCALE
            if target_dodged:
                results.append(NegativeAbilityResult("{1} dodged the ability", True))
                continue

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            damage = int(randint(20, 30) * critical_hit_boost)
            damage += int(damage * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))
            
            target_armor = target_equipment.get_total_reduced_armor()
            target_dueling = target.get_dueling()

            target_dueling.status_effects = list(filter(lambda x: x.key != StatusEffectKey.DmgReduction, target_dueling.status_effects))

            percent_dmg_reduct = target_dueling.get_total_percent_dmg_reduct()
            
            actual_damage_dealt = target_expertise.damage(damage, target_armor, percent_dmg_reduct)
            damage_reduction_str = Dueling.format_armor_dmg_reduct_str(damage, actual_damage_dealt)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"
            percent_dmg_reduct_str = f" ({percent_dmg_reduct * 100}% Reduction)"

            results.append(NegativeAbilityResult("{1}" + f" took {actual_damage_dealt}{damage_reduction_str}{percent_dmg_reduct_str}{critical_hit_str} damage", False))
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# SHATTERING STORM 
# -----------------------------------------------------------------------------

class ShatteringStormI(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 15% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.15,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class ShatteringStormII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 25% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=24
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.25,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class ShatteringStormIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u26C8\uFE0F",
            name="Shattering Storm",
            class_key=ExpertiseClass.Fisher,
            description="Invoke the tempest against up to 5 enemies, dealing 40-60 damage with a 35% chance for each to lose their next turn.",
            flavor_text="",
            mana_cost=150,
            cooldown=5,
            num_targets=5,
            level_requirement=24
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        skip_debuff = TurnSkipChance(
            turns_remaining=1,
            value=0.35,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_and_effect_ability(caster, targets, range(40, 60), [skip_debuff])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# GUARDIAN ABILITIES
# -----------------------------------------------------------------------------
# WHIRLWIND
# -----------------------------------------------------------------------------

class WhirlwindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 50% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=2
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = ceil(weapon_stats.get_random_damage() * 0.5)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WhirlwindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 60% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=5
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = ceil(weapon_stats.get_random_damage() * 0.6)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str


class WhirlwindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF2A\uFE0F",
            name="Whirlwind",
            class_key=ExpertiseClass.Guardian,
            description="Swing your weapon around you, dealing 70% of your weapon damage to all enemies.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=-1,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = weapon_stats.get_random_damage() * 0.7
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

# -----------------------------------------------------------------------------
# SECOND WIND
# -----------------------------------------------------------------------------

class SecondWindI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind",
            class_key=ExpertiseClass.Guardian,
            description="Restore 5% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=3
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_equipment: Equipment = caster.get_equipment()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster_equipment.get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = ceil(weapon_stats.get_random_damage() * 0.5)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        # TODO: Implement healing base function

        return result_str