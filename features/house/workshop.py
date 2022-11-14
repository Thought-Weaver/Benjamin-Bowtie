from __future__ import annotations

import discord

from discord.embeds import Embed
from features.house.house import HouseRoom
from features.house.recipe import LOADED_RECIPES, Recipe
from features.shared.item import LOADED_ITEMS, ClassTag, ItemKey, Rarity
from enum import StrEnum

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
# WORKSHOP VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Craft = "Craft"
    Patterns = "Patterns"
    Deconstruct = "Deconstruct"
    Storage = "Storage"
    Store = "Store"
    Retrieve = "Retrieve"


class EnterCraftButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Craft", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.enter_craft()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterPatternsButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Patterns", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.enter_patterns()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterStorageButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Storage", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.enter_storage()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DeconstructButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Deconstruct", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.enter_deconstruct()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
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
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            embed = view.exit_with_intent()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class StoreButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_storage_store()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RetrieveButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_storage_retrieve()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class SelectInventoryItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.select_inventory_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectPatternButton(discord.ui.Button):
    def __init__(self, recipe: Recipe, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{recipe.name}", row=row, emoji=recipe.icon)
        
        self._recipe = recipe

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.select_recipe(self._recipe)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectStorageItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.select_storage_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.store()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.store_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class AddItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Add", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.add_crafting_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RemoveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Remove", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.remove_crafting_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectMaterialButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.select_material(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmPatternButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.use_pattern()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmCraftingButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Craft", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.try_crafting()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseWorkshopButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_workshop()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectDeconstructItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.select_deconstruct_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmDeconstructButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: WorkshopView = self.view
        if interaction.user == view.get_user():
            response = view.deconstruct()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WorkshopView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView):
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

        self._current_crafting: Dict[ItemKey, int] = {}

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._PURCHASE_COST = 2500
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Storage:
            return Embed(title="Storage", description="Store materials or retrieve them from your workshop storage." + error)
        if self._intent == Intent.Store:
            return Embed(title="Storage (Storing)", description="Choose an item to store in the workshop storage.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Retrieve:
            return Embed(title="Storage (Retrieving)", description="Choose an item to retrieve from storage.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Craft:
            current_crafting_str = self.get_current_crafting_str()
            current_crafting_display = f"──────────\n{current_crafting_str}──────────\n\n" if current_crafting_str != "" else ""
            return Embed(title="Craft", description=f"{current_crafting_display}Use materials from your inventory and attempt to craft something.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Patterns:
            return Embed(title="Patterns", description="Choose a pattern you've acquired or discovered to craft.\n\nNavigate through your patterns using the Prev and Next buttons." + error)
        if self._intent == Intent.Deconstruct:
            return Embed(title="Deconstruct", description="Choose an item to deconstruct into some materials.\n\nNavigate through the items using the Prev and Next buttons." + error)
        return Embed(title="Workshop", description="You enter the workshop, where you can use an existing pattern to craft weapons and armor, try making something from any materials you have in your inventory, or store materials for later use." + error)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Workshop in self._get_player().get_house().house_rooms:
            self.add_item(EnterPatternsButton(0))
            self.add_item(EnterCraftButton(1))
            self.add_item(DeconstructButton(2))
            self.add_item(EnterStorageButton(3))
            self.add_item(ExitToHouseButton(4))
        else:
            self.add_item(PurchaseWorkshopButton(self._PURCHASE_COST, 0))
            self.add_item(ExitToHouseButton(0))

        self._intent = None

    def purchase_workshop(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(error="\n\n*Error: You don't have enough coins to purchase the workshop.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Workshop)
        self._display_initial_buttons()

        return self.get_embed_for_intent(error="\n\nWorkshop purchased! You can now craft, deconstruct items, and store materials.")

    def enter_storage(self):
        self.clear_items()
        self.add_item(StoreButton(0))
        self.add_item(RetrieveButton(1))
        self.add_item(ExitWithIntentButton(2))

        self._intent = Intent.Storage

        return self.get_embed_for_intent()

    def enter_storage_store(self):
        self.clear_items()
        self._get_store_storage_buttons()

        self._intent = Intent.Store

        return self.get_embed_for_intent()

    def _get_store_storage_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.CraftingMaterial])
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

    def enter_storage_retrieve(self):
        self.clear_items()
        self._get_retrieve_storage_buttons()

        self._intent = Intent.Retrieve

        return self.get_embed_for_intent()

    def _get_retrieve_storage_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_house().workshop_storage
        inventory_slots = inventory.get_inventory_slots()

        page_slots = inventory_slots[self._page * self._NUM_PER_PAGE:min(len(inventory_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(SelectStorageItemButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(RetrieveItemButton(min(4, len(page_slots))))
            self.add_item(RetrieveAllItemButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def _get_craft_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Ingredient.CraftingMaterial])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectMaterialButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            if self._current_crafting.get(self._selected_item.get_key(), 0) < inventory_slots[self._selected_item_index].get_count():
                self.add_item(AddItemButton(min(4, len(page_slots))))
            if self._current_crafting.get(self._selected_item.get_key(), 0) > 0:
                self.add_item(RemoveItemButton(min(4, len(page_slots))))
        self.add_item(ConfirmCraftingButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_craft(self):
        self.clear_items()
        self._get_craft_buttons()

        self._intent = Intent.Craft

        return self.get_embed_for_intent()

    def _get_pattern_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        recipes: List[Recipe] = player.get_house().crafting_recipes
        filtered_recipes: List[Recipe] = list(filter(lambda r: r.any_output_has_any_class_tag([ClassTag.Equipment.Equipment]), recipes))

        page_slots = filtered_recipes[self._page * self._NUM_PER_PAGE:min(len(filtered_recipes), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, recipe in enumerate(page_slots):
            self.add_item(SelectPatternButton(recipe, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_recipes) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_recipe is not None:
            self.add_item(ConfirmPatternButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_patterns(self):
        self.clear_items()
        self._get_pattern_buttons()

        self._intent = Intent.Patterns

        return self.get_embed_for_intent()

    def _get_deconstruct_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Equipment.Equipment])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectDeconstructItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(ConfirmDeconstructButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_deconstruct(self):
        self.clear_items()
        self._get_deconstruct_buttons()

        self._intent = Intent.Deconstruct

        return self.get_embed_for_intent()

    def next_page(self):
        self._page += 1
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Store:
            self._get_store_storage_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_storage_buttons()
        if self._intent == Intent.Craft:
            self._get_craft_buttons()
        if self._intent == Intent.Patterns:
            self._get_pattern_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None

        if self._intent == Intent.Store:
            self._get_store_storage_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_storage_buttons()
        if self._intent == Intent.Craft:
            self._get_craft_buttons()
        if self._intent == Intent.Patterns:
            self._get_pattern_buttons()

        return self.get_embed_for_intent()

    def select_inventory_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_store_storage_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Storage (Storing)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def select_recipe(self, recipe: Recipe):
        self._selected_recipe = recipe

        self._get_pattern_buttons()
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that pattern changed or it's no longer available.*")

        num_can_be_created = self._selected_recipe.num_can_be_made(self._get_player().get_inventory())

        return Embed(title="Patterns", description=f"──────────\n{self._selected_recipe}\nYou have enough materials to make {num_can_be_created}.\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def select_storage_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_retrieve_storage_buttons()

        player: Player = self._get_player()
        storage_slots: List[Item] = player.get_house().workshop_storage.get_inventory_slots()
        if self._selected_item is None or storage_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Storage (Retrieving)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def retrieve(self):
        player: Player = self._get_player()
        storage: Inventory = player.get_house().workshop_storage
        storage_slots: List[Item] = storage.get_inventory_slots()
        if self._selected_item is None or storage_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = storage.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_storage_buttons()

        return Embed(title="Storage (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved 1 {removed_item.get_full_name()} and added it to your inventory.*")

    def retrieve_all(self):
        player: Player = self._get_player()
        storage: Inventory = player.get_house().workshop_storage
        storage_slots: List[Item] = storage.get_inventory_slots()
        if self._selected_item is None or storage_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = storage.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_storage_buttons()

        return Embed(title="Storage (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved {removed_item.get_count()} {removed_item.get_full_name()} and added to your inventory.*")

    def store(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        storage: Inventory = player.get_house().workshop_storage
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        storage.add_item(removed_item)
        self._get_store_storage_buttons()

        return Embed(title="Storage (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored 1 {removed_item.get_full_name()} and added it to storage.*")

    def store_all(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        storage: Inventory = player.get_house().workshop_storage
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        storage.add_item(removed_item)
        self._get_store_storage_buttons()

        return Embed(title="Storage (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored {removed_item.get_count()} {removed_item.get_full_name()} and added to storage.*")

    def get_current_crafting_str(self):
        input_strs = []
        for item_key, quantity in self._current_crafting.items():
            if quantity > 0:
                item_data = LOADED_ITEMS.get_item_state(item_key)
                input_strs.append(f"{item_data['icon']} {item_data['name']} (x{quantity})\n")
        return '\n'.join(input_strs)

    def add_crafting_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_crafting[item_key] = self._current_crafting.get(item_key, 0) + 1

        current_crafting_str = self.get_current_crafting_str()
        current_crafting_display = f"──────────\n{current_crafting_str}──────────\n\n" if current_crafting_str != "" else ""
        return Embed(title="Craft", description=f"{current_crafting_display}Use materials from your inventory and attempt to craft something.\n\nNavigate through the items using the Prev and Next buttons.")

    def remove_crafting_item(self):
        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        
        item_key = self._selected_item.get_key()
        self._current_crafting[item_key] = max(self._current_crafting.get(item_key, 0) - 1, 0)

        current_crafting_str = self.get_current_crafting_str()
        current_crafting_display = f"──────────\n{current_crafting_str}──────────\n\n" if current_crafting_str != "" else ""
        return Embed(title="Craft", description=f"{current_crafting_display}Use materials from your inventory and attempt to craft something.\n\nNavigate through the items using the Prev and Next buttons.")

    def select_material(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_craft_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        current_crafting_str = self.get_current_crafting_str()
        current_crafting_display = f"──────────\n{current_crafting_str}──────────\n\n" if current_crafting_str != "" else ""
        return Embed(title="Craft", description=f"{current_crafting_display}Use materials from your inventory and attempt to craft something.\n\nNavigate through the items using the Prev and Next buttons.")

    def use_pattern(self):
        if self._selected_recipe is None:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that pattern changed or it's no longer available.*")

        # TODO: This raises an interesting question: Should I search the inventory for anything matching the keys? The problem is what if some item has a
        # different set of state tags? Shouldn't I use whatever the player pressed from their inventory? But then again, the player can't discern which
        # items have state tags from the buttons, so perhaps this is a later problem.

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have one of the items for that pattern.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items.*")

        for input_key, quantity in self._selected_recipe.inputs.items():
            index = inventory.search_by_key(input_key)
            inventory.remove_item(index, quantity)

        xp_strs = []
        for xp_class, xp in self._selected_recipe.xp_reward_for_use.items():
            final_xp = player.get_expertise().add_xp_to_class(xp, xp_class, player.get_equipment())
            xp_strs.append(f"*(+{final_xp} {xp_class} xp)*")
        xp_display = '\n'.join(xp_strs)

        stats: Stats = player.get_stats()

        output_strs = []
        for output_key, quantity in self._selected_recipe.outputs.items():
            new_item = LOADED_ITEMS.get_new_item(output_key)
            # There's one by default, so add any extra as needed
            new_item.add_amount(quantity - 1)
            inventory.add_item(new_item)
            output_strs.append(f"{new_item.get_full_name()} (x{quantity})\n")

            if new_item.get_rarity() == Rarity.Common:
                stats.crafting.common_items_crafted += 1
            if new_item.get_rarity() == Rarity.Uncommon:
                stats.crafting.uncommon_items_crafted += 1
            if new_item.get_rarity() == Rarity.Rare:
                stats.crafting.rare_items_crafted += 1
            if new_item.get_rarity() == Rarity.Epic:
                stats.crafting.epic_items_crafted += 1
            if new_item.get_rarity() == Rarity.Legendary:
                stats.crafting.legendary_items_crafted += 1
            if new_item.get_rarity() == Rarity.Artifact:
                stats.crafting.artifact_items_crafted += 1
        output_display = '\n'.join(output_strs)
        
        return Embed(title="Patterns", description=f"Crafting successful! You received:\n\n{output_display}\n{xp_display}\n\nChoose a pattern you've acquired or discovered to craft.\n\nNavigate through your patterns using the Prev and Next buttons.")

    def try_crafting(self):
        if len(self._current_crafting.items()) == 0:
            return self.get_embed_for_intent(error="\n\n*Error: You need to add at least one item.*")

        # TODO: See above also here.

        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()

        # Validation before continuing, slightly slower but avoids having to remove and then return items when something goes wrong
        for input_key, quantity in self._current_crafting.items():
            index = inventory.search_by_key(input_key)
            if index == -1:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have at least one of the items needed to craft that.*")
        
            item = inventory.get_inventory_slots()[index]
            if item.get_count() < quantity:
                return self.get_embed_for_intent(error="\n\n*Error: You don't have enough of one of those items to craft that.*")

        for input_key, quantity in self._current_crafting.items():
            index = inventory.search_by_key(input_key)
            inventory.remove_item(index, quantity)

        found_recipe = None
        new_recipe = False
        for recipe_key in LOADED_RECIPES.get_all_keys():
            recipe = LOADED_RECIPES.get_new_recipe(recipe_key)
            if recipe.inputs == self._current_crafting:
                # Assume uniqueness and that the first valid matching is the result
                if recipe not in player.get_house().crafting_recipes:
                    new_recipe = True
                    player.get_house().crafting_recipes.append(recipe)
                found_recipe = recipe
                break

        if found_recipe is None:
            return Embed(title="Craft", description=f"You attempt to combine these materials together, but nothing happens.\n──────────\n\nUse materials from your inventory and attempt to craft something.\n\nNavigate through your patterns using the Prev and Next buttons.")
            
        new_recipe_str = f"\n*You acquired the {found_recipe.get_name_and_icon()} pattern!*\n" if new_recipe else ""

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
                stats.crafting.common_items_crafted += 1
            if new_item.get_rarity() == Rarity.Uncommon:
                stats.crafting.uncommon_items_crafted += 1
            if new_item.get_rarity() == Rarity.Rare:
                stats.crafting.rare_items_crafted += 1
            if new_item.get_rarity() == Rarity.Epic:
                stats.crafting.epic_items_crafted += 1
            if new_item.get_rarity() == Rarity.Legendary:
                stats.crafting.legendary_items_crafted += 1
            if new_item.get_rarity() == Rarity.Artifact:
                stats.crafting.artifact_items_crafted += 1
        output_display = '\n'.join(output_strs)

        stats.crafting.patterns_discovered += 1

        return Embed(title="Craft", description=f"Crafting successful! You received:\n\n{output_display}\n{xp_display}{new_recipe_str}\n──────────\n\nChoose a pattern you've acquired or discovered to craft.\n\nNavigate through your patterns using the Prev and Next buttons.")

    def select_deconstruct_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_deconstruct_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Deconstruct", description=f"──────────\n{self._selected_item}\n──────────\n\nChoose an item to deconstruct into some materials.\n\nNavigate through the items using the Prev and Next buttons.")

    def deconstruct(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        # TODO: By doing this reverse lookup, I've defined crafting/deconstructing as a reversible process. Namely, there must exist a recipe
        # to deconstruct something, therefore anything that is deconstructible must also be craftable. It's not necessarily ideal -- at least
        # I suspect there are things I'd want not to be crafted that I would be fine with being deconstructed at some point. I'll figure out
        # some way to address that in the future.

        found = False
        result_strs = []
        for recipe_key in LOADED_RECIPES.get_all_keys():
            recipe = LOADED_RECIPES.get_new_recipe(recipe_key)
            if len(recipe.outputs.items()) == 1 and list(recipe.outputs.values())[0] == 1:
                if list(recipe.outputs.keys())[0] == self._selected_item.get_key():
                    inventory.remove_item(self._selected_item_index, 1)
                    for input_key, quantity in recipe.inputs.items():
                        item = LOADED_ITEMS.get_new_item(input_key)
                        # Get rid of the base amount and replace it with half the amount it takes to craft.
                        item.remove_amount(1)
                        item.add_amount(int(quantity / 2))
                        inventory.add_item(item)

                        result_strs.append(f"{item.get_full_name()} (x{int(quantity / 2)})")
                        found = True
        result_str = "\n".join(result_strs)

        if not found:
            return self.get_embed_for_intent(error="\n\n*You cannot deconstruct that item.*")

        return Embed(title="Deconstruct", description=f"You successfully deconstructed {self._selected_item.get_full_name()} into:\n\n──────────\n{result_str}\n──────────\n\nChoose an item to deconstruct into some materials.\n\nChoose an item to deconstruct into some materials.\n\nNavigate through the items using the Prev and Next buttons.")

    def exit_with_intent(self):
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_recipe = None
        self._page = 0
        self._current_crafting = {}

        if self._intent == Intent.Craft or self._intent == Intent.Patterns or self._intent == Intent.Storage or self._intent == Intent.Deconstruct:
            self._intent = None
            self._display_initial_buttons()
            return self.get_embed_for_intent()
        if self._intent == Intent.Store or self._intent == Intent.Retrieve:
            return self.enter_storage()

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
