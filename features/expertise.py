from abc import abstractmethod
from discord.embeds import Embed
from math import ceil
from strenum import StrEnum

import discord

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

CON_HEALTH_SCALE = 0.08
CON_HEALTH_REGEN_SCALE = 0.01
STR_DMG_SCALE = 0.02
DEX_DODGE_SCALE = 0.0025
INT_MANA_SCALE = 0.11
INT_MANA_REGEN_SCALE = 0.01
INT_DMG_SCALE = 0.02
LUCK_CRIT_SCALE = 0.005

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class ExpertiseClass(StrEnum):
    Alchemist = "Alchemist"
    Fisher = "Fisher"
    Guardian = "Guardian"
    Merchant = "Merchant"

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

# Expertise is similar to a class system in RPG games, such as being able to
# level Illusion magic in Skyrim or level cooking in WoW. While somewhat related
# to stats, it's going to be a separate system, since it's abstracted away from
# individual actions. I may rely on values in stats to contribute to leveling
# or I may pick and choose certain actions to level a class.

class BaseExpertise():
    def __init__(self):
        self._xp: int = 0
        self._level: int = 0
        self._remaining_xp: int = 0

    # Could be positive or negative, regardless don't go below 0.
    def add_xp(self, value: int):
        org_level = self._level

        self._xp = max(0, self._xp + value)
        self._remaining_xp = self.get_xp_to_level(self._level + 1)

        while self._remaining_xp <= 0:
            self._level += 1
            self._remaining_xp = self.get_xp_to_level(self._level + 1)

        return self._level - org_level

    def get_xp(self):
        return self._xp

    def get_level(self):
        return self._level

    @abstractmethod
    def get_xp_to_level(self, level: int) -> float:
        return


class FisherExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int):
        return 100 + 25 * level * (level - 1) + 75 * (2 ** ((level - 1) / 7.0) - 1) / (1 - 2 ** (-1 / 7.0))


class MerchantExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int):
        return 15 + 15 * level * (level - 1) + 25 * (2 ** ((level - 1) / 8.0) - 1) / (1 - 2 ** (-1 / 8.0))


class Expertise():
    def __init__(self):
        # Expertise classes
        self._fisher = FisherExpertise()
        self._merchant = MerchantExpertise()

        # Base stats
        self.level = 0
        self.max_hp = 20
        self.hp = 20
        self.max_mana = 20
        self.mana = 20

        # Attributes
        self.constitution = 0
        self.strength = 0
        self.dexterity = 0
        self.intelligence = 0
        self.luck = 0
        self.memory = 0

        # Leveling Up
        self.points_to_spend = 0

    def add_xp_to_class(self, xp: int, expertise_class: ExpertiseClass):
        levels_gained: int = 0
        if expertise_class == ExpertiseClass.Fisher:
            levels_gained = self._fisher.add_xp(xp)
        elif expertise_class == ExpertiseClass.Merchant:
            levels_gained = self._merchant.add_xp(xp)
        self.points_to_spend += levels_gained

    def heal(self, heal_amount: int):
        self.hp = min(self.max_hp, self.hp + heal_amount)

    def damage(self, damage: int):
        self.hp = max(0, self.hp - damage)

    def restore_mana(self, restore_amount: int):
        self.mana = min(self.max_mana, self.mana + restore_amount)
    
    def remove_mana(self, remove_amount: int):
        self.mana = max(0, self.mana - remove_amount)

    def get_health_and_mana_string(self):
        hp_num_squares = ceil(self.hp / self.max_hp * 10)
        mana_num_squares = ceil(self.mana / self.max_mana * 10)
        
        hp_squares_string = ""
        mana_squares_string = ""

        for i in range(1, 11):
            hp_squares_string += "🟥" if i <= hp_num_squares else "⬛"
            mana_squares_string += "🟦" if i <= mana_num_squares else "⬛"

        return f"HP: {hp_squares_string} ({self.hp}/{self.max_hp})\n" \
               f"Mana: {mana_squares_string} ({self.mana}/{self.max_mana})"

    def get_info_string(self):
        fisher_level: int = self._fisher.get_level()
        merchant_level: int = self._merchant.get_level()

        info_string = f"**Base Stats**\n\n" \
            f"{self.get_health_and_mana_string()}\n\n" \
            f"**Classes**\n\n" \
            f"Alchemist: ???\n" \
            f"Fisher: Lvl. {fisher_level} ({self._fisher.get_xp_to_level(fisher_level + 1)} xp to next)\n" \
            f"Guardian: ???\n" \
            f"Merchant: Lvl. {merchant_level} ({self._fisher.get_xp_to_level(merchant_level + 1)} xp to next)\n\n" \
            f"**Attributes**\n\n" \
            f"Constitution: {self.constitution}\n" \
            f"Strength: {self.strength}\n" \
            f"Dexterity: {self.dexterity}\n" \
            f"Intelligence: {self.intelligence}\n" \
            f"Luck: {self.luck}\n" \
            f"Memory: {self.memory}"

        if self.points_to_spend > 0:
            info_string += f"\n\n*You have {self.points_to_spend} attribute points to spend!*"

        return info_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._fisher = state.get("_fisher", FisherExpertise())
        self._merchant = state.get("_merchant", MerchantExpertise())

        self.level = state.get("level", 1)
        self.max_hp = state.get("max_hp", 20)
        self.hp = state.get("hp", 20)
        self.max_mana = state.get("max_mana", 20)
        self.mana = state.get("mana", 20)

        self.constitution = state.get("constitution", 0)
        self.strength = state.get("strength", 0)
        self.dexterity = state.get("dexterity", 0)
        self.intelligence = state.get("intelligence", 0)
        self.luck = state.get("luck", 0)
        self.memory = state.get("memory", 0)

        self.points_to_spend = state.get("points_to_spend", 0)


class ExpertiseView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_user(self):
        return self._user
