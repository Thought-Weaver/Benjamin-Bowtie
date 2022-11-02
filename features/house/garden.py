from __future__ import annotations
from audioop import add

import discord

from discord.embeds import Embed
from features.house.house import HouseRoom
from features.house.recipe import LOADED_RECIPES, Recipe
from features.shared.item import LOADED_ITEMS, ClassTag, ItemKey
from strenum import StrEnum

from typing import TYPE_CHECKING, Dict, List
from features.shared.nextbutton import NextButton

from features.shared.prevbutton import PrevButton

if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House, HouseView
    from features.inventory import Inventory
    from features.shared.item import Item
    from features.player import Player

# -----------------------------------------------------------------------------
# GARDEN PLOT
# -----------------------------------------------------------------------------

class GardenPlot():
    def __init__(self):
        self.seed: Item | None = None
        # Should be None until the growth ticks match those needed by the seed
        self.plant: Item | None = None
        self.soil: Item | None = None

        # These will be looked up based on the seed item key
        self.ticks_until_sprout: int = 0
        self.ticks_until_mature: int = 0
        self.ticks_until_death: int = 0
        self.growth_ticks: int = 0

        self.sprout_icon: str = ""
        self.mature_icon: str = ""

    def harvest(self):
        if self.seed is None:
            return None

        # If self.growth_ticks < self.ticks_until_mature, this uproots it 
        # and returns None!
        harvested_plant = self.plant
        self.reset(keep_soil=True)

        return harvested_plant

    def tick(self):
        self.growth_ticks += 1
        
        if self.growth_ticks >= self.ticks_until_death:
            self.reset(keep_soil=True)

    def reset(self, keep_soil=False):
        self.seed = None
        self.plant = None
        self.soil = None if not keep_soil else self.soil
        
        self.ticks_until_sprout = 0
        self.ticks_until_mature = 0
        self.ticks_until_death = 0
        self.growth_ticks = 0

    def plant_seed(self, seed: Item):
        # TODO: Implement this when I've figured out the lookup dicts
        pass

    def use_item(self, item: Item):
        # TODO: Implement this when I've figured out the lookup dicts
        pass

    def get_icon(self):
        if self.growth_ticks >= self.ticks_until_sprout and self.growth_ticks < self.ticks_until_mature:
            return self.sprout_icon
        
        if self.growth_ticks >= self.ticks_until_mature and self.growth_ticks < self.ticks_until_death:
            return self.mature_icon

        # Return a question mark
        return "\u2753"

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # TODO: Theoretically, only seed, soil, and growth_ticks should be loaded from state.
        # Plant, the other tick values, and icons should be loaded from the lookup dict.
        self.seed = state.get("seed", None)
        self.plant = state.get("plant", None)
        self.soil = state.get("soil", None)

        self.ticks_until_sprout = state.get("ticks_until_sprout", 0)
        self.ticks_until_mature = state.get("ticks_until_mature", 0)
        self.ticks_until_death = state.get("ticks_until_death", 0)
        self.growth_ticks = state.get("growth_ticks", 0)

        self.sprout_icon = state.get("sprout_icon", "")
        self.mature_icon = state.get("mature_icon", "")

# -----------------------------------------------------------------------------
# GARDEN VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    PlantSeed = "PlantSeed"
    UseItem = "UseItem"


class HarvestButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Harvest", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.harvest()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PlantSeedButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Plant Seed", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_plant_seed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UseItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Use Item", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_use_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExpandButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Expand ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.expand_garden()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSeedButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.select_seed(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GardenPlotButton(discord.ui.Button):
    def __init__(self, plot: GardenPlot, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, row=row, emoji=plot.get_icon())
        
        self._plot = plot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.select_plot(self._plot)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseGardenButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_garden()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmPlantSeedButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_plant_seed()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmUseItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_use_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView = view.get_house_view()
            embed = house_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=house_view)


class ExitToGardenButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: GardenView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class GardenView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view
        
        self._selected_item_index = -1
        self._selected_item: Item | None = None
        self._selected_plot: GardenPlot | None = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._intent: Intent | None = None
        
        self._PLOT_COST = 500
        self._PURCHASE_COST = 2000
        self._MAX_SIZE = 5

        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, additional: str=""):
        if self._intent == Intent.PlantSeed:
            return Embed(title="Plant Seed", description="Choose a seed to plant in this plot.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        if self._intent == Intent.UseItem:
            return Embed(title="Use Item", description="Choose an item to use on this plot.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        return Embed(title="Garden", description="You enter the garden, where you can plant seeds and harvest crops." + additional)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Storage in self._get_player().get_house().house_rooms:
            self._get_garden_buttons()
        else:
            self.add_item(PurchaseGardenButton(self._PURCHASE_COST, 0))
            self.add_item(ExitToHouseButton(0))

        self._intent = None

    def _get_garden_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        house: House = player.get_house()
        
        num_per_row = 1
        for i in range(1, self._MAX_SIZE + 1):
            if len(house.garden_plots) % i == 0:
                num_per_row = i

        for i, plot in enumerate(house.garden_plots):
            self.add_item(GardenPlotButton(plot, i % num_per_row))

        if self._selected_plot is not None:
            self.add_item(HarvestButton(min(4, num_per_row)))
            self.add_item(PlantSeedButton(min(4, num_per_row)))
            self.add_item(UseItemButton(min(4, num_per_row)))
        if len(player.get_house().garden_plots) % self._MAX_SIZE != 0:
            self.add_item(ExpandButton(self._PLOT_COST, min(4, num_per_row)))
        self.add_item(ExitToHouseButton(min(4, num_per_row)))

        self._intent = None

    def purchase_garden(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(additional="\n\n*Error: You don't have enough coins to purchase the basement storage.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Garden)
        # You get one for free!
        house.garden_plots = [GardenPlot()]
        self._get_garden_buttons()

        return self.get_embed_for_intent(additional=f"\n\n*Garden purchased! You can further expand it for {self._PLOT_COST} coins.*")
    
    def _get_plant_seed_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Gardening.Seed])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectSeedButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmPlantSeedButton(min(4, len(page_slots))))
        self.add_item(ExitToGardenButton(min(4, len(page_slots))))

    def _get_use_item_buttons(self):
        self.clear_items()

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Gardening.Soil, ClassTag.Gardening.GrowthAssist])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectSeedButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmUseItemButton(min(4, len(page_slots))))
        self.add_item(ExitToGardenButton(min(4, len(page_slots))))

    def enter_plant_seed(self):
        self._intent = Intent.PlantSeed

        self._get_plant_seed_buttons()
        return self.get_embed_for_intent()

    def enter_use_item(self):
        self._intent = Intent.UseItem

        self._get_use_item_buttons()
        return self.get_embed_for_intent()

    def harvest(self):
        if self._selected_plot is None:
            self._get_garden_buttons()
            return self.get_embed_for_intent(additional="\n\n*That plot doesn't exist and can't be harvested!*")

        harvest_result = self._selected_plot.harvest()

        self._get_garden_buttons()

        if harvest_result is None:
            return self.get_embed_for_intent(additional="\n\n*The harvest yielded nothing!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory.add_item(harvest_result)

        return self.get_embed_for_intent(additional=f"\n\n*You received {harvest_result.get_full_name()} (x{harvest_result.get_count()})*")

    def expand_garden(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()

        if len(house.garden_plots) % self._MAX_SIZE == 0:
            self._get_garden_buttons()
            return self.get_embed_for_intent(additional="\n\n*You've reached the max size for the garden!*")

        if inventory.get_coins() < self._PLOT_COST:
            return self.get_embed_for_intent(additional=f"\n\n*You don't have enough coins ({self._PLOT_COST}) to expand the garden.*")

        cur_size = 1
        for i in range(1, self._MAX_SIZE + 1):
            if len(house.garden_plots) % i == 0:
                cur_size = i

        inventory.remove_coins(self._PLOT_COST)

        for i in range(cur_size * cur_size, (cur_size + 1) * (cur_size + 1)):
            house.garden_plots.append(GardenPlot())

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*You increased the size of the garden from {cur_size * cur_size} plots to {(cur_size + 1) * (cur_size + 1)} plots!*")

    def select_plot(self, plot: GardenPlot):
        self._selected_plot = plot
        self._get_garden_buttons()
        return self.get_embed_for_intent()

    def select_seed(self, index: int, seed: Item):
        self._selected_item = seed
        self._selected_item_index = index

        self._get_plant_seed_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Plant Seed", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def tick(self):
        # TODO: Implement this once I've added the tick loop to adventures.
        pass

    def confirm_plant_seed(self):
        if self._selected_plot is None:
            return self.get_embed_for_intent(additional="\n\n*That plot doesn't exist!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        seed = inventory.remove_item(self._selected_item_index, 1)
        if seed is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        response = self._selected_plot.plant_seed(seed)

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*{response}*")

    def confirm_use_item(self):
        if self._selected_plot is None:
            return self.get_embed_for_intent(additional="\n\n*That plot doesn't exist!*")

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        item = inventory.remove_item(self._selected_item_index, 1)
        if item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        response = self._selected_plot.use_item(self._selected_item)

        self._get_garden_buttons()
        return self.get_embed_for_intent(additional=f"\n\n*{response}*")

    def next_page(self):
        self._page += 1
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_plot = None

        if self._intent == Intent.PlantSeed:
            self._get_plant_seed_buttons()
        if self._intent == Intent.UseItem:
            self._get_use_item_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_plot = None

        if self._intent == Intent.PlantSeed:
            self._get_plant_seed_buttons()
        if self._intent == Intent.UseItem:
            self._get_use_item_buttons()

        return self.get_embed_for_intent()
    
    def exit_to_main_menu(self):
        self._get_garden_buttons()
        return self.get_embed_for_intent()

    def get_bot(self):
        return self._bot

    def get_user(self):
        return self._user

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_house_view(self):
        return self._house_view
