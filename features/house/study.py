from __future__ import annotations

import discord

from discord.embeds import Embed
from features.expertise import Expertise
from features.shared.enums import ClassTag, HouseRoom
from features.shared.item import LOADED_ITEMS
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from enum import StrEnum

from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.house.house import House, HouseView
    from features.inventory import Inventory
    from features.shared.item import Item
    from features.player import Player
    from features.stats import Stats


# -----------------------------------------------------------------------------
# STUDY VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Enchant = "Enchant"
    SelectSocket = "SelectSocket"
    SelectGem = "SelectGem"
    Chest = "Chest"
    Store = "Store"
    Retrieve = "Retrieve"


class EnterEnchantButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Enchant", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.enter_enchant()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterStorageButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Storage", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.enter_storage()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitToHouseButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
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
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            embed = view.exit_with_intent()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class StoreButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            embed = view.enter_storage_store()
            await interaction.response.edit_message(content=None, embed=embed, view=view)


class RetrieveButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
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
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.select_inventory_item_to_store(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectEnchantItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.select_enchant_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSocketButton(discord.ui.Button):
    def __init__(self, socket_index: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Socket {socket_index + 1}", row=socket_index)

        self._socket_index = socket_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.select_socket(self._socket_index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectGemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())

        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.select_gem(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectStorageItemButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.select_storage_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RetrieveAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Retrieve All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.retrieve_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.store()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StoreAllItemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Store All", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.store_all()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class RemoveGemButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"Remove Gem", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.remove_gem()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class PurchaseStudyButton(discord.ui.Button):
    def __init__(self, cost: int, row: int):
        super().__init__(style=discord.ButtonStyle.green, label=f"Buy ({cost})", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: StudyView = self.view
        if interaction.user == view.get_user():
            response = view.purchase_study()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class StudyView(discord.ui.View):
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
        self._selected_socket: int = -1

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._PURCHASE_COST = 2500
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_embed_for_intent(self, error: str=""):
        if self._intent == Intent.Chest:
            return Embed(title="Chest", description="Store gems, armor, and items or retrieve them from your cupboard." + error)
        if self._intent == Intent.Store:
            return Embed(title="Chest (Storing)", description="Choose an item to store in the chest.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Retrieve:
            return Embed(title="Chest (Retrieving)", description="Choose an item to retrieve from the chest.\n\nNavigate through the items using the Prev and Next buttons." + error)
        if self._intent == Intent.Enchant:
            return Embed(title="Enchant", description="Choose an item to enchant.\n\nNavigate through your patterns using the Prev and Next buttons." + error)
        if self._intent == Intent.SelectSocket:
            return Embed(title="Select Socket", description="Choose a socket to add or remove a gem." + error)
        if self._intent == Intent.SelectGem:
            return Embed(title="Select Gem", description="Choose a gem to place in this socket." + error)
        return Embed(title="Study", description="You enter the study, where you can enchant items using gemstones, as well as store enchanting materials and equippable items." + error)

    def _display_initial_buttons(self):
        self.clear_items()

        if HouseRoom.Study in self._get_player().get_house().house_rooms:
            self.add_item(EnterEnchantButton(0))
            self.add_item(EnterStorageButton(1))
            self.add_item(ExitToHouseButton(2))
        else:
            self.add_item(PurchaseStudyButton(self._PURCHASE_COST, 0))
            self.add_item(ExitToHouseButton(0))

        self._intent = None

    def purchase_study(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        house: House = player.get_house()
        
        if inventory.get_coins() < self._PURCHASE_COST:
            return self.get_embed_for_intent(error="\n\n*Error: You don't have enough coins to purchase the study.*")

        inventory.remove_coins(self._PURCHASE_COST)
        house.house_rooms.append(HouseRoom.Study)
        self._display_initial_buttons()

        return self.get_embed_for_intent(error="\n\n*Study purchased! You can now enchant items and store materials.*")

    def enter_storage(self):
        self.clear_items()
        self.add_item(StoreButton(0))
        self.add_item(RetrieveButton(1))
        self.add_item(ExitWithIntentButton(2))

        self._intent = Intent.Chest

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

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Valuable.Gemstone, ClassTag.Equipment.Equipment], require_enchantable_equipment=True)
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

    def _get_select_enchant_item_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        expertise: Expertise = player.get_expertise()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        # You can only socket gems into items that you have a high enough level to use properly, and (of course)
        # the item must be able to be enchanted
        filtered_indices = inventory.filter_inventory_slots([ClassTag.Equipment.Equipment], player_level=expertise.level, require_enchantable_equipment=True, require_player_level=True)
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectEnchantItemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def enter_enchant(self):
        self.clear_items()
        self._get_select_enchant_item_buttons()

        self._intent = Intent.Enchant

        return self.get_embed_for_intent()

    def select_inventory_item_to_store(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_store_storage_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Chest (Storing)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

    def select_storage_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_retrieve_storage_buttons()

        player: Player = self._get_player()
        storage_slots: List[Item] = player.get_house().workshop_storage.get_inventory_slots()
        if self._selected_item is None or storage_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")
        return Embed(title="Chest (Retrieving)", description=f"──────────\n{self._selected_item}\n──────────\n\nNavigate through the items using the Prev and Next buttons.")

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

        return Embed(title="Chest (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved 1 {removed_item.get_full_name()} and added it to your inventory.*")

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

        return Embed(title="Chest (Retrieving)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Retrieved {removed_item.get_count()} {removed_item.get_full_name()} and added to your inventory.*")

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

        return Embed(title="Chest (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored 1 {removed_item.get_full_name()} and added it to storage.*")

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

        return Embed(title="Chest (Storing)", description=f"Navigate through the items using the Prev and Next buttons.\n\n*Stored {removed_item.get_count()} {removed_item.get_full_name()} and added to storage.*")

    def _get_gem_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([ClassTag.Valuable.Gemstone])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(SelectGemButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(ExitWithIntentButton(min(4, len(page_slots))))

    def select_socket(self, socket_index: int):
        self._selected_socket = socket_index

        self._get_gem_buttons()

        return self.get_embed_for_intent()

    def _get_socket_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return

        num_sockets = len(self._selected_item.get_altering_item_keys())
        for i in range(num_sockets):
            self.add_item(SelectSocketButton(i))
        self.add_item(ExitWithIntentButton(num_sockets))

    def select_enchant_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_select_enchant_item_buttons()

        player: Player = self._get_player()
        inventory_slots: List[Item] = player.get_inventory().get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            return self.get_embed_for_intent(error="\n\n*Error: Something about that item changed or it's no longer available.*")

        self._intent = Intent.SelectSocket

        self._get_socket_buttons()
        return Embed(title="Select Socket", description=f"──────────\n{self._selected_item}\n──────────\n\nChoose a socket to add or remove a gem.")

    def select_gem(self, index: int, item: Item):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: Something about the item you want to enchant changed or it's no longer available.*")

        if item is None or inventory_slots[index] != item:
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: Something about the gem changed or it's no longer available.*")

        new_item = self._selected_item.remove_amount(1)
        if new_item is None:
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: Something about the item you want to enchant changed or it's no longer available.*")

        altering_item_keys = new_item.get_altering_item_keys()
        if not (0 <= self._selected_socket < len(altering_item_keys)):
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: That's not a valid socket.*")
        
        inventory.remove_item(index, 1)
        altering_item_keys[self._selected_socket] = item.get_key()
        inventory.add_item(new_item)

        return self.get_embed_for_intent(f"\n\n*{item.get_full_name()} has been socketed into socket {self._selected_socket}*")

    def remove_gem(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        inventory_slots: List[Item] = inventory.get_inventory_slots()
        if self._selected_item is None or inventory_slots[self._selected_item_index] != self._selected_item:
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: Something about the item you want to enchant changed or it's no longer available.*")

        altering_item_keys = self._selected_item.get_altering_item_keys()
        if not (0 <= self._selected_socket < len(altering_item_keys)):
            self.exit_with_intent()
            return self.get_embed_for_intent(error="\n\n*Error: That's not a valid socket.*")
        
        key = altering_item_keys[self._selected_socket]
        altering_item_keys[self._selected_socket] = ""
        item = LOADED_ITEMS.get_new_item(key)
        inventory.add_item(item)
        
        self._get_gem_buttons()

        return self.get_embed_for_intent(f"\n\n*{item.get_full_name()} has been unsocketed from socket {self._selected_socket}*")

    def exit_with_intent(self):
        self._page = 0

        if self._intent == Intent.Chest or self._intent == Intent.Enchant:
            self._intent = None
            self._selected_item = None
            self._selected_item_index = -1
            self._display_initial_buttons()
            return self.get_embed_for_intent()
        if self._intent == Intent.Store or self._intent == Intent.Retrieve:
            self._selected_item = None
            self._selected_item_index = -1
            return self.enter_storage()
        if self._intent == Intent.SelectSocket:
            self._selected_socket = -1
            return self.enter_enchant()
        if self._intent == Intent.SelectGem:
            self._intent = Intent.SelectSocket
            self._get_socket_buttons()
        
        return self.get_embed_for_intent()

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Store:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_store_storage_buttons()
        if self._intent == Intent.Retrieve:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_retrieve_storage_buttons()
        if self._intent == Intent.Enchant:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_select_enchant_item_buttons()
        if self._intent == Intent.SelectSocket:
            self._selected_socket = -1
            self._get_socket_buttons()
        if self._intent == Intent.SelectGem:
            self._get_gem_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Store:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_store_storage_buttons()
        if self._intent == Intent.Retrieve:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_retrieve_storage_buttons()
        if self._intent == Intent.Enchant:
            self._selected_item = None
            self._selected_item_index = -1
            self._get_select_enchant_item_buttons()
        if self._intent == Intent.SelectSocket:
            self._selected_socket = -1
            self._get_socket_buttons()
        if self._intent == Intent.SelectGem:
            self._get_gem_buttons()

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
