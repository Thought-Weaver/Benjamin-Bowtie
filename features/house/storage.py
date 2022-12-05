from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands
from strenum import StrEnum
from features.inventory import Inventory
from features.shared.enums import ClassTag, HouseRoom
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House, HouseView
    from features.shared.item import Item
    from features.player import Player

# -----------------------------------------------------------------------------
# MODAL
# -----------------------------------------------------------------------------

class RenameModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, storage_bin_key: str, view: StorageView, message_id: int):
        super().__init__(title=f"Rename {storage_bin_key}")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._storage_bin_key = storage_bin_key
        self._view = view
        self._message_id = message_id

        self._name_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Name",
            required=True,
            max_length=25,
            min_length=1
        )
        self.add_item(self._name_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        player: Player = self._get_player(self._user.id)
        house: House = player.get_house()

        if self._name_input.value == "":
            await interaction.response.send_message(f"Error: The name can't be empty.")
            return

        if self._name_input.value in house.storage_bins.keys():
            await interaction.response.send_message(f"Error: That name is already taken.")
            return

        house.storage_bins[self._name_input.value] = house.storage_bins.pop(self._storage_bin_key)

        embed = Embed(
            title="Basement Storage",
            description="Navigate through the items using the Prev and Next buttons."
        )

        await self._view.refresh(self._message_id, embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")

# -----------------------------------------------------------------------------
# KITCHEN VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Store = "Store"
    Retrieve = "Retrieve"


class SelectStorageBinButton(discord.ui.Button):
    def __init__(self, bin_key: str, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{bin_key}", row=row)
        
        self._bin_key = bin_key

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.select_storage_bin(self._bin_key)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_storage_bin_store()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RetrieveButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_storage_bin_retrieve()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class BuyNewButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Buy New ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            embed = view.buy_new_storage_bin()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RenameButton(discord.ui.Button):
    def __init__(self, selected_bin_key: str, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Rename", row=row)

        self._selected_bin_key = selected_bin_key

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if view.get_user() == interaction.user:
            await interaction.response.send_modal(RenameModal(
                view.get_database(),
                view.get_guild_id(),
                view.get_user(),
                self._selected_bin_key,
                view,
                interaction.message.id)
            )


class SelectInventoryItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.select_inventory_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectStorageBinItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.select_storage_bin_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.store()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.store_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            house_view: HouseView | None = view.get_house_view()
            if house_view is not None:
                embed = house_view.get_initial_embed()
                await interaction.response.edit_message(content=None, embed=embed, view=house_view)


class ExitToBasementButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.return_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseStorageButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StorageView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_storage_room()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StorageView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, house_view: HouseView | None, context: commands.Context):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._house_view = house_view
        self._context = context

        self._intent: Intent | None = None
        self._selected_item: Item | None = None
        self._selected_item_index: int = -1
        self._selected_bin_key: str = ""

        self._page = 0
        self._NUM_PER_PAGE = 3

        self._PURCHASE_COST = 1000
        self._NEW_BIN_COST = 500
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, additional: str=""):
        if self._intent == Intent.Store:
            return Embed(title=f"{self._selected_bin_key} (Storing)", description="Choose an item to store.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        if self._intent == Intent.Retrieve:
            return Embed(title=f"{self._selected_bin_key} (Retrieving)", description="Choose an item to retrieve.\n\nNavigate through the items using the Prev and Next buttons." + additional)
        
        selected_bin_str = f"You've currently selected the following bin: {self._selected_bin_key}\n\n" if self._selected_bin_key != "" else ""
        return Embed(title="Basement Storage", description=f"{selected_bin_str}Navigate through the items using the Prev and Next buttons." + additional)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Storage in self._get_player().get_house().house_rooms:
            self._get_storage_buttons()
        else:
            self.add_item(PurchaseStorageButton(self._PURCHASE_COST, 0))
            if self._house_view is not None:
                self.add_item(ExitToHouseButton(0))

        self._intent = None

    def purchase_storage_room(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(additional="\n\n*Error: You don't have enough coins to purchase the basement storage.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Storage)
        # You get one for free!
        house.storage_bins["Storage Bin"] = Inventory()
        self._display_initial_buttons()

        return self.get_embed_for_intent(additional="\n\n*Basement storage purchased! You can now store items with named storage chests.*")
    
    def return_to_main_menu(self):
        self._intent = None
        self._page = 0
        self._selected_item = None
        self._selected_item_index = -1
        self._selected_bin_key = ""

        self._display_initial_buttons()
        
        return self.get_embed_for_intent()

    def _get_storage_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        house: House = player.get_house()
        sorted_bin_keys: List[str] = sorted(house.storage_bins.keys())

        page_slots = sorted_bin_keys[self._page * self._NUM_PER_PAGE:min(len(sorted_bin_keys), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, bin_key in enumerate(page_slots):
            self.add_item(SelectStorageBinButton(bin_key, i))
        if self._page != 0:
            self.add_item(PrevButton(min(3, len(page_slots))))
        if len(sorted_bin_keys) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(3, len(page_slots))))
        if self._selected_bin_key != "":
            self.add_item(StoreButton(min(4, len(page_slots))))
            self.add_item(RetrieveButton(min(4, len(page_slots))))
            self.add_item(RenameButton(self._selected_bin_key, min(4, len(page_slots))))
        self.add_item(BuyNewButton(self._NEW_BIN_COST, min(4, len(page_slots))))
        if self._house_view is not None:
            self.add_item(ExitToHouseButton(min(4, len(page_slots))))

    def select_storage_bin(self, bin_key: str):
        self._selected_bin_key = bin_key

        self._get_storage_buttons()

        player: Player = self._get_player()
        house: House = player.get_house()
        if self._selected_bin_key == "" or house.storage_bins.get(self._selected_bin_key) is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that storage bin changed or it's no longer available.*")

        return self.get_embed_for_intent()

    def enter_storage_bin_store(self):
        self.clear_items()
        self._get_store_storage_bin_buttons()

        self._intent = Intent.Store

        return self.get_embed_for_intent()

    def _get_store_storage_bin_buttons(self):
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
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(StoreItemButton(min(4, len(page_slots))))
            self.add_item(StoreAllItemButton(min(4, len(page_slots))))
        self.add_item(ExitToBasementButton(min(4, len(page_slots))))

    def enter_storage_bin_retrieve(self):
        self.clear_items()
        self._get_retrieve_storage_bin_buttons()

        self._intent = Intent.Retrieve

        return self.get_embed_for_intent()

    def _get_retrieve_storage_bin_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_house().storage_bins.get(self._selected_bin_key, Inventory())
        inventory_slots = inventory.get_inventory_slots()

        page_slots = inventory_slots[self._page * self._NUM_PER_PAGE:min(len(inventory_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(SelectStorageBinItemButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(inventory_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        if self._selected_item_index != -1 and self._selected_item is not None:
            self.add_item(RetrieveItemButton(min(4, len(page_slots))))
            self.add_item(RetrieveAllItemButton(min(4, len(page_slots))))
        self.add_item(ExitToBasementButton(min(4, len(page_slots))))

    def select_inventory_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_store_storage_bin_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title=f"{self._selected_bin_key} (Storing)", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def select_storage_bin_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_retrieve_storage_bin_buttons()

        player: Player = self._get_player()
        storage_bin_slots: List[Item] = player.get_house().storage_bins.get(self._selected_bin_key, Inventory()).get_inventory_slots()
        if self._selected_item is None or storage_bin_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title=f"{self._selected_bin_key} (Retrieving)", description=f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\nNavigate through the items using the Prev and Next buttons.")

    def retrieve(self):
        player: Player = self._get_player()
        house: House = player.get_house()

        if self._selected_bin_key == "" or house.storage_bins.get(self._selected_bin_key) is None:
            self.return_to_main_menu()
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that storage bin changed or it's no longer available.*")
        
        storage_bin: Inventory = player.get_house().storage_bins.get(self._selected_bin_key, Inventory())
        storage_bin_slots = storage_bin.get_inventory_slots()
        if self._selected_item is None or storage_bin_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = storage_bin.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_storage_bin_buttons()

        return Embed(title=f"{self._selected_bin_key} (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved 1 {removed_item.get_full_name()} and added it to your inventory.*")

    def retrieve_all(self):
        player: Player = self._get_player()
        house: House = player.get_house()

        if self._selected_bin_key == "" or house.storage_bins.get(self._selected_bin_key) is None:
            self.return_to_main_menu()
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that storage bin changed or it's no longer available.*")
        
        storage_bin: Inventory = player.get_house().storage_bins.get(self._selected_bin_key, Inventory())
        storage_bin_slots = storage_bin.get_inventory_slots()
        if self._selected_item is None or storage_bin_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = storage_bin.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        player.get_inventory().add_item(removed_item)
        self._get_retrieve_storage_bin_buttons()

        return Embed(title=f"{self._selected_bin_key} (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved {removed_item.get_count()} {removed_item.get_full_name()} and added to your inventory.*")

    def store(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()

        if self._selected_bin_key == "" or house.storage_bins.get(self._selected_bin_key) is None:
            self.return_to_main_menu()
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that storage bin changed or it's no longer available.*")

        storage_bin: Inventory = player.get_house().storage_bins.get(self._selected_bin_key, Inventory())
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, 1)
        if removed_item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        storage_bin.add_item(removed_item)
        self._get_store_storage_bin_buttons()

        return Embed(title=f"{self._selected_bin_key} (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored 1 {removed_item.get_full_name()} and added it to the cupboard.*")

    def store_all(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()

        if self._selected_bin_key == "" or house.storage_bins.get(self._selected_bin_key) is None:
            self.return_to_main_menu()
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that storage bin changed or it's no longer available.*")

        storage_bin: Inventory = player.get_house().storage_bins.get(self._selected_bin_key, Inventory())
        if self._selected_item is None or inventory.get_inventory_slots()[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        removed_item = inventory.remove_item(self._selected_item_index, self._selected_item.get_count())
        if removed_item is None:
            return self.get_embed_for_intent(additional="\n\n*Error: Something about that item changed or it's no longer available.*")

        storage_bin.add_item(removed_item)
        self._get_store_storage_bin_buttons()

        return Embed(title=f"{self._selected_bin_key} (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored {removed_item.get_count()} {removed_item.get_full_name()} and added to the cupboard.*")

    def buy_new_storage_bin(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()

        if inventory.get_coins() < self._NEW_BIN_COST:
            return self.get_embed_for_intent(additional="\n\n*Error: You don't have enough coins to purchase a new storage bin.*")

        inventory.remove_coins(self._NEW_BIN_COST)

        cur_num = 1
        storage_bin_name = "New Chest 1"
        while storage_bin_name in house.storage_bins.keys():
            cur_num += 1
            storage_bin_name = f"New Chest {cur_num}"
        house.storage_bins[storage_bin_name] = Inventory()

        self._get_storage_buttons()

        return self.get_embed_for_intent(additional="\n\n*You have purchased a new storage chest!*")

    async def refresh(self, message_id: int, embed: Embed):
        self._selected_bin_key = ""
        self._get_storage_buttons()
        message: discord.Message = await self._context.fetch_message(message_id)
        await message.edit(view=self, embed=embed)

    def next_page(self):
        self._page += 1
        self._selected_item = None
        self._selected_item_index = -1

        if self._intent is None:
            self._selected_bin_key = ""
        if self._intent == Intent.Store:
            self._get_store_storage_bin_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_storage_bin_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._selected_item = None
        self._selected_item_index = -1

        if self._intent is None:
            self._selected_bin_key = ""
        if self._intent == Intent.Store:
            self._get_store_storage_bin_buttons()
        if self._intent == Intent.Retrieve:
            self._get_retrieve_storage_bin_buttons()

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
