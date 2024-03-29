from __future__ import annotations
from random import choice, random

import discord

from discord.embeds import Embed
from enum import StrEnum
from features.house.recipe import LOADED_RECIPES, Recipe, RecipeKey
from features.shared.enums import ClassTag, HouseRoom
from features.shared.item import LOADED_ITEMS, ItemKey, Rarity

from typing import TYPE_CHECKING, Dict, List
from features.shared.nextbutton import NextButton

from features.shared.prevbutton import PrevButton
from features.stats import Stats

if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House, HouseView
    from features.inventory import Inventory
    from features.shared.item import Item
    from features.player import Player

# -----------------------------------------------------------------------------
# ALCHEMY CHAMBER VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Alchemize = "Alchemize"
    Recipes = "Recipes"
    Cupboard = "Cupboard"
    Store = "Store"
    Retrieve = "Retrieve"


class EnterAlchemizeButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Alchemize", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.enter_alchemize()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterRecipesButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Recipes", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.enter_recipes()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterCupboardButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cupboard", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.enter_cupboard()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView | None = view.get_house_view()
            if house_view is not None:
                embed = house_view.get_initial_embed()
                await interaction.response.edit_message(content=None, embed=embed, view=house_view)


class ExitWithIntentButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            embed = view.exit_with_intent()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class StoreButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_cupboard_store()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RetrieveButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_cupboard_retrieve()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class SelectInventoryItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.select_inventory_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectRecipeButton(discord.ui.Button):
    def __init__(self, recipe: Recipe, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{recipe.name}", row=row, emoji=recipe.icon)
        
        self._recipe = recipe

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.select_recipe(self._recipe)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectCupboardItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.select_cupboard_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.store()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.store_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AddItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Add", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.add_alchemizing_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RemoveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Remove", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.remove_alchemizing_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectalchemizingIngredientButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.select_alchemizing_ingredient(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmRecipeButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.use_recipe()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmRecipeAllButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Alchemize All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.use_recipe(make_all=True)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmalchemizingButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Alchemize", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.try_alchemizing()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseAlchemyChamberButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: AlchemyChamberView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_alchemy_chamber()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AlchemyChamberView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView | None):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view

        self._intent: Intent | None = None
        self._selected_item: Item | None = None
        self._selected_item_index: int = -1
        self._selected_recipe: Recipe | None = None

        self._current_alchemizing: Dict[ItemKey, int] = {}

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._PURCHASE_COST = 2500
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Cupboard:
            return Embed(title="Cupboard", description="Store ingredients or retrieve them from your cupboard." + error)
        if self._intent == Intent.Store:
            return Embed(title="Cupboard (Storing)", description="Choose an item to store in the cupboard.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Retrieve:
            return Embed(title="Cupboard (Retrieving)", description="Choose an item to retrieve from the cupboard.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Alchemize:
            current_alchemizing_str = self.get_current_alchemizing_str()
            current_alchemizing_display = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{current_alchemizing_str}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if current_alchemizing_str != "" else ""
            return Embed(title="Alchemize", description=f"{current_alchemizing_display}Mix together ingredients from your inventory and attempt to create a potion.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Recipes:
            return Embed(title="Recipes", description="Choose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons." + error)
        return Embed(title="Alchemy Chamber", description="You enter the alchemy chamber, where you can use an existing recipe to alchemize, try making something from any ingredients you have in your inventory, or store ingredients in the cupboard." + error)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Alchemy in self._get_player().get_house().house_rooms:
            self.add_item(EnterRecipesButton(0))
            self.add_item(EnterAlchemizeButton(1))
            self.add_item(EnterCupboardButton(2))
            if self._house_view is not None:
                self.add_item(ExitToHouseButton(3))
        else:
            self.add_item(PurchaseAlchemyChamberButton(self._PURCHASE_COST, 0))
            if self._house_view is not None:
                self.add_item(ExitToHouseButton(0))

        self._intent = None

    def purchase_alchemy_chamber(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(error="\n\n*Error: You don't have enough coins to purchase the alchemy chamber.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Alchemy)
        self._display_initial_buttons()

        return self.get_embed_for_intent(error="\n\n*Alchemy chamber purchased! You can now alchemize and store ingredients.*")

    def enter_cupboard(self):
        self.clear_items()
        self.add_item(StoreButton(0))
        self.add_item(RetrieveButton(1))
        self.add_item(ExitWithIntentButton(2))

        self._intent = Intent.Cupboard

        return self.get_embed_for_intent()

    def enter_cupboard_store(self):
        self.clear_items()
        self._get_store_cupboard_buttons()

        self._intent = Intent.Store

        return self.get_embed_for_intent()

    def _get_store_cupboard_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.PotionIngredient, ClassTag.Valuable.Gemstone])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectInventoryItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(StoreItemButton(min(4, len(page_slots))))
            self.add_item(StoreAllItemButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_cupboard_retrieve(self):
        self.clear_items()
        self._get_retrieve_cupboard_buttons()

        self._intent = Intent.Retrieve

        return self.get_embed_for_intent()

    def _get_retrieve_cupboard_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_house().alchemy_chamber_cupboard
        inventory_slots = inventory.get_inventory_slots()

        page_slots = inventory_slots[self._page * self._NUM_PER_PAGE:min(len(inventory_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(SelectCupboardItemButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(RetrieveItemButton(min(4, len(page_slots))))
            self.add_item(RetrieveAllItemButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def _get_alchemize_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        special_num_per_page: int = self._NUM_PER_PAGE - 1

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.PotionIngredient, ClassTag.Valuable.Gemstone])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * special_num_per_page:min(len(filtered_items), (self._page + 1) * special_num_per_page)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * special_num_per_page)]
            self.add_item(SelectalchemizingIngredientButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(special_num_per_page, len(page_slots))))
        if len(filtered_items) - special_num_per_page * (self._page + 1) > 0:
            self.add_item(NextButton(min(special_num_per_page, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            if self._current_alchemizing.get(self._selected_item.get_key(), 0) < inventory_slots[self._selected_item_index].get_count():
                self.add_item(AddItemButton(min(special_num_per_page, len(page_slots))))
            if self._current_alchemizing.get(self._selected_item.get_key(), 0) > 0:
                self.add_item(RemoveItemButton(min(special_num_per_page, len(page_slots))))
        self.add_item(ConfirmalchemizingButton(min(4, len(page_slots) + 1)))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots) + 1)))

    def enter_alchemize(self):
        self.clear_items()
        self._get_alchemize_buttons()

        self._intent = Intent.Alchemize

        return self.get_embed_for_intent()

    def enter_recipes(self):
        self.clear_items()
        self._get_recipe_buttons()

        self._intent = Intent.Recipes

        return self.get_embed_for_intent()

    def _get_recipe_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        recipes: List[Recipe] = player.get_house().crafting_recipes
        filtered_recipes: List[Recipe] = list(filter(lambda r: r.any_output_has_any_class_tag([ClassTag.Consumable.Potion, ClassTag.Ingredient.PotionIngredient]), recipes))

        page_slots = filtered_recipes[self._page * self._NUM_PER_PAGE:min(len(filtered_recipes), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, recipe in enumerate(page_slots):
            self.add_item(SelectRecipeButton(recipe, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_recipes) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_recipe is not None:
            self.add_item(ConfirmRecipeButton(min(4, len(page_slots))))
            self.add_item(ConfirmRecipeAllButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def next_page(self):
        self._page += 1
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Store:
            self._get_store_cupboard_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_cupboard_buttons()
        if self._intent == Intent.Alchemize:
            self._get_alchemize_buttons()
        if self._intent == Intent.Recipes:
            self._get_recipe_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Store:
            self._get_store_cupboard_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_cupboard_buttons()
        if self._intent == Intent.Alchemize:
            self._get_alchemize_buttons()
        if self._intent == Intent.Recipes:
            self._get_recipe_buttons()

        return self.get_embed_for_intent()

    def select_inventory_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_store_cupboard_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Cupboard (Storing)", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def select_recipe(self, recipe: Recipe):
        self._selected_recipe = recipe

        self._get_recipe_buttons()
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that recipe changed or it's no longer available.*")

        num_can_be_created = self._selected_recipe.num_can_be_made(self._get_player().get_inventory())

        return Embed(title="Recipes", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_recipe}\nYou have enough ingredients to make {num_can_be_created}.\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def select_cupboard_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_retrieve_cupboard_buttons()

        player: Player = self._get_player()
        cupboard_slots: List[Item] = player.get_house().alchemy_chamber_cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Cupboard (Retrieving)", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def retrieve(self):
        player: Player = self._get_player()
        cupboard: Inventory = player.get_house().alchemy_chamber_cupboard
        cupboard_slots: List[Item] = cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = cupboard.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_cupboard_buttons()

        return Embed(title="Cupboard (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved 1 {removed_item.get_full_name()} and added it to your inventory.*")

    def retrieve_all(self):
        player: Player = self._get_player()
        cupboard: Inventory = player.get_house().alchemy_chamber_cupboard
        cupboard_slots: List[Item] = cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = cupboard.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_cupboard_buttons()

        return Embed(title="Cupboard (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved {removed_item.get_count()} {removed_item.get_full_name()} and added to your inventory.*")

    def store(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        cupboard: Inventory = player.get_house().alchemy_chamber_cupboard
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        cupboard.add_item(removed_item)
        self._get_store_cupboard_buttons()

        return Embed(title="Cupboard (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored 1 {removed_item.get_full_name()} and added it to the cupboard.*")

    def store_all(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        cupboard: Inventory = player.get_house().alchemy_chamber_cupboard
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        cupboard.add_item(removed_item)
        self._get_store_cupboard_buttons()

        return Embed(title="Cupboard (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored {removed_item.get_count()} {removed_item.get_full_name()} and added to the cupboard.*")

    def get_current_alchemizing_str(self):
        input_strs = []
        for item_key, quantity in self._current_alchemizing.items():
            if quantity > 0:
                item_data = LOADED_ITEMS.get_item_state(item_key)
                input_strs.append(f"{item_data['icon']} {item_data['name']} (x{quantity})\n")
        return '\n'.join(input_strs)

    def add_alchemizing_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_alchemizing[item_key] = self._current_alchemizing.get(item_key, 0) + 1

        current_alchemizing_str = self.get_current_alchemizing_str()
        current_alchemizing_display = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{current_alchemizing_str}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if current_alchemizing_str != "" else ""
        return Embed(title="Alchemize", description=f"{current_alchemizing_display}Mix together ingredients from your inventory and attempt to create a potion.\n\nNavigate through the items using the Prev and Next buttons.")

    def remove_alchemizing_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_alchemizing[item_key] = max(self._current_alchemizing.get(item_key, 0) - 1, 0)

        current_alchemizing_str = self.get_current_alchemizing_str()
        current_alchemizing_display = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{current_alchemizing_str}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if current_alchemizing_str != "" else ""
        return Embed(title="Alchemize", description=f"{current_alchemizing_display}Mix together ingredients from your inventory and attempt to create a potion.\n\nNavigate through the items using the Prev and Next buttons.")

    def select_alchemizing_ingredient(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_alchemize_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        current_alchemizing_str = self.get_current_alchemizing_str()
        current_alchemizing_display = f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{current_alchemizing_str}᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n" if current_alchemizing_str != "" else ""
        return Embed(title="Alchemize", description=f"{current_alchemizing_display}Mix together ingredients from your inventory and attempt to create a potion.\n\nNavigate through the items using the Prev and Next buttons.")

    def use_recipe(self, make_all: bool=False):
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that recipe changed or it's no longer available.*")

        # TODO: This raises an interesting question: Should I search the inventory for anything matching the keys? The problem is what if some item has a
        # different set of state tags? Shouldn't I use whatever the player pressed from their inventory? But then again, the player can't discern which
        # items have state tags from the buttons, so perhaps this is a later problem.

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()

        num_to_make = 1 if not make_all else self._selected_recipe.num_can_be_made(self._get_player().get_inventory())

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have one of the items for that recipe.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity * num_to_make:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items.*")

        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            inventory.remove_item(index, quantity * num_to_make)

        xp_strs = []
        for xp_class, xp in self._selected_recipe.xp_reward_for_use.items():
            final_xp = player.get_expertise().add_xp_to_class(xp * num_to_make, xp_class, player.get_equipment())
            xp_strs.append(f"*(+{final_xp} {xp_class} xp)*")
        xp_strs_joined = '\n'.join(xp_strs)
        xp_display = f"\n{xp_strs_joined}" if len(xp_strs) > 0 else ""

        stats: Stats = player.get_stats()

        output_strs = []
        for output_key, quantity in self._selected_recipe.outputs.items():
            new_item = LOADED_ITEMS.get_new_item(output_key)
            # There's one by default, so add any extra as needed
            new_item.add_amount((quantity * num_to_make) - 1)
            inventory.add_item(new_item)
            output_strs.append(f"{new_item.get_full_name()} (x{quantity * num_to_make})\n")

            if new_item.get_rarity() == Rarity.Common:
                stats.crafting.common_items_alchemized += num_to_make
            if new_item.get_rarity() == Rarity.Uncommon:
                stats.crafting.uncommon_items_alchemized += num_to_make
            if new_item.get_rarity() == Rarity.Rare:
                stats.crafting.rare_items_alchemized += num_to_make
            if new_item.get_rarity() == Rarity.Epic:
                stats.crafting.epic_items_alchemized += num_to_make
            if new_item.get_rarity() == Rarity.Legendary:
                stats.crafting.legendary_items_alchemized += num_to_make
            if new_item.get_rarity() == Rarity.Artifact:
                stats.crafting.artifact_items_alchemized += num_to_make
        output_display = '\n'.join(output_strs)

        return Embed(title="Recipes", description=f"Alchemizing successful! You received:\n\n{output_display}{xp_display}\n\nChoose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons.")

    def try_alchemizing(self):
        if len(self._current_alchemizing.items()) == 0:
            self._get_alchemize_buttons()
            return self.get_embed_for_intent(error="\n\n*Error: You need to add at least one item.*")

        # TODO: See above also here.

        player: Player = self._get_player()
        player_recipe_keys: List[RecipeKey] = list(map(lambda r: r.key, player.get_house().crafting_recipes))
        inventory: Inventory = player.get_inventory()

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._current_alchemizing.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                self._get_alchemize_buttons()
                return self.get_embed_for_intent(error="\n\n*Error: You don't have at least one of the items needed to alchemize that.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity:
                self._get_alchemize_buttons()
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items to alchemize that.*")

        found_recipe = None
        new_recipe = False
        for recipe_key in LOADED_RECIPES.get_all_keys():
            recipe = LOADED_RECIPES.get_new_recipe(recipe_key)
            if recipe.inputs == self._current_alchemizing:
                # Assume uniqueness and that the first valid matching is the result
                if recipe.key not in player_recipe_keys:
                    new_recipe = True
                    player.get_house().crafting_recipes.append(recipe)
                found_recipe = recipe
                break

        for input_key, quantity in self._current_alchemizing.items():
            index = inventory.search_by_key(input_key)
            for _ in range(quantity):
                inventory.remove_item(index, 1)

        if found_recipe is None:
            self._get_alchemize_buttons()

            alchemizing_failed_info: str = ""
            for input_key, quantity in self._current_alchemizing.items():
                if quantity > 0:
                    recipe_key: RecipeKey | None = LOADED_RECIPES.get_random_recipe_using_item(input_key, [ClassTag.Consumable.Potion, ClassTag.Ingredient.PotionIngredient], player_recipe_keys)
                    if recipe_key is not None:
                        recipe: Recipe = LOADED_RECIPES.get_new_recipe(recipe_key)

                        # Potion recipes only have a single output
                        item_key: ItemKey | None = None
                        for output_key in recipe.outputs:
                            item_key = output_key
                            break

                        if item_key is None:
                            continue

                        resulting_item: Item = LOADED_ITEMS.get_new_item(item_key)
                        item_effects = resulting_item.get_item_effects()
                        
                        if item_effects is not None:
                            amount_adj_str: str = ""
                            if recipe.inputs[input_key] - quantity == 0:
                                amount_adj_str = "\u2705"
                            elif recipe.inputs[input_key] - quantity > 0:
                                amount_adj_str = "\u2B06\uFE0F"
                            else:
                                amount_adj_str = "\u2B07\uFE0F"

                            # This is a bit hacky
                            effect_level: str = "Standard"
                            if "superior" in item_key:
                                effect_level = "Superior"
                            elif "greater" in item_key:
                                effect_level = "Greater"
                            elif "lesser" in item_key:
                                effect_level = "Lesser"

                            input_item: Item = LOADED_ITEMS.get_new_item(input_key)
                            # Consumable effects only exist on the permanent parameter
                            if len(item_effects.permanent) > 0:
                                effect = choice(item_effects.permanent)
                                alchemizing_failed_info += f"\n{input_item.get_full_name()} (x{quantity}): {effect.get_descriptive_name()} ({effect_level}) {amount_adj_str}"

            if alchemizing_failed_info != "":
                alchemizing_failed_info = f"\n\nYou learned:\n{alchemizing_failed_info}"

            return Embed(title="Alchemize", description=f"You attempt to mix these ingredients together, but nothing happens.{alchemizing_failed_info}\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nMix together ingredients from your inventory and attempt to create a potion.\n\nNavigate through your recipes using the Prev and Next buttons.")
        else:
            self._current_cooking = {}

        new_recipe_str = f"\n*You acquired the {found_recipe.get_name_and_icon()} recipe!*\n" if new_recipe else ""

        xp_strs = []
        for xp_class, xp in found_recipe.xp_reward_for_use.items():
            final_xp = player.get_expertise().add_xp_to_class(xp, xp_class, player.get_equipment())
            xp_strs.append(f"*(+{final_xp} {xp_class} xp)*")
        xp_display = '\n'.join(xp_strs)
        if len(xp_strs) > 0:
            xp_display += "\n"

        stats: Stats = player.get_stats()

        output_strs = []
        for output_key, quantity in found_recipe.outputs.items():
            new_item = LOADED_ITEMS.get_new_item(output_key)
            # There's one by default, so add any extra as needed
            new_item.add_amount(quantity - 1)
            inventory.add_item(new_item)
            output_strs.append(f"{new_item.get_full_name()} (x{quantity})\n")

            if new_item.get_rarity() == Rarity.Common:
                stats.crafting.common_items_alchemized += 1
            if new_item.get_rarity() == Rarity.Uncommon:
                stats.crafting.uncommon_items_alchemized += 1
            if new_item.get_rarity() == Rarity.Rare:
                stats.crafting.rare_items_alchemized += 1
            if new_item.get_rarity() == Rarity.Epic:
                stats.crafting.epic_items_alchemized += 1
            if new_item.get_rarity() == Rarity.Legendary:
                stats.crafting.legendary_items_alchemized += 1
            if new_item.get_rarity() == Rarity.Artifact:
                stats.crafting.artifact_items_alchemized += 1
        output_display = '\n'.join(output_strs)

        if new_recipe:
            stats.crafting.alchemy_recipes_discovered += 1

        self._get_alchemize_buttons()

        return Embed(title="Alchemize", description=f"Alchemizing successful! You received:\n\n{output_display}\n{xp_display}{new_recipe_str}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nChoose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons.")

    def exit_with_intent(self):
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None
        self._page = 0
        self._current_alchemizing = {}

        if self._intent == Intent.Alchemize or self._intent == Intent.Recipes or self._intent == Intent.Cupboard:
            self._intent = None
            self._display_initial_buttons()
            return self.get_embed_for_intent()
        if self._intent == Intent.Store or self._intent == Intent.Retrieve:
            return self.enter_cupboard()

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
