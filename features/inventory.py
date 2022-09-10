from __future__ import annotations

import discord

from discord.embeds import Embed
from features.shared.item import Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player


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
            item_set.append(Item(
                item.get_key(),
                item.get_icon(),
                item.get_name(),
                item.get_value(),
                item.get_rarity(),
                item.get_class_tags(),
                item.get_state_tags(),
                0)
            )
        if len(self._inventory_slots) >= 2:
            for item in self._inventory_slots:
                exists = False
                for item_in_set in item_set:
                    if item_in_set == item:
                        exists = True
                        break
                if not exists:
                    item_set.append(Item(
                        item.get_key(),
                        item.get_icon(),
                        item.get_name(),
                        item.get_value(),
                        item.get_rarity(),
                        item.get_class_tags(),
                        item.get_state_tags(),
                        0)
                    )

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
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: InventoryView = self.view
        player: Player = view.get_player()
        coins_str = player.get_inventory().get_coins_str()

        await interaction.edit_original_response(embed=Embed(
            title=f"{view.get_user().display_name}'s Inventory",
            description=f"You have {coins_str}.\n\n" \
                        f"──────────\n{self._item}\n──────────\n\n" \
                        "Navigate through your items using the Prev and Next buttons."
        ))


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

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player()
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
    def _get_current_page_info(self):
        player: Player = self.get_player()
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
