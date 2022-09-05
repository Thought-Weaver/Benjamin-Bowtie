from __future__ import annotations

import discord

from discord.embeds import Embed
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player


class Item():
    def __init__(self, icon: str, name: str, value: int, count=1, is_unique=False):
        self._icon = icon
        self._name = name
        self._value = value
        self._count = count
        self._is_unique = is_unique

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(self._icon, self._name, self._value, amount, self._is_unique)
            self._count -= amount
            return result
        return None

    def add_amount(self, amount: int):
        self._count += amount

    def get_name(self):
        return self._name

    def get_full_name(self):
        return f"{self._icon} {self._name}"

    def get_full_name_and_count(self):
        return f"{self._icon} {self._name} ({self._count})"

    def get_value(self):
        return self._value

    def get_value_str(self):
        if self._value == 1:
            return "1 coin"
        return f"{self._value} coins"

    def get_count(self):
        return self._count

    def get_is_unique(self):
        return self._is_unique

    def get_icon(self):
        return self._icon

    def __eq__(self, obj):
        if not isinstance(obj, Item):
            return False
        
        if self._is_unique or obj.get_is_unique():
            return False
        
        if self._icon == obj.get_icon() and self._name == obj.get_name() and self._value == obj.get_value():
            return True

        return False

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._icon = state.get("_icon", "")
        self._name = state.get("_name", "")
        self._value = state.get("_value", 0)
        self._count = state.get("_count", 0)
        self._is_unique = state.get("_is_unique", False)


class Inventory():
    def __init__(self):
        self._inventory_slots: List[Item] = []
        self._coins: int = 0

    def _organize_inventory_slots(self):
        if len(self._inventory_slots) == 0:
            return
        
        item_set: List[Item] = []
        if len(self._inventory_slots) == 1:
            item = self._inventory_slots[0]
            item_set.append(Item(item.get_icon(), item.get_name(), item.get_value(), 0, item.get_is_unique()))
        if len(self._inventory_slots) >= 2:
            for item in self._inventory_slots:
                exists = False
                for item_in_set in item_set:
                    if item_in_set == item:
                        exists = True
                        break
                if not exists:
                    item_set.append(Item(item.get_icon(), item.get_name(), item.get_value(), 0, item.get_is_unique()))

        new_slots: List[Item] = []
        for item in item_set:
            for other_item in self._inventory_slots:
                if item == other_item:
                    item.add_amount(other_item.get_count())
            if item.get_count() != 0:
                new_slots.append(item)

        self._inventory_slots = sorted(new_slots, key=lambda item: item.get_name())

    def item_exists(self, item: Item):
        for i, inv_item in enumerate(self._inventory_slots):
            if inv_item == item:
                return i
        return -1

    def search_by_name(self, name: str):
        for i, item in enumerate(self._inventory_slots):
            if item.get_name() == name:
                return i
        return -1

    def add_item(self, item: Item):
        if item is None:
            self._organize_inventory_slots()
            return
        self._inventory_slots.append(item)
        self._organize_inventory_slots()

    def remove_item(self, slot_index: int, count=1):
        if count <= 0:
            return None
        if slot_index < len(self._inventory_slots):
            result = self._inventory_slots[slot_index].remove_amount(count)
            if result is not None:
                self._organize_inventory_slots()
                return result
        return None

    def add_coins(self, amount: int):
        self._coins += amount
    
    def remove_coins(self, amount: int):
        if amount > self._coins:
            return None
        self._coins -= amount
        return self._coins

    def get_inventory_slots(self):
        return self._inventory_slots

    def get_coins(self):
        return self._coins

    def get_coins_str(self):
        if self._coins == 1:
            return "1 coin"
        return f"{self._coins} coins"


class InventoryButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=item_index)
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()


class InventoryView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 4

        self._get_current_page_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
    def _get_current_page_info(self):
        player: Player = self._get_player()
        coins_str = player.get_inventory().get_coins_str()
        return Embed(
            title=f"{self._user.display_name}'s Inventory",
            description=f"You have {coins_str}.\n\nNavigate through your items using the Prev and Next buttons."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_current_page_info()

    def get_user(self):
        return self._user
