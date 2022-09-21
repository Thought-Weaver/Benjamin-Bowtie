from __future__ import annotations

from abc import abstractmethod
from random import randint
from re import S
from strenum import StrEnum

from typing import List, TYPE_CHECKING

from features.expertise import INT_DMG_SCALE, ExpertiseClass

if TYPE_CHECKING:
    from features.npcs.npc import NPC
    from features.player import Player

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

BLEED_PERCENT_HP = 0.01
POISONED_PERCENT_HP = 0.01

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class StatusEffect(StrEnum):
    Bleeding = "Bleeding"
    Poisoned = "Poisoned"

# -----------------------------------------------------------------------------
# BASE CLASS
# -----------------------------------------------------------------------------

class Ability():
    def __init__(self, icon: str, name: str, class_key: ExpertiseClass, description: str, flavor_text: str, mana_cost: int, cooldown: int, num_targets: int, level_requirement: int):
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

    @abstractmethod
    def use_ability(self, caster: Player, targets: List[Player | NPC]) -> str:
        pass

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

# -----------------------------------------------------------------------------
# SEA SPRAY
# -----------------------------------------------------------------------------

class SeaSprayI(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
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
        caster_expertise = caster.get_expertise()
        caster_equipment = caster.get_equipment()
        caster_int = caster_expertise.intelligence
        equipment_int = caster_equipment.get_total_buffs().int_buff

        damage = randint(2, 4)
        damage += int(damage * INT_DMG_SCALE * (caster_int + equipment_int))

        target = targets[0]
        target_expertise = target.get_expertise()

        target_expertise.damage(damage)

        return "{0}" + f" cast {self.get_icon_and_name()} against " + "{1}" + f" for {damage} damage."


class SeaSprayII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
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
        caster_expertise = caster.get_expertise()
        caster_equipment = caster.get_equipment()
        caster_int = caster_expertise.intelligence
        equipment_int = caster_equipment.get_total_buffs().int_buff

        damage = randint(3, 6)
        damage += int(damage * INT_DMG_SCALE * (caster_int + equipment_int))

        target = targets[0]
        target_expertise = target.get_expertise()

        target_expertise.damage(damage)

        return "{0}" + f" cast {self.get_icon_and_name()} against " + "{1}" + f" for {damage} damage."


class SeaSprayIII(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
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
        caster_expertise = caster.get_expertise()
        caster_equipment = caster.get_equipment()
        caster_int = caster_expertise.intelligence
        equipment_int = caster_equipment.get_total_buffs().int_buff

        damage = randint(4, 8)
        damage += int(damage * INT_DMG_SCALE * (caster_int + equipment_int))

        target = targets[0]
        target_expertise = target.get_expertise()

        target_expertise.damage(damage)

        return "{0}" + f" cast {self.get_icon_and_name()} against " + "{1}" + f" for {damage} damage."


class SeaSprayIV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
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
        caster_expertise = caster.get_expertise()
        caster_equipment = caster.get_equipment()
        caster_int = caster_expertise.intelligence
        equipment_int = caster_equipment.get_total_buffs().int_buff

        damage = randint(5, 10)
        damage += int(damage * INT_DMG_SCALE * (caster_int + equipment_int))

        target = targets[0]
        target_expertise = target.get_expertise()

        target_expertise.damage(damage)

        return "{0}" + f" cast {self.get_icon_and_name()} against " + "{1}" + f" for {damage} damage."


class SeaSprayV(Ability):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDEE7",
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
        caster_expertise = caster.get_expertise()
        caster_equipment = caster.get_equipment()
        caster_int = caster_expertise.intelligence
        equipment_int = caster_equipment.get_total_buffs().int_buff

        damage = randint(6, 12)
        damage += int(damage * INT_DMG_SCALE * (caster_int + equipment_int))

        target = targets[0]
        target_expertise = target.get_expertise()

        target_expertise.damage(damage)

        return "{0}" + f" cast {self.get_icon_and_name()} against " + "{1}" + f" for {damage} damage."

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
        target = targets[0]
        target_expertise = target.get_expertise()

        # TODO: In Dueling, implement a temporary effect system.

        return f"You cast {self.get_icon_and_name()}! The opponent has been weakened."
