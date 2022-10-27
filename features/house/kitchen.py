from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands
from features.house.recipe import LOADED_RECIPES, Recipe
from features.inventory import Inventory
from features.shared.item import LOADED_ITEMS, ClassTag, Item, ItemKey
from strenum import StrEnum

from typing import TYPE_CHECKING, Dict, List
from features.shared.nextbutton import NextButton

from features.shared.prevbutton import PrevButton

if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import HouseView
    from features.player import Player

# -----------------------------------------------------------------------------
# KITCHEN VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    CookOptions = "CookOptions"
    Cook = "Cook"
    Recipes = "Recipes"
    Cupboard = "Cupboard"
    Store = "Store"
    Retrieve = "Retrieve"


class EnterCookOptionsButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cook", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_cook_options()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterCookButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cook", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_cook()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterRecipesButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Recipes", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_recipes()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterCupboardButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Cupboard", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.enter_cupboard()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView = view.get_house_view()
            embed = house_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=house_view)


class ExitWithIntentButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            embed = view.exit_with_intent()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class StoreButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_cupboard_store()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RetrieveButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
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
        
        view: KitchenView = self.view
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
        
        view: KitchenView = self.view
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
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.select_cupboard_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveAllItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AddItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.add_cooking_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RemoveItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.remove_cooking_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectCookingIngredientButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.select_cooking_ingredient(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmRecipeButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.use_recipe()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmCookingButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Cook", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: KitchenView = self.view
        if interaction.user == view.get_user():
            response = view.try_cooking()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class KitchenView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView):
        super().__init__(timeout=900)

        # TODO: Pass in the parent view instance so I can have an exit button?

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view

        self._intent: Intent | None = None
        self._selected_item: Item | None = None
        self._selected_item_index: int = -1
        self._selected_recipe: Recipe | None = None

        self._current_cooking: Dict[ItemKey, int] = {}

        self._page = 0
        self._NUM_PER_PAGE = 4
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        # TODO: Handle the case where the kitchen hasn't been purchased yet.
        return Embed(title="Kitchen", description="")

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.CookOptions:
            return Embed(title="Cooking Options", description="Use an existing recipe or try to make something from any ingredients you have in your inventory." + error)
        if self._intent == Intent.Cupboard:
            return Embed(title="Cupboard", description="Store ingredients in your cupboard or retrieve them." + error)
        if self._intent == Intent.Store:
            return Embed(title="Cupboard (Storing)", description="Choose an item to store in the cupboard.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Retrieve:
            return Embed(title="Cupboard (Retrieving)", description="Choose an item to retrieve in the cupboard.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Cook:
            return Embed(title="Cook", description="Mix together ingredients from your inventory and attempt to cook something.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Recipes:
            return Embed(title="Recipes", description="Choose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons." + error)
        return Embed(title="Kitchen", description=error)

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterCookOptionsButton(0))
        self.add_item(EnterCupboardButton(1))
        self.add_item(ExitToHouseButton(2))

        self._intent = None

    def enter_cook_options(self):
        self.clear_items()
        self.add_item(EnterRecipesButton(0))
        self.add_item(EnterCookButton(1))
        self.add_item(ExitWithIntentButton(2))

        self._intent = Intent.CookOptions

        return self.get_embed_for_intent()

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

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.Ingredient])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectInventoryItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_cupboard_retrieve(self):
        self.clear_items()
        self._get_retrieve_cupboard_buttons()

        self._intent = Intent.Retrieve

        return self.get_embed_for_intent()

    def _get_retrieve_cupboard_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_house().kitchen_cupboard
        inventory_slots = inventory.get_inventory_slots()

        page_slots = inventory_slots[self._page * self._NUM_PER_PAGE:min(len(inventory_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(SelectCupboardItemButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(RetrieveItemButton(self._selected_item_index, self._selected_item, min(4, len(page_slots))))
            self.add_item(RetrieveAllItemButton(self._selected_item_index, self._selected_item, min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def _get_cook_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_house().kitchen_cupboard
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.Ingredient])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectCookingIngredientButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            if self._current_cooking.get(self._selected_item.get_key(), 0) < inventory_slots[self._selected_item_index].get_count():
                self.add_item(AddItemButton(self._selected_item_index, self._selected_item, min(4, len(page_slots))))
            if self._current_cooking.get(self._selected_item.get_key(), 0) > 0:
                self.add_item(RemoveItemButton(self._selected_item_index, self._selected_item, min(4, len(page_slots))))
        self.add_item(ConfirmCookingButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_cook(self):
        self.clear_items()
        self._get_cook_buttons()

        self._intent = Intent.Cook

        return self.get_embed_for_intent()

    def enter_recipes(self):
        self.clear_items()
        self._get_recipe_buttons()

        self._intent = Intent.Cook

        return self.get_embed_for_intent()

    def _get_recipe_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        recipes: List[Recipe] = player.get_house().crafting_recipes
        filtered_recipes: List[Recipe] = list(filter(lambda r: r.any_output_has_any_class_tag([ClassTag.Consumable.Food]), recipes))

        page_slots = filtered_recipes[self._page * self._NUM_PER_PAGE:min(len(filtered_recipes), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, recipe in enumerate(page_slots):
            self.add_item(SelectRecipeButton(recipe, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_recipes) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_recipe is not None:
            self.add_item(ConfirmRecipeButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Store:
            self._get_store_cupboard_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_cupboard_buttons()
        if self._intent == Intent.Cook:
            self._get_cook_buttons()
        if self._intent == Intent.Recipes:
            self._get_recipe_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Store:
            self._get_store_cupboard_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_cupboard_buttons()
        if self._intent == Intent.Cook:
            pass
        if self._intent == Intent.Recipes:
            pass

        return self.get_embed_for_intent()

    def select_inventory_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_store_cupboard_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Cupboard (Storing)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def select_recipe(self, recipe: Recipe):
        self._selected_recipe = recipe

        self._get_recipe_buttons()
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that recipe changed or it's no longer available.*")
        return Embed(title="Recipes", description=f"──────────\n{self._selected_recipe}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def select_cupboard_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_retrieve_cupboard_buttons()

        player: Player = self._get_player()
        cupboard_slots: List[Item] = player.get_house().kitchen_cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Cupboard (Retrieving)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def retrieve(self):
        player: Player = self._get_player()
        cupboard: Inventory = player.get_house().kitchen_cupboard
        cupboard_slots: List[Item] = cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = cupboard.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)

        return Embed(title="Cupboard (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved 1 {removed_item.get_full_name()} and added it to your inventory.*")

    def retrieve_all(self):
        player: Player = self._get_player()
        cupboard: Inventory = player.get_house().kitchen_cupboard
        cupboard_slots: List[Item] = cupboard.get_inventory_slots()
        if self._selected_item is None or cupboard_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = cupboard.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)

        return Embed(title="Cupboard (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved {removed_item.get_count()} {removed_item.get_full_name()} and added to your inventory.*")

    def get_current_cooking_str(self):
        input_strs = []
        for item_key, quantity in self._current_cooking.items():
            if quantity > 0:
                item_data = LOADED_ITEMS.get_item_state(item_key)
                input_strs.append(f"{item_data['icon']} {item_data['name']} (x{quantity})\n")
        return '\n'.join(input_strs)

    def add_cooking_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_cooking[item_key] = self._current_cooking.get(item_key, 0) + 1

        current_cooking_str = self.get_current_cooking_str()
        return Embed(title="Cook", description=f"──────────\n{current_cooking_str}\n──────────\n\nMix together ingredients from your inventory and attempt to cook something.\n\nNavigate through the items using the Prev and Next buttons.")

    def remove_cooking_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_cooking[item_key] = max(self._current_cooking.get(item_key, 0) - 1, 0)

        current_cooking_str = self.get_current_cooking_str()
        return Embed(title="Cook", description=f"──────────\n{current_cooking_str}\n──────────\n\nMix together ingredients from your inventory and attempt to cook something.\n\nNavigate through the items using the Prev and Next buttons.")

    def select_cooking_ingredient(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_cook_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        current_cooking_str = self.get_current_cooking_str()
        return Embed(title="Cook", description=f"──────────\n{current_cooking_str}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def use_recipe(self):
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that recipe changed or it's no longer available.*")

        # TODO: This raises an interesting question: Should I search the inventory for anything matching the keys? The problem is what if some item has a
        # different set of state tags? Shouldn't I use whatever the player pressed from their inventory? But then again, the player can't discern which
        # items have state tags from the buttons, so perhaps this is a later problem.

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have one of the items for that recipe.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items.*")

        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            inventory.remove_item(index, quantity)

        xp_strs = []
        for xp_class, xp in self._selected_recipe.xp_reward_for_use.items():
            xp_strs.append(f"*(+{xp} {xp_class} xp)*")
            player.get_expertise().add_xp_to_class(xp, xp_class)
        xp_display = '\n'.join(xp_strs)

        output_strs = []
        for output_key, quantity in self._selected_recipe.outputs.items():
            new_item = LOADED_ITEMS.get_new_item(output_key)
            # There's one by default, so add any extra as needed
            new_item.add_amount(quantity - 1)
            inventory.add_item(new_item)
            output_strs.append(f"{new_item.get_full_name()} (x{quantity})\n")
        output_display = '\n'.join(output_strs)

        for xp_class, xp in self._selected_recipe.xp_reward_for_use.items():
            player.get_expertise().add_xp_to_class(xp, xp_class)
        
        return Embed(title="Recipes", description=f"Cooking successful! You received:\n\n{output_display}\n\n{xp_display}\n\nChoose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons.")

    def try_cooking(self):
        if len(self._current_cooking.items()) == 0:
            return self.get_embed_for_intent(error="\n\n*Error: You need to add at least one item.*")

        # TODO: See above also here.

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._current_cooking.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have at least one of the items needed to cook that.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items to cook that.*")

        for input_key, quantity in self._current_cooking.items():
            index = inventory.search_by_key(input_key)
            inventory.remove_item(index, quantity)

        found_recipe = None
        new_recipe = False
        for recipe_key in LOADED_RECIPES.get_all_keys():
            recipe = LOADED_RECIPES.get_new_recipe(recipe_key)
            if recipe.inputs == self._current_cooking:
                # Assume uniqueness and that the first valid matching is the result
                if recipe not in player.get_house().crafting_recipes:
                    new_recipe = True
                    player.get_house().crafting_recipes.append(recipe)
                found_recipe = recipe
                break

        if found_recipe is None:
            return Embed(title="Cook", description=f"You attempt to mix these ingredients together, but nothing happens.\n\nChoose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons.")
            
        new_recipe_str = f"You acquired the {found_recipe.get_name_and_icon()} recipe!\n\n" if new_recipe else ""

        xp_strs = []
        for xp_class, xp in found_recipe.xp_reward_for_use.items():
            xp_strs.append(f"*(+{xp} {xp_class} xp)*")
            player.get_expertise().add_xp_to_class(xp, xp_class)
        xp_display = '\n'.join(xp_strs)
        if len(xp_strs) > 0:
            xp_display += "\n\n"

        output_strs = []
        for output_key, quantity in found_recipe.outputs.items():
            new_item = LOADED_ITEMS.get_new_item(output_key)
            # There's one by default, so add any extra as needed
            new_item.add_amount(quantity - 1)
            inventory.add_item(new_item)
            output_strs.append(f"{new_item.get_full_name()} (x{quantity})\n")
        output_display = '\n'.join(output_strs)

        return Embed(title="Cook", description=f"Cooking successful! You received:\n\n{output_display}\n\n{xp_display}{new_recipe_str}Choose a recipe you've acquired or discovered to make.\n\nNavigate through your recipes using the Prev and Next buttons.")

    def exit_with_intent(self):
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None
        self._page = 0
        self._current_cooking = {}

        if self._intent == Intent.CookOptions or self._intent == Intent.Cupboard:
            self._intent = None
            self._display_initial_buttons()
            return self.get_embed_for_intent()
        if self._intent == Intent.Cook or self._intent == Intent.Recipes:
            return self.enter_cook_options()
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