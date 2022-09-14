from __future__ import annotations

import discord

from discord.embeds import Embed
from features.shared.item import ClassTag, Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
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
        self._main_hand: Item = None
        self._off_hand: Item = None

    def get_item_in_slot(self, slot: ClassTag.Equipment):
        if slot == ClassTag.Equipment.Helmet:
            return self._helmet
        if slot == ClassTag.Equipment.Amulet:
            return self._amulet
        if slot == ClassTag.Equipment.ChestArmor:
            return self._chest_armor
        if slot == ClassTag.Equipment.Gloves:
            return self._gloves
        if slot == ClassTag.Equipment.Ring:
            return self._ring
        if slot == ClassTag.Equipment.Leggings:
            return self._leggings
        if slot == ClassTag.Equipment.Boots:
            return self._boots
        if slot == ClassTag.Equipment.MainHand:
            return self._main_hand
        if slot == ClassTag.Equipment.OffHand:
            return self._off_hand
        return None

    def unequip_item_from_slot(self, slot: ClassTag.Equipment):
        if slot == ClassTag.Equipment.Helmet:
            item = self._helmet
            self._helmet = None
            return item
        if slot == ClassTag.Equipment.Amulet:
            item = self._amulet
            self._amulet = None
            return item
        if slot == ClassTag.Equipment.ChestArmor:
            item = self._chest_armor
            self._chest_armor = None
            return item
        if slot == ClassTag.Equipment.Gloves:
            item = self._gloves
            self._gloves = None
            return item
        if slot == ClassTag.Equipment.Ring:
            item = self._ring
            self._ring = None
            return item
        if slot == ClassTag.Equipment.Leggings:
            item = self._leggings
            self._leggings = None
            return item
        if slot == ClassTag.Equipment.Boots:
            item = self._boots
            self._boots = None
            return item
        if slot == ClassTag.Equipment.MainHand:
            item = self._main_hand
            self._main_hand = None
            return item
        if slot == ClassTag.Equipment.OffHand:
            item = self._off_hand
            self._off_hand = None
            return item
        return None

    def equip_item_to_slot(self, slot: ClassTag.Equipment, item: (Item | None)):
        if slot == ClassTag.Equipment.Helmet:
            self._helmet = item
        if slot == ClassTag.Equipment.Amulet:
            self._amulet = item
        if slot == ClassTag.Equipment.ChestArmor:
            self._chest_armor = item
        if slot == ClassTag.Equipment.Gloves:
            self._gloves = item
        if slot == ClassTag.Equipment.Ring:
            self._ring = item
        if slot == ClassTag.Equipment.Leggings:
            self._leggings = item
        if slot == ClassTag.Equipment.Boots:
            self._boots = item
        if slot == ClassTag.Equipment.MainHand:
            self._main_hand = item
        if slot == ClassTag.Equipment.OffHand:
            self._off_hand = item

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
        self._main_hand = state.get("_main_hand")
        self._off_hand = state.get("_off_hand")


class EquipSlotButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=row)
        
        self._exact_item_index = exact_item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.equip_item(self._exact_item_index)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSlotButton(discord.ui.Button):
    def __init__(self, label: str, slot: ClassTag.Equipment, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=label, row=row)
        
        self._slot = slot

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.display_item_in_slot(self._slot)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterEquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Equip", row=0)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.enter_equip_for_slot()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class UnequipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Unequip", row=0)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.unequip_item()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EquipSlotExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_slot_view()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class SelectSlotExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


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

        self._display_slot_select_buttons()

    def get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_str_for_slot(self, slot: ClassTag.Equipment):
        if slot == ClassTag.Equipment.ChestArmor:
            return "Chest Armor"
        if slot == ClassTag.Equipment.MainHand:
            return "Main Hand"
        if slot == ClassTag.Equipment.OffHand:
            return "Off Hand"
        return slot

    def enter_equip_for_slot(self):
        self._get_current_page_buttons()

        return Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description=f"Choose an item from your inventory to equip."
        )

    def equip_item(self, exact_item_index: int):
        player: Player = self.get_player()
        inventory = player.get_inventory()
        equipment = player.get_equipment()

        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        embed = Embed(
            title=f"{self.get_str_for_slot(self._cur_equip_slot)}",
            description = "None equipped. Use Equip below to select an item for this slot."
        )

        # The "exact_item_index" here is the index of the item with respect to the entire
        # inventory. This is used instead of an adjusted index here because the items are
        # filtered when displayed to the user, so adjusting based on page size wouldn't work.
        found_index = inventory.item_exists(exact_item_index)
        if found_index == exact_item_index:
            item = inventory.remove_item(exact_item_index, 1)
            equipment.equip_item_to_slot(self._cur_equip_slot, item)

            embed = Embed(
                title=f"{self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"──────────\n{item}\n──────────\n\n"
            )
        
        self._get_current_page_buttons()
        return embed

    def unequip_item(self):
        player: Player = self.get_player()
        equipment: Equipment = player.get_equipment()
        inventory: Inventory = player.get_inventory()

        equipped_item: (Item | None) = equipment.unequip_item_from_slot(self._cur_equip_slot)
        inventory.add_item(equipped_item)

        self.clear_items()
        self.add_item(EnterEquipButton())

        return Embed(
            title=f"{self.get_str_for_slot(self._cur_equip_slot)}",
            description = "None equipped. Use Equip below to select an item for this slot."
        )

    def display_item_in_slot(self, slot: ClassTag.Equipment):
        self.clear_items()
        self.add_item(EnterEquipButton())

        self._cur_equip_slot = slot
        player: Player = self.get_player()
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(slot)

        description = "None equipped. Use Equip below to select an item for this slot."
        if equipped_item is not None:
            description = f"──────────\n{equipped_item}\n──────────\n\n"
            self.add_item(UnequipButton())

        self.add_item(SelectSlotExitButton(0))

        return Embed(
            title=f"{self.get_str_for_slot(slot)}",
            description=description
        )

    def _display_slot_select_buttons(self):
        self.clear_items()
        self.add_item(SelectSlotButton("Helmet", ClassTag.Equipment.Helmet, 0))
        self.add_item(SelectSlotButton("Amulet", ClassTag.Equipment.Amulet, 0))
        self.add_item(SelectSlotButton("Gloves", ClassTag.Equipment.Gloves, 1))
        self.add_item(SelectSlotButton("Chest Armor", ClassTag.Equipment.ChestArmor, 1))
        self.add_item(SelectSlotButton("Ring", ClassTag.Equipment.Ring, 1))
        self.add_item(SelectSlotButton("Leggings", ClassTag.Equipment.Leggings, 2))
        self.add_item(SelectSlotButton("Boots", ClassTag.Equipment.Boots, 2))
        self.add_item(SelectSlotButton("Main Hand", ClassTag.Equipment.MainHand, 3))
        self.add_item(SelectSlotButton("Off Hand", ClassTag.Equipment.OffHand, 3))

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self.get_player()
        inventory = player.get_inventory()
        inventory_slots = inventory.get_inventory_slots()

        filtered_indices = inventory.filter_inventory_slots([self._cur_equip_slot])
        filtered_items = [inventory_slots[i] for i in filtered_indices]

        page_slots = filtered_items[self._page * self._NUM_PER_PAGE:min(len(filtered_items), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(EquipSlotButton(filtered_indices[i + (self._page * self._NUM_PER_PAGE)], item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(EquipSlotExitButton(min(4, len(page_slots))))

    def get_initial_info(self):
        return Embed(
            title=f"{self._user.display_name}'s Equipment",
            description="Choose a slot to see currently equipped item and equip another or unequip it."
        )

    def exit_to_slot_view(self):
        return self.display_item_in_slot(self._cur_equip_slot)

    def exit_to_main_menu(self):
        self._cur_equip_slot = None
        self._display_slot_select_buttons()
        return self.get_initial_info()

    def _get_current_equip_page_info(self):
        return Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description=f"Choose an item from your inventory to equip."
        )
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()
        return self._get_current_equip_page_info()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()
        return self._get_current_equip_page_info()

    def get_user(self):
        return self._user
