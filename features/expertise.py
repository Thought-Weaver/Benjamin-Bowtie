from __future__ import annotations

from abc import abstractmethod
from discord.embeds import Embed
from math import ceil
from strenum import StrEnum

import discord

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.equipment import Equipment
    from features.player import Player
    from features.shared.item import Buffs

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

# Don't want this in the Expertise class to avoid serializing them. Might be
# safer to write a custom __getstate__ instead of leaving these as globals.

BASE_HP = 20
BASE_MANA = 20

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
    Unknown = "Unknown"
    Alchemist = "Alchemist"
    Fisher = "Fisher"
    Guardian = "Guardian"
    Merchant = "Merchant"

class Attribute(StrEnum):
    Constitution = "Constitution"
    Strength = "Strength"
    Dexterity = "Dexterity"
    Intelligence = "Intelligence"
    Luck = "Luck"
    Memory = "Memory"

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
        self._remaining_xp: int = 1

    def level_up_check(self):
        org_level = self._level
        while self._remaining_xp <= 0:
            self._level += 1
            self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp
        return self._level - org_level

    # Could be positive or negative, regardless don't go below 0.
    def add_xp(self, value: int):
        org_level = self._level

        self._xp = max(0, self._xp + value)
        self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp

        self.level_up_check()

        return self._level - org_level

    def get_xp(self):
        return self._xp

    def get_level(self):
        return self._level

    @abstractmethod
    def get_xp_to_level(self, level: int) -> int:
        return 1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._xp = state.get("_xp", 0)
        self._level = state.get("_level", 0)
        self._remaining_xp = self.get_xp_to_level(self._level + 1) - self._xp


class FisherExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int) -> int:
        return ceil(100 + 25 * level * (level - 1) + 75 * (2 ** ((level - 1) / 7.0) - 1) / (1 - 2 ** (-1 / 7.0)))


class MerchantExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int) -> int:
        return ceil(15 + 15 * level * (level - 1) + 25 * (2 ** ((level - 1) / 8.0) - 1) / (1 - 2 ** (-1 / 8.0)))


class Expertise():
    def __init__(self):
        # Expertise classes
        self._fisher = FisherExpertise()
        self._merchant = MerchantExpertise()

        # Base stats
        self.level = 0
        self.max_hp = BASE_HP
        self.hp = BASE_HP
        self.max_mana = BASE_MANA
        self.mana = BASE_MANA

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
        self.level = self._fisher.get_level() + self._merchant.get_level()

    def update_stats(self, equipment_buffs: Buffs):
        percent_health = self.hp / self.max_hp
        updated_max_hp: int = BASE_HP
        for _ in range(self.constitution + equipment_buffs.con_buff):
            updated_max_hp += int(updated_max_hp * CON_HEALTH_SCALE)
        self.max_hp = updated_max_hp
        self.hp = int(percent_health * self.max_hp)

        percent_mana = self.mana / self.max_mana
        updated_max_mana: int = BASE_MANA
        for _ in range(self.intelligence + equipment_buffs.int_buff):
            updated_max_mana += int(updated_max_mana * INT_MANA_SCALE)
        self.max_mana = updated_max_mana
        self.mana = int(percent_mana * self.max_mana)

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

        return (
            f"HP: {hp_squares_string} ({self.hp}/{self.max_hp})\n"
            f"Mana: {mana_squares_string} ({self.mana}/{self.max_mana})"
        )

    def level_up_check(self):
        fisher_level_diff = self._fisher.level_up_check()
        merchant_level_diff = self._merchant.level_up_check()

        self.points_to_spend += fisher_level_diff + merchant_level_diff
        self.level = self._fisher.get_level() + self._merchant.get_level()

    def get_info_string(self, buffs: Buffs):
        self.level_up_check()

        fisher_level: int = self._fisher.get_level()
        merchant_level: int = self._merchant.get_level()

        def format_buff_modifier(value: int):
            if value == 0:
                return ""
            if value < 0:
                return f"({value})"
            if value > 0:
                return f"(+{value})"

        info_string = (
            f"**Base Stats**\n\n"
            f"{self.get_health_and_mana_string()}\n\n"
            f"**Classes**\n\n"
            f"Alchemist: ???\n"
            f"Fisher: Lvl. {fisher_level} *({self._fisher.get_xp_to_level(fisher_level + 1) - self._fisher.get_xp()} xp to next)*\n"
            f"Guardian: ???\n"
            f"Merchant: Lvl. {merchant_level} *({self._merchant.get_xp_to_level(merchant_level + 1) - self._merchant.get_xp()} xp to next)*\n\n"
            f"**Attributes**\n\n"
            f"Constitution: {self.constitution} {format_buff_modifier(buffs.con_buff)}\n"
            f"Strength: {self.strength} {format_buff_modifier(buffs.str_buff)}\n"
            f"Dexterity: {self.dexterity} {format_buff_modifier(buffs.dex_buff)}\n"
            f"Intelligence: {self.intelligence} {format_buff_modifier(buffs.int_buff)}\n"
            f"Luck: {self.luck} {format_buff_modifier(buffs.lck_buff)}\n"
            f"Memory: {self.memory} {format_buff_modifier(buffs.mem_buff)}"
        )

        if self.points_to_spend > 0:
            point_str = "point" if self.points_to_spend == 1 else "points"
            info_string += f"\n\n*You have {self.points_to_spend} attribute {point_str} to spend!*"

        return info_string

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._fisher = state.get("_fisher", FisherExpertise())
        self._merchant = state.get("_merchant", MerchantExpertise())

        self.level = state.get("level", 0)
        self.max_hp = state.get("max_hp", BASE_HP)
        self.hp = state.get("hp", BASE_HP)
        self.max_mana = state.get("max_mana", BASE_MANA)
        self.mana = state.get("mana", BASE_MANA)

        self.constitution = state.get("constitution", 0)
        self.strength = state.get("strength", 0)
        self.dexterity = state.get("dexterity", 0)
        self.intelligence = state.get("intelligence", 0)
        self.luck = state.get("luck", 0)
        self.memory = state.get("memory", 0)

        self.points_to_spend = state.get("points_to_spend", 0)


class AttributeButton(discord.ui.Button):
    def __init__(self, attribute: Attribute, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=attribute, row=row)
        
        self._attribute = attribute

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ExpertiseView = self.view
        if view.get_user() == interaction.user:
            response = view.add_point_to_attribute(self._attribute)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExpertiseView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._get_current_buttons()

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_current_page_info(self):
        expertise: Expertise = self.get_player().get_expertise()
        equipment: Equipment = self.get_player().get_equipment()
        expertise.level_up_check()

        return Embed(title=f"{self._user.display_name}'s Expertise (Lvl. {expertise.level})", description=expertise.get_info_string(equipment.get_total_buffs()))

    def _get_current_buttons(self):
        self.clear_items()

        player: Player = self.get_player()
        expertise: Expertise = player.get_expertise()
        equipment: Equipment = player.get_equipment()

        expertise.level_up_check()
        expertise.update_stats(equipment.get_total_buffs())

        if expertise.points_to_spend > 0:
            self.add_item(AttributeButton(Attribute.Constitution, 0))
            self.add_item(AttributeButton(Attribute.Strength, 0))
            self.add_item(AttributeButton(Attribute.Dexterity, 1))
            self.add_item(AttributeButton(Attribute.Intelligence, 1))
            self.add_item(AttributeButton(Attribute.Luck, 2))
            self.add_item(AttributeButton(Attribute.Memory, 2))

    def add_point_to_attribute(self, attribute: Attribute):
        player: Player = self.get_player()
        expertise: Expertise = player.get_expertise()
        equipment: Equipment = player.get_equipment()

        if attribute == Attribute.Constitution:
            expertise.constitution += 1
            expertise.update_stats(equipment.get_total_buffs())
        if attribute == Attribute.Strength:
            expertise.strength += 1
        if attribute == Attribute.Dexterity:
            expertise.dexterity += 1
        if attribute == Attribute.Intelligence:
            expertise.intelligence += 1
            expertise.update_stats(equipment.get_total_buffs())
        if attribute == Attribute.Luck:
            expertise.luck += 1
        if attribute == Attribute.Memory:
            expertise.memory += 1
        
        expertise.points_to_spend -= 1
        expertise.level_up_check()
        self._get_current_buttons()

        return Embed(title=f"{self._user.display_name}'s Expertise (Lvl. {expertise.level})", description=expertise.get_info_string(equipment.get_total_buffs()))

    def get_user(self):
        return self._user
