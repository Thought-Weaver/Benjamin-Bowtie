from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands
from features.house.alchemy import AlchemyChamberView
from features.house.recipe import Recipe
from features.inventory import Inventory
from features.mail import MailboxView
from strenum import StrEnum

from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player

# -----------------------------------------------------------------------------
# ENUMS
# -----------------------------------------------------------------------------

class HouseRoom(StrEnum):
    Unknown = "Unknown"
    Study = "Study"
    Alchemy = "Alchemy"
    Workshop = "Workshop"
    Kitchen = "Kitchen"
    Garden = "Garden"
    Storage = "Storage"

# -----------------------------------------------------------------------------
# HOUSE CLASS
# -----------------------------------------------------------------------------

class House():
    def __init__(self):
        self.house_rooms: List[HouseRoom] = []
        self.crafting_recipes: List[Recipe] = []

        self.storage_bins: Dict[str, Inventory] = {}
        self.kitchen_cupboard: Inventory = Inventory()
        self.workshop_storage: Inventory = Inventory()
        self.study_storage: Inventory = Inventory()

        # TODO: Garden state will need to be kept here

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.house_rooms = state.get("house_rooms", [])
        self.crafting_recipes = state.get("crafting_recipes", [])

        self.storage_bins = state.get("storage_bins", {})
        self.kitchen_cupboard = state.get("kitchen_cupboard", [])
        self.workshop_storage = state.get("workshop_storage", [])
        self.study_storage = state.get("study_storage", [])

# -----------------------------------------------------------------------------
# HOUSE VIEW
# -----------------------------------------------------------------------------

from features.house.kitchen import KitchenView

class KitchenButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Kitchen", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: KitchenView = KitchenView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user(), view)
            embed = new_view.get_embed_for_intent()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class GardenButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Garden", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: MailboxView = MailboxView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = Embed()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class StorageButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Storage", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: MailboxView = MailboxView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = Embed()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class WorkshopButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Workshop", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: MailboxView = MailboxView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = Embed()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class StudyButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Study", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: MailboxView = MailboxView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = Embed()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class AlchemyChamberButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Alchemy Chamber", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: AlchemyChamberView = AlchemyChamberView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user(), view)
            embed = Embed()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class MailboxButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Mailbox", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            new_view: MailboxView = MailboxView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = new_view.get_current_page_info()
            await interaction.response.edit_message(content=None, embed=embed, view=new_view)


class RestButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.blurple, label="Rest", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: HouseView = self.view
        if interaction.user == view.get_user():
            response = view.rest()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class HouseView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, context: commands.Context):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._context = context

        self._page = 0
        self._NUM_PER_PAGE = 4
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(title="A Nice Home", description="")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(StudyButton(0))
        self.add_item(AlchemyChamberButton(0))
        self.add_item(WorkshopButton(0))
        self.add_item(GardenButton(1))
        self.add_item(KitchenButton(1))
        self.add_item(MailboxButton(2))
        self.add_item(StorageButton(2))
        self.add_item(RestButton(3))

    def rest(self):
        # TODO: Implement resting mechanic and out-of-combat status effects
        pass

    def get_bot(self):
        return self._bot

    def get_user(self):
        return self._user

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
