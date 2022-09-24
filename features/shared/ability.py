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
from features.shared.statuseffect import BLEED_PERCENT_HP, AttrBuffOnDamage, Bleeding, ConBuff, ConDebuff, DexBuff, DexDebuff, DmgReduction, FixedDmgTick, Generating, IntBuff, IntDebuff, LckBuff, ManaToHP, NonTargetable, StatusEffect, StatusEffectKey, StrBuff, StrDebuff, Tarnished, Taunted, TurnSkipChance

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

    def get_cur_cooldown(self):
        return self._cur_cooldown

    def reset_cd(self):
        self._cur_cooldown = 0

    def decrement_cd(self):
        if self._cur_cooldown != -1:
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
            target.get_expertise().update_stats()

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
                targets[i].get_expertise().update_stats()
            results[i].target_str += f" and is now {status_effects_str}"
        
        return results

    def _use_positive_status_effect_ability(self, caster: Player, targets: List[Player | NPC], status_effects: List[StatusEffect]) -> List[str]:
        results: List[str] = []
        status_effects_str: str = ", ".join(list(map(lambda x: x.name, status_effects)))

        caster_expertise = caster.get_expertise()

        for target in targets:
            target.get_dueling().status_effects += status_effects
            target.get_expertise().update_stats()
            results.append("{1}" + f" is now {status_effects_str}")
        
        caster_expertise.remove_mana(self.get_mana_cost())
        self._cur_cooldown = self._cooldown

        return results

    def _use_heal_ability(self, caster: Player, targets: List[Player | NPC], heal_range: range) -> List[str]:
        results: List[str] = []
        
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()

        for target in targets:
            target_expertise = target.get_expertise()

            critical_hit_boost = LUCK_CRIT_DMG_BOOST if random() < caster_attrs.luck * LUCK_CRIT_SCALE else 1

            heal_amount = int(randint(heal_range.start, heal_range.stop) * critical_hit_boost)
            heal_amount += int(heal_amount * INT_DMG_SCALE * max(caster_attrs.intelligence, 0))

            target_expertise.heal(heal_amount)

            critical_hit_str = "" if critical_hit_boost == 0 else " [Crit!]"

            results.append("{1}" + f" was healed for {heal_amount}{critical_hit_str} HP")
        
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

        flavor_text: str = f"*{self._flavor_text}*\n\n" if self._flavor_text != "" else ""

        return (
            f"{self._icon} **{self._name}**\n"
            f"{self._mana_cost} Mana / {target_str} / {cooldown_str}\n\n"
            f"{self._description}\n\n"
            f"{flavor_text}"
            f"Requires {self._class_key} level {self._level_requirement}"
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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


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
        heal_amount = caster.get_expertise().max_hp * 0.05

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SecondWindII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind",
            class_key=ExpertiseClass.Guardian,
            description="Restore 10% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        heal_amount = caster.get_expertise().max_hp * 0.1

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class SecondWindIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Second Wind",
            class_key=ExpertiseClass.Guardian,
            description="Restore 15% of your missing health.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=13
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        heal_amount = caster.get_expertise().max_hp * 0.15

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_heal_ability(caster, targets, range(heal_amount, heal_amount))
        result_str += "\n".join(results)

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
            name="Scar Armor",
            class_key=ExpertiseClass.Guardian,
            description="Whenever you're attacked over the next 3 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=5
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        on_damage_buff = AttrBuffOnDamage(
            turns_remaining=3,
            on_being_hit_buffs=[ConBuff(
                turns_remaining=-1,
                value=1,
                source_ability_str=self.get_icon_and_name()
            )],
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [on_damage_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ScarArmorII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2620\uFE0F",
            name="Scar Armor",
            class_key=ExpertiseClass.Guardian,
            description="Whenever you're attacked over the next 5 turns, increase your Constitution by 1 until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=15
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        on_damage_buff = AttrBuffOnDamage(
            turns_remaining=5,
            on_being_hit_buffs=[ConBuff(
                turns_remaining=-1,
                value=1,
                source_ability_str=self.get_icon_and_name()
            )],
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [on_damage_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# EVADE
# -----------------------------------------------------------------------------

class UnbreakingI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Unbreaking",
            class_key=ExpertiseClass.Guardian,
            description="Gain +1 Constitution for each slot of armor you don't have equipped until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=caster.get_equipment().get_num_slots_unequipped(),
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnbreakingII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Unbreaking",
            class_key=ExpertiseClass.Guardian,
            description="Gain +2 Constitution for each slot of armor you don't have equipped until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=2 * caster.get_equipment().get_num_slots_unequipped(),
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnbreakingIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDEE1\uFE0F",
            name="Unbreaking",
            class_key=ExpertiseClass.Guardian,
            description="Gain +3 Constitution for each slot of armor you don't have equipped until the end of the duel.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=16
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        con_buff = ConBuff(
            turns_remaining=-1,
            value=3 * caster.get_equipment().get_num_slots_unequipped(),
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [con_buff])
        result_str += "\n".join(results)

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
            name="Counterstrike",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 75% of your weapon damage + 10% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=9
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.75 * weapon_stats.get_random_damage() + 0.1 * (caster_expertise.max_hp - caster_expertise.hp)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CounterstrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Counterstrike",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 80% of your weapon damage + 20% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.8 * weapon_stats.get_random_damage() + 0.2 * (caster_expertise.max_hp - caster_expertise.hp)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CounterstrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDD04",
            name="Counterstrike",
            class_key=ExpertiseClass.Guardian,
            description="Strike back at an enemy dealing 85% of your weapon damage + 30% of your missing health as damage.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=15
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_expertise = caster.get_expertise()
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.85 * weapon_stats.get_random_damage() + 0.3 * (caster_expertise.max_hp - caster_expertise.hp)
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="Bided Attack",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +3 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BidedAttackII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Bided Attack",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +4 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=11
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=4,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BidedAttackIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u23F3",
            name="Bided Attack",
            class_key=ExpertiseClass.Guardian,
            description="Prepare your attack, gaining +5 Strength for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=0,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        str_buff = StrBuff(
            turns_remaining=1,
            value=4,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [str_buff])
        result_str += "\n".join(results)

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
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        taunt = Taunted(
            turns_remaining=1,
            forced_to_attack=caster,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [taunt])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="Piercing Strike",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 110% of your weapon damage with a 20% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=15
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 1.1 * weapon_stats.get_random_damage()
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_ability_str=self
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.2:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats()
            results[i].target_str += f" and is now {bleed.name}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PiercingStrikeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Piercing Strike",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 120% of your weapon damage with a 25% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 1.2 * weapon_stats.get_random_damage()
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_ability_str=self
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.25:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats()
            results[i].target_str += f" and is now {bleed.name}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class PiercingStrikeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCCD",
            name="Piercing Strike",
            class_key=ExpertiseClass.Guardian,
            description="Lunge forward at an enemy, dealing 130% of your weapon damage with a 30% chance to set Bleeding.",
            flavor_text="",
            mana_cost=0,
            cooldown=2,
            num_targets=1,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 1.3 * weapon_stats.get_random_damage()
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        
        bleed = Bleeding(
            turns_remaining=3,
            value=BLEED_PERCENT_HP,
            source_ability_str=self
        )

        for i in range(len(results)):
            if not results[i].dodged and random() < 0.3:
                targets[i].get_dueling().status_effects.append(bleed)
                targets[i].get_expertise().update_stats()
            results[i].target_str += f" and is now {bleed.name}"
                
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="Press the Advantage",
            class_key=ExpertiseClass.Guardian,
            description="Gain 2 actions this turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=-1,
            num_targets=0,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster.get_dueling().actions_remaining += 2
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
            name="Evade",
            class_key=ExpertiseClass.Guardian,
            description="Gain +200 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=20
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=200,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EvadeII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Evade",
            class_key=ExpertiseClass.Guardian,
            description="Gain +300 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=300,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class EvadeIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA8",
            name="Evade",
            class_key=ExpertiseClass.Guardian,
            description="Gain +400 Dexterity for 1 turn.",
            flavor_text="",
            mana_cost=0,
            cooldown=5,
            num_targets=0,
            level_requirement=24
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        dex_buff = DexBuff(
            turns_remaining=1,
            value=400,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [dex_buff])
        result_str += "\n".join(results)

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
            name="Heavy Slam",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 40% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.4 * weapon_stats.get_random_damage() + 0.05 * caster_attrs.constitution
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavySlamII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Heavy Slam",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 60% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=24
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.6 * weapon_stats.get_random_damage() + 0.05 * caster_attrs.constitution
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavySlamIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCA5",
            name="Heavy Slam",
            class_key=ExpertiseClass.Guardian,
            description="Power forward with your weapon, dealing 80% of your weapon damage + 5% for each point of Constitution you have",
            flavor_text="",
            mana_cost=0,
            cooldown=3,
            num_targets=1,
            level_requirement=26
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        caster_attrs = caster.get_combined_attributes()
        main_hand_item = caster.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)
        weapon_stats = WeaponStats(1, 2) if main_hand_item is None else main_hand_item.get_weapon_stats()

        damage = 0.8 * weapon_stats.get_random_damage() + 0.05 * caster_attrs.constitution
        damage += int(damage * STR_DMG_SCALE * max(caster_attrs.strength, 0))

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="Contract: Wealth for Power",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 50 coins for +1 Intelligence, +1 Strength, and +1 Dexterity until the end of the duel. If you can't pay, you instead receive -1 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=-1,
            num_targets=0,
            level_requirement=2
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-1,
                source_ability_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-1,
                source_ability_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-1,
                source_ability_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=1,
                source_ability_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=1,
                source_ability_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=1,
                source_ability_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractWealthForPowerII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCDC",
            name="Contract: Wealth for Power",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 50 coins for +3 Intelligence, +3 Strength, and +3 Dexterity until the end of the duel. If you can't pay, you instead receive -3 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=-1,
            num_targets=0,
            level_requirement=6
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-3,
                source_ability_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-3,
                source_ability_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-3,
                source_ability_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=3,
                source_ability_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=3,
                source_ability_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=3,
                source_ability_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractWealthForPowerIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCDC",
            name="Contract: Wealth for Power",
            class_key=ExpertiseClass.Merchant,
            description="Summon a binding contract, exchanging 50 coins for +5 Intelligence, +5 Strength, and +5 Dexterity until the end of the duel. If you can't pay, you instead receive -3 to those attributes.",
            flavor_text="",
            mana_cost=10,
            cooldown=-1,
            num_targets=0,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"

        if caster.get_inventory().get_coins() < 50:
            int_debuff = IntDebuff(
                turns_remaining=-1,
                value=-5,
                source_ability_str=self.get_icon_and_name()
            )

            str_debuff = IntDebuff(
                turns_remaining=-1,
                value=-5,
                source_ability_str=self.get_icon_and_name()
            )

            dex_debuff = DexDebuff(
                turns_remaining=-1,
                value=-5,
                source_ability_str=self.get_icon_and_name()
            )

            results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [int_debuff, str_debuff, dex_debuff])
            result_str += "\n".join(list(map(lambda x: x.target_str, results)))
        else:
            caster.get_inventory().remove_coins(50)

            int_buff = IntBuff(
                turns_remaining=-1,
                value=5,
                source_ability_str=self.get_icon_and_name()
            )

            str_buff = StrBuff(
                turns_remaining=-1,
                value=5,
                source_ability_str=self.get_icon_and_name()
            )

            dex_buff = DexBuff(
                turns_remaining=-1,
                value=5,
                source_ability_str=self.get_icon_and_name()
            )

            result_str += "\n".join(self._use_positive_status_effect_ability(caster, targets, [int_buff, str_buff, dex_buff]))

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
            name="Bound to Get Lucky",
            class_key=ExpertiseClass.Merchant,
            description="Gain +4 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=4
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
            value=4,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky",
            class_key=ExpertiseClass.Merchant,
            description="Gain +6 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=6
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
            value=6,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class BoundToGetLuckyIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83C\uDF40",
            name="Bound to Get Lucky",
            class_key=ExpertiseClass.Merchant,
            description="Gain +8 Luck for the next 2 turns.",
            flavor_text="",
            mana_cost=15,
            cooldown=4,
            num_targets=0,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        lck_buff = LckBuff(
            turns_remaining=2,
            value=8,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [lck_buff])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# SMOOTH TALKING
# -----------------------------------------------------------------------------

class SmoothTalkingI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDDE3\uFE0F",
            name="Smooth Talking",
            class_key=ExpertiseClass.Merchant,
            description="Convince an enemy not to attack, use an ability, or target you with an item next turn.",
            flavor_text="",
            mana_cost=20,
            cooldown=3,
            num_targets=1,
            level_requirement=6
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        non_targetable = NonTargetable(
            turns_remaining=1,
            who_cant_target=targets,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [non_targetable])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="A Tidy Sum",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 2 turns, part of the enemy struct turns into coins, awarding you 5 coins per attack hit.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=8
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=2,
            value=5,
            targets_that_generate_on_hit=targets,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ATidySumII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="A Tidy Sum",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 2 turns, part of the enemy struct turns into coins, awarding you 10 coins per attack hit.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=2,
            value=10,
            targets_that_generate_on_hit=targets,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ATidySumIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDCB0",
            name="A Tidy Sum",
            class_key=ExpertiseClass.Merchant,
            description="Whenever you attack for the next 2 turns, part of the enemy struct turns into coin, awarding you 15 coins per attack hit.",
            flavor_text="",
            mana_cost=25,
            cooldown=5,
            num_targets=1,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        generating = Generating(
            turns_remaining=2,
            value=15,
            targets_that_generate_on_hit=targets,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_negative_status_effect_ability(caster, targets, [generating])
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

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
            name="Cursed Coins",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain coins, deal 0.25 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=10
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.25,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CursedCoinsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain coins, deal 0.5 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=12
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.5,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class CursedCoinsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE99",
            name="Cursed Coins",
            class_key=ExpertiseClass.Merchant,
            description="For the next 3 turns, whenever you gain coins, deal 0.75 times that much damage to all enemies.",
            flavor_text="",
            mana_cost=25,
            cooldown=4,
            num_targets=0,
            level_requirement=14
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        tarnished = Tarnished(
            turns_remaining=3,
            value=0.75,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [tarnished])
        result_str += "\n".join(results)

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
            name="Unseen Riches",
            class_key=ExpertiseClass.Merchant,
            description="Gain coins equal to 0.5 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=11
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(0.5 * coins_to_add)
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnseenRichesII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches",
            class_key=ExpertiseClass.Merchant,
            description="Gain coins equal to 1 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=13
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(coins_to_add)
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class UnseenRichesIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83D\uDC8E",
            name="Unseen Riches",
            class_key=ExpertiseClass.Merchant,
            description="Gain coins equal to 1.5 times your current Luck.",
            flavor_text="",
            mana_cost=30,
            cooldown=5,
            num_targets=0,
            level_requirement=15
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        coins_to_add: int = caster.get_combined_attributes().luck
        caster.get_inventory().add_coins(1.5 * coins_to_add)
        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\nYou gained {coins_to_add} coins."

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
            name="Contract: Mana to Blood",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 70% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=14
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
            value=0.7,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractManaToBloodII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 50% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=16
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
            value=0.5,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractManaToBloodIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\u2728",
            name="Contract: Mana to Blood",
            class_key=ExpertiseClass.Merchant,
            description="All of your abilities that use Mana instead take 30% of their cost in HP next turn.",
            flavor_text="",
            mana_cost=10,
            cooldown=2,
            num_targets=0,
            level_requirement=16
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        mana_to_hp = ManaToHP(
            turns_remaining=1,
            value=0.3,
            source_ability_str=self.get_icon_and_name()
        )

        result_str: str = "{0}" + f" used {self.get_icon_and_name()}!\n\n"
        results: List[str] = self._use_positive_status_effect_ability(caster, targets, [mana_to_hp])
        result_str += "\n".join(results)

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
            name="Contract: Blood for Blood",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 15% of your current health and deals 0.5 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=16
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(0.15 * 0.5 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractBloodForBloodII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Contract: Blood for Blood",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 10% of your current health and deals 1 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=18
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(0.1 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class ContractBloodForBloodIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDE78",
            name="Contract: Blood for Blood",
            class_key=ExpertiseClass.Merchant,
            description="Create a binding contract that exchanges 5% of your current health and deals 3 times that damage against up to 3 targets.",
            flavor_text="",
            mana_cost=75,
            cooldown=5,
            num_targets=3,
            level_requirement=20
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        current_health: int = caster.get_expertise().hp
        damage: int = int(3 * 0.05 * current_health)

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

# -----------------------------------------------------------------------------
# HEAVY POCKETS
# -----------------------------------------------------------------------------

class HeavyPocketsI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Heavy Pockets",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=19
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(100, int(0.01 * caster.get_inventory().get_coins()))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavyPocketsII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Heavy Pockets",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(150, int(0.01 * caster.get_inventory().get_coins()))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore


class HeavyPocketsIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDDFE",
            name="Heavy Pockets",
            class_key=ExpertiseClass.Merchant,
            description="Deal damage equal to 1% of your current coins (up to 100 damage) and lose that many coins.",
            flavor_text="",
            mana_cost=80,
            cooldown=2,
            num_targets=1,
            level_requirement=22
        )

    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        damage: int = max(200, int(0.01 * caster.get_inventory().get_coins()))

        result_str: str = "{0}" + f" cast {self.get_icon_and_name()}!\n\n"
        results: List[NegativeAbilityResult] = self._use_damage_ability(caster, targets, range(damage, damage))
        result_str += "\n".join(list(map(lambda x: x.target_str, results)))

        return result_str

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore
