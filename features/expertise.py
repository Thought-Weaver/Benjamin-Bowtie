from __future__ import annotations

import discord

from abc import abstractmethod
from discord.embeds import Embed
from math import ceil
from strenum import StrEnum

from features.shared.constants import BASE_HP, BASE_MANA, CON_HEALTH_SCALE, INT_MANA_SCALE
from features.shared.effect import EffectType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.equipment import Equipment
    from features.player import Player

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

# This is a convenient container for handling merging attributes from various
# sources. One day, I might update the Expertise class to use this.
class Attributes():
    def __init__(self, constitution, strength, dexterity, intelligence, luck, memory):
        self.constitution: int = constitution
        self.strength: int = strength
        self.dexterity: int = dexterity
        self.intelligence: int = intelligence
        self.luck: int = luck
        self.memory: int = memory

    def __add__(self, other: Attributes):
        return Attributes(
            self.constitution + other.constitution,
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.luck + other.luck,
            self.memory + other.memory
        )

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


class GuardianExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int) -> int:
        return ceil(30 + 30 * level * (level - 1) + 20 * (2 ** ((level - 1) / 7.0) - 1) / (1 - 2 ** (-1 / 7.0)))


class AlchemistExpertise(BaseExpertise):
    def get_xp_to_level(self, level: int) -> int:
        return ceil(20 + 20 * level * (level - 1) + 30 * (2 ** ((level - 1) / 8.0) - 1) / (1 - 2 ** (-1 / 8.0)))


class Expertise():
    def __init__(self):
        # Expertise classes
        self._fisher = FisherExpertise()
        self._merchant = MerchantExpertise()
        self._guardian = GuardianExpertise()
        self._alchemist = AlchemistExpertise()

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

    def reset_points(self):
        self.points_to_spend = self.constitution + self.strength + self.dexterity + self.intelligence + self.luck + self.memory
        self.constitution = 0
        self.strength = 0
        self.dexterity = 0
        self.intelligence = 0
        self.luck = 0
        self.memory = 0

    def add_xp_to_class(self, xp: int, expertise_class: ExpertiseClass):
        levels_gained: int = 0
        if expertise_class == ExpertiseClass.Fisher:
            levels_gained = self._fisher.add_xp(xp)
        elif expertise_class == ExpertiseClass.Merchant:
            levels_gained = self._merchant.add_xp(xp)
        elif expertise_class == ExpertiseClass.Guardian:
            levels_gained = self._guardian.add_xp(xp)
        elif expertise_class == ExpertiseClass.Alchemist:
            levels_gained = self._alchemist.add_xp(xp)
        self.points_to_spend += levels_gained
        self.level = self._fisher.get_level() + self._merchant.get_level() + self._guardian.get_level()

    def update_stats(self, combined_attributes: Attributes):
        percent_health = self.hp / self.max_hp
        updated_max_hp: int = BASE_HP
        for _ in range(combined_attributes.constitution):
            updated_max_hp += ceil(updated_max_hp * CON_HEALTH_SCALE)
        self.max_hp = updated_max_hp
        self.hp = int(percent_health * self.max_hp)

        percent_mana = self.mana / self.max_mana
        updated_max_mana: int = BASE_MANA
        for _ in range(combined_attributes.intelligence):
            updated_max_mana += ceil(updated_max_mana * INT_MANA_SCALE)
        self.max_mana = updated_max_mana
        self.mana = int(percent_mana * self.max_mana)

    def heal(self, heal_amount: int):
        self.hp = min(self.max_hp, self.hp + heal_amount)

    def damage(self, damage: int, armor: int, percent_reduct: float, equipment: Equipment):
        # TODO: This doesn't actually give any indication that you were resurrected since
        # I can't return a string this way. Should it be moved out despite the duplicated
        # code? Also, at the moment, it doesn't destroy the item afterwards.
        if any(item.get_item_effects() is not None and item.get_item_effects().has_item_effect(EffectType.ResurrectOnce) for item in equipment.get_all_equipped_items()):
            self.hp = self.max_hp
            return 0

        actual_damage = max(0, damage - armor)
        actual_damage -= int(actual_damage * percent_reduct)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def restore_mana(self, restore_amount: int):
        self.mana = min(self.max_mana, self.mana + restore_amount)
    
    def remove_mana(self, remove_amount: int):
        self.mana = max(0, self.mana - remove_amount)

    def get_health_string(self):
        hp_num_squares = ceil(self.hp / self.max_hp * 10)        
        hp_squares_string = ""

        for i in range(1, 11):
            hp_squares_string += "🟥" if i <= hp_num_squares else "⬛"

        return f"{hp_squares_string} ({self.hp}/{self.max_hp})"

    def get_mana_string(self):
        mana_num_squares = ceil(self.mana / self.max_mana * 10)
        mana_squares_string = ""

        for i in range(1, 11):
            mana_squares_string += "🟦" if i <= mana_num_squares else "⬛"

        return f"{mana_squares_string} ({self.mana}/{self.max_mana})"

    def get_health_and_mana_string(self):
        return (
            f"HP: {self.get_health_string()}\n"
            f"Mana: {self.get_mana_string()}"
        )

    def level_up_check(self):
        fisher_level_diff = self._fisher.level_up_check()
        merchant_level_diff = self._merchant.level_up_check()
        guardian_level_diff = self._guardian.level_up_check()

        self.points_to_spend += fisher_level_diff + merchant_level_diff + guardian_level_diff
        self.level = self._fisher.get_level() + self._merchant.get_level() + self._guardian.get_level()

    def get_info_string(self, attribute_mods: Attributes, armor_str: str):
        self.level_up_check()

        fisher_level: int = self._fisher.get_level()
        merchant_level: int = self._merchant.get_level()
        guardian_level: int = self._guardian.get_level()
        alchemist_level: int = self._alchemist.get_level()

        def format_buff_modifier(value: int):
            if value == 0:
                return ""
            if value < 0:
                return f"({value})"
            if value > 0:
                return f"(+{value})"

        info_string = (
            f"**Base Stats**\n\n"
            f"{self.get_health_and_mana_string()}\nEquipment: {armor_str}\n\n"
            f"**Classes**\n\n"
            f"Alchemist: Lvl. {alchemist_level} *({self._alchemist.get_xp_to_level(alchemist_level + 1) - self._alchemist.get_xp()} xp to next)*\n"
            f"Fisher: Lvl. {fisher_level} *({self._fisher.get_xp_to_level(fisher_level + 1) - self._fisher.get_xp()} xp to next)*\n"
            f"Guardian: Lvl. {guardian_level} *({self._guardian.get_xp_to_level(guardian_level + 1) - self._guardian.get_xp()} xp to next)*\n"
            f"Merchant: Lvl. {merchant_level} *({self._merchant.get_xp_to_level(merchant_level + 1) - self._merchant.get_xp()} xp to next)*\n\n"
            f"**Attributes**\n\n"
            f"Constitution: {self.constitution} {format_buff_modifier(attribute_mods.constitution)}\n"
            f"Strength: {self.strength} {format_buff_modifier(attribute_mods.strength)}\n"
            f"Dexterity: {self.dexterity} {format_buff_modifier(attribute_mods.dexterity)}\n"
            f"Intelligence: {self.intelligence} {format_buff_modifier(attribute_mods.intelligence)}\n"
            f"Luck: {self.luck} {format_buff_modifier(attribute_mods.luck)}\n"
            f"Memory: {self.memory} {format_buff_modifier(attribute_mods.memory)}"
        )

        if self.points_to_spend > 0:
            point_str = "point" if self.points_to_spend == 1 else "points"
            info_string += f"\n\n*You have {self.points_to_spend} attribute {point_str} to spend!*"

        return info_string

    def get_all_attributes(self) -> Attributes:
        return Attributes(self.constitution, self.strength, self.dexterity, self.intelligence, self.luck, self.memory)

    def get_level_for_class(self, expertise_class: ExpertiseClass) -> int:
        if expertise_class == ExpertiseClass.Fisher:
            return self._fisher.get_level()
        if expertise_class == ExpertiseClass.Guardian:
            return self._guardian.get_level()
        if expertise_class == ExpertiseClass.Merchant:
            return self._merchant.get_level()
        if expertise_class == ExpertiseClass.Alchemist:
            return self._alchemist.get_level()
        return -1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._fisher = state.get("_fisher", FisherExpertise())
        self._merchant = state.get("_merchant", MerchantExpertise())
        self._guardian = state.get("_guardian", GuardianExpertise())
        self._alchemist = state.get("_alchemist", AlchemistExpertise())

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
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, show_with_buttons: bool):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        if show_with_buttons:
            self._get_current_buttons()

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_current_page_info(self):
        expertise: Expertise = self.get_player().get_expertise()
        equipment: Equipment = self.get_player().get_equipment()
        
        expertise.level_up_check()
        expertise.update_stats(self.get_player().get_combined_attributes())
        armor_str = equipment.get_total_armor_str(self.get_player().get_expertise().level)

        # TODO: Also need to account for status effect attribute mods here and elsewhere in Expertise
        return Embed(title=f"{self._user.display_name}'s Expertise (Lvl. {expertise.level})", description=expertise.get_info_string(equipment.get_total_attribute_mods(), armor_str))

    def _get_current_buttons(self):
        self.clear_items()

        player: Player = self.get_player()
        expertise: Expertise = player.get_expertise()

        expertise.level_up_check()
        expertise.update_stats(player.get_combined_attributes())

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
            expertise.update_stats(player.get_combined_attributes())
        if attribute == Attribute.Strength:
            expertise.strength += 1
        if attribute == Attribute.Dexterity:
            expertise.dexterity += 1
        if attribute == Attribute.Intelligence:
            expertise.intelligence += 1
            expertise.update_stats(player.get_combined_attributes())
        if attribute == Attribute.Luck:
            expertise.luck += 1
        if attribute == Attribute.Memory:
            expertise.memory += 1
        
        expertise.points_to_spend -= 1
        expertise.level_up_check()
        self._get_current_buttons()

        armor_str = equipment.get_total_armor_str(self.get_player().get_expertise().level)

        return Embed(title=f"{self._user.display_name}'s Expertise (Lvl. {expertise.level})", description=expertise.get_info_string(equipment.get_total_attribute_mods(), armor_str))

    def get_user(self):
        return self._user
