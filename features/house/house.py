from __future__ import annotations
import random

import discord

from discord.embeds import Embed
from discord.ext import commands
from features.house.garden import MUTATION_PROBS
from features.inventory import Inventory

from features.shared.constants import MAX_GARDEN_SIZE
from features.shared.enums import HouseRoom
from features.shared.item import LOADED_ITEMS

from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.garden import GardenPlot
    from features.house.recipe import Recipe
    from features.player import Player

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
        self.alchemy_chamber_cupboard: Inventory = Inventory()

        self.garden_plots: List[GardenPlot] = []

    def tick_garden(self):
        if HouseRoom.Garden not in self.house_rooms:
            return

        size = 1
        for i in range(1, MAX_GARDEN_SIZE + 1):
            if len(self.garden_plots) % i == 0:
                size = i

        # Do mutations first rather than as the plots tick to avoid plant death
        # and confusing results for the player.
        if size > 1:
            for i, plot in enumerate(self.garden_plots):
                if plot.seed is not None:
                    continue

                neighbors: List[GardenPlot] = []
                if i - size >= 0:
                    neighbors.append(self.garden_plots[i - size])
                if i % size != 0:
                    neighbors.append(self.garden_plots[i - 1])
                if (i + 1) % size != 0:
                    neighbors.append(self.garden_plots[i + 1])
                if i + size < size:
                    neighbors.append(self.garden_plots[i + size])
                if i - size - 1 >= 0 and i % size != 0:
                    neighbors.append(self.garden_plots[i - size - 1])
                if i - size + 1 >= 0 and (i + 1) % size != 0:
                    neighbors.append(self.garden_plots[i - size + 1])
                if i + size - 1 < size and i % size != 0:
                    neighbors.append(self.garden_plots[i + size - 1])
                if i + size + 1 < size and (i + 1) % size != 0:
                    neighbors.append(self.garden_plots[i + size + 1])
        
                plant_keys = [neighbor_plot.seed_data.result if (neighbor_plot.seed_data is not None and neighbor_plot.is_mature()) else "" for neighbor_plot in neighbors]

                min_prob = 1
                min_prob_result = None
                for required_plants, possible_result in MUTATION_PROBS.items():
                    if required_plants[0] in plant_keys and required_plants[1] in plant_keys:
                        if random.random() < possible_result[1]:
                            # Favor the result with the lowest probability if random chance has willed it.
                            if possible_result[1] <= min_prob:
                                min_prob = possible_result[1]
                                min_prob_result = possible_result[0]
                
                if min_prob_result is not None:
                    seed = LOADED_ITEMS.get_new_item(min_prob_result)
                    self.garden_plots[i].plant_seed(seed)

        for plot in self.garden_plots:
            plot.tick()

    def tick(self):
        self.tick_garden()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.house_rooms = state.get("house_rooms", [])
        self.crafting_recipes = state.get("crafting_recipes", [])

        self.storage_bins = state.get("storage_bins", {})
        self.kitchen_cupboard = state.get("kitchen_cupboard", Inventory())
        self.workshop_storage = state.get("workshop_storage", Inventory())
        self.study_storage = state.get("study_storage", Inventory())
        self.alchemy_chamber_cupboard = state.get("alchemy_chamber_cupboard", Inventory())

        self.garden_plots = state.get("garden_plots", [])

# -----------------------------------------------------------------------------
# HOUSE VIEW
# -----------------------------------------------------------------------------

from features.house.alchemy import AlchemyChamberView
from features.house.kitchen import KitchenView
from features.mail import MailboxView

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
