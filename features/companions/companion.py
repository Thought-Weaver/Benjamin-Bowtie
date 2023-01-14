from __future__ import annotations

from abc import abstractmethod
from math import ceil
from strenum import StrEnum

from features.npcs.npc import NPC
from features.shared.enums import ClassTag
from features.shared.item import Rarity

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.shared.ability import Ability
    from features.shared.effect import Effect

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

BASE_GOOD_TIER_ACTIONS = 50
BASE_GREAT_TIER_ACTIONS = 500
BASE_BEST_TIER_ACTIONS = 5000

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class CompanionKey(StrEnum):
    Unknown = "Unknown"
    TidewaterCrab = "TidewaterCrab"
    PondloverFrog = "PondloverFrog"
    SunbaskTurtle = "SunbaskTurtle"
    FlyingFox = "FlyingFox"
    ShadowfootRaccoon = "ShadowfootRaccoon"
    TanglewebSpider = "TanglewebSpider"
    PaleWalkerSpider = "PaleWalkerSpider"
    VerdantSlitherer = "VerdantSlitherer"
    GnashtuskBoar = "GnashtuskBoar"
    VoidseenCat = "VoidseenCat"
    VoidseenPup = "VoidseenPup"
    DeepwoodCub = "DeepwoodCub"
    FleetfootRabbit = "FleetfootRabbit"
    GiantTowerBeetle = "GiantTowerBeetle"
    MinatureBoneGolem = "MiniatureBoneGolem"
    SilverwingOwl = "SilverwingOwl"
    BlueFlitterwingButterfly = "BlueFlitterwingButterfly"
    ScuttledarkScorpion = "ScuttledarkScorpion"
    WanderboundRaven = "WanderboundRaven"

class CompanionTier(StrEnum):
    NoTier = "NoTier"
    Good = "Good"
    Great = "Great"
    Best = "Best"

# -----------------------------------------------------------------------------
# BASE CLASS
# -----------------------------------------------------------------------------

class Companion():
    def __init__(self, icon: str, display_name: str, key: CompanionKey, rarity: Rarity, has_active_ability: bool, duel_xp_gain: int, pet_battle_xp_gain: int):
        self._icon = icon
        self._display_name = display_name
        self._key = key
        self._rarity = rarity
        self._has_active_ability = has_active_ability
        
        self.duel_xp_gain = duel_xp_gain
        self.pet_battle_xp_gain = pet_battle_xp_gain

        self._xp: int = 0
        self._level: int = 0
        self._remaining_xp: int = 1

        self._actions_remaining_to_next_tier: int = 50
        self._companion_tier: CompanionTier = CompanionTier.NoTier

        # So, the concept here is that each Companion will reference an NPC which will be instantised based on the level
        # of the Companion; the abilities and stats, notably, will be determined based on that input level.
        self._pet_battle_entity: NPC | None = None

    # This will either return an Ability or an Effect, with a that based on the level of the companion
    @abstractmethod
    def get_dueling_ability(self) -> Effect | Ability:
        pass

    @abstractmethod
    def instantise_pet_battle_entity(self) -> NPC:
        pass

    def get_xp_to_level(self, level: int) -> int:
        return ceil(75 + 30 * level * (level - 1) + (2 ** ((level - 1) / 15.0) - 1) / (1 - 2 ** (-1 / 15.0)))

    def level_up_check(self) -> int:
        org_level = self._level
        while self._remaining_xp <= 0:
            self._level += 1
            self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp
        return self._level - org_level

    def add_xp(self, xp_to_add: int) -> int:
        org_level = self._level

        self._xp = max(0, self._xp + xp_to_add)
        self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp

        self.level_up_check()

        return self._level - org_level

    def get_icon_and_name(self):
        return f"{self._icon} {self._display_name}"

    def get_name(self):
        return self._display_name

    def get_icon(self):
        return self._icon

    def get_has_active_ability(self):
        return self._has_active_ability

    def __str__(self) -> str:
        display_string = f"**{self.get_icon_and_name()}**\n*{self._rarity} Companion*\n\n"

        display_string += f"Level: {self._level} *({self.get_xp_to_level(self._level + 1) - self._xp} xp to next)*\n\n"
        
        if self._has_active_ability:
            display_string += "**Active Dueling Ability**\n\n"
        else:
            display_string += "**Passive Dueling Ability**\n\n"
        display_string += str(self.get_dueling_ability()) + "\n\n"

        self._pet_battle_entity = self.instantise_pet_battle_entity()
        expertise = self._pet_battle_entity.get_expertise()
        display_string += (
            f"**Attributes**\n\n"
            f"Constitution: {expertise.constitution}\n"
            f"Strength: {expertise.strength}\n"
            f"Dexterity: {expertise.dexterity}\n"
            f"Intelligence: {expertise.intelligence}\n"
            f"Luck: {expertise.luck}\n"
            f"Memory: {expertise.memory}\n\n"
        )

        display_string += (
            f"**Weapon**\n\n"
            f"{self._pet_battle_entity.get_equipment().get_item_in_slot(ClassTag.Equipment.MainHand)}"
        )

        return display_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._icon = state.get("_icon", "")
        self._display_name = state.get("_display_name", "")
        self._key = state.get("_key", CompanionKey.Unknown)
        self._rarity = state.get("_rarity", Rarity.Unknown)
        self._has_active_ability = state.get("_has_active_ability", False)
        self._duel_xp_gain = state.get("_duel_xp_gain", 1)

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._actions_remaining_to_next_tier = state.get("_actions_remaining_to_next_tier", 50)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self._pet_battle_entity = state.get("_pet_battle_entity", None)

# -----------------------------------------------------------------------------
# COMPANION CLASSES
# -----------------------------------------------------------------------------

class TidewaterCrab(Companion):
    def __init__(self):
        super().__init__(
            icon="\uD83E\uDD80",
            display_name="Tidewater Crab",
            key=CompanionKey.TidewaterCrab,
            rarity=Rarity.Common,
            has_active_ability=True,
            duel_xp_gain=3,
            pet_battle_xp_gain=5
        )

    def get_dueling_ability(self) -> Ability:
        pass

    def instantise_pet_battle_entity(self) -> NPC:
        pass

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.__init__() # type: ignore

        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = state.get("_remaining_xp", 1)

        self._actions_remaining_to_next_tier = state.get("_actions_remaining_to_next_tier", 50)
        self._companion_tier = state.get("_companion_tier", CompanionTier.NoTier)

        self._pet_battle_entity = state.get("_pet_battle_entity", None)
