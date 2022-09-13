from __future__ import annotations

import discord

from discord.embeds import Embed
from features.shared.item import ClassTag, Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player


class Equipment():
    def __init__(self):
        self._helmet: Item = None
        self._amulet: Item = None
        self._chest_armor: Item = None
        self._gloves: Item = None
        self._ring: Item = None
        self._leggings: Item = None
        self._boots: Item = None

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self._helmet = state.get("_helmet")
        self._amulet = state.get("_amulet")
        self._chest_armor = state.get("_chest_armor")
        self._gloves = state.get("_gloves")
        self._ring = state.get("_ring")
        self._leggings = state.get("_leggings")
        self._boots = state.get("_boots")


class EquipSlotButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, slot: ClassTag.Equipment):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=item_index)
        
        self._item_index = item_index
        self._item = item
        self._slot = slot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        player: Player = view.get_player()
        
        await interaction.response.defer()


class SelectSlotButton(discord.ui.Button):
    def __init__(self, label: str, slot: ClassTag.Equipment, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        
        self._slot = slot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        player: Player = view.get_player()
        
        await interaction.response.defer()


class EquipmentView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0
        self._cur_equip_slot = None

        self._NUM_PER_PAGE = 4

        self._display_initial_buttons()

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_str_for_slot(self, slot: ClassTag.Equipment):
        if slot == ClassTag.Equipment.ChestArmor:
            return "Chest Armor"
        return slot

    def _display_initial_buttons(self):
        self.clear_items()

    def _display_slot_select_buttons(self):
        self.clear_items()
        self.add_item(SelectSlotButton("Helmet", ClassTag.Equipment.Helmet, 0))
        self.add_item(SelectSlotButton("Amulet", ClassTag.Equipment.Amulet, 0))
        self.add_item(SelectSlotButton("Gloves", ClassTag.Equipment.Gloves, 1))
        self.add_item(SelectSlotButton("Chest Armor", ClassTag.Equipment.ChestArmor, 1))
        self.add_item(SelectSlotButton("Ring", ClassTag.Equipment.Ring, 1))
        self.add_item(SelectSlotButton("Leggings", ClassTag.Equipment.Leggings, 2))
        self.add_item(SelectSlotButton("Boots", ClassTag.Equipment.Boots, 1))

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player()
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            # TODO: Need to do an absolute item index (index in all_slots) since I need to filter the list. Probably the
            # filtering should return a list of indices? I can't return a new list since lists are immutable, so it wouldn't
            # remove the item upon being pressed.
            self.add_item(EquipSlotButton(i, item, self._cur_equip_slot))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
    def get_current_page_info(self):
        return Embed(
            title=f"{self._user.display_name}'s Equipment",
            description=f"Choose an item to equip to your {self.get_str_for_slot(self._cur_equip_slot)} slot. Navigate through your items using the Prev and Next buttons."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self.get_current_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self.get_current_page_info()

    def get_user(self):
        return self._user
