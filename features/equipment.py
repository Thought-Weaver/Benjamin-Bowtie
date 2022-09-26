from __future__ import annotations

import discord

from discord.embeds import Embed
from features.expertise import Expertise
from features.shared.item import Buffs, ClassTag, Item
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player
    from features.shared.item import ArmorStats

# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

ARMOR_OVERLEVELED_DEBUFF = 0.15

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

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

    def get_all_equipped_items(self):
        equipment = [
            self._helmet,
            self._amulet,
            self._chest_armor,
            self._gloves,
            self._ring,
            self._leggings,
            self._boots,
            self._main_hand,
            self._off_hand
        ]
        return list(filter(lambda item: item is not None, equipment))

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
        prev_item = None
        if slot == ClassTag.Equipment.Helmet:
            prev_item = self._helmet
            self._helmet = item
        if slot == ClassTag.Equipment.Amulet:
            prev_item = self._amulet
            self._amulet = item
        if slot == ClassTag.Equipment.ChestArmor:
            prev_item = self._chest_armor
            self._chest_armor = item
        if slot == ClassTag.Equipment.Gloves:
            prev_item = self._gloves
            self._gloves = item
        if slot == ClassTag.Equipment.Ring:
            prev_item = self._ring
            self._ring = item
        if slot == ClassTag.Equipment.Leggings:
            prev_item = self._leggings
            self._leggings = item
        if slot == ClassTag.Equipment.Boots:
            prev_item = self._boots
            self._boots = item
        if slot == ClassTag.Equipment.MainHand:
            prev_item = self._main_hand
            self._main_hand = item
        if slot == ClassTag.Equipment.OffHand:
            prev_item = self._off_hand
            self._off_hand = item
        return prev_item

    def get_total_buffs(self):
        buffs = Buffs()
        for item in self.get_all_equipped_items():
            item_buffs = item.get_buffs()
            if item_buffs is not None:
                buffs.con_buff += item_buffs.con_buff
                buffs.str_buff += item_buffs.str_buff
                buffs.dex_buff += item_buffs.dex_buff
                buffs.int_buff += item_buffs.int_buff
                buffs.lck_buff += item_buffs.lck_buff
                buffs.mem_buff += item_buffs.mem_buff
        return buffs

    def _get_total_armor(self):
        armor: int = 0
        for item in self.get_all_equipped_items():
            armor_stats: ArmorStats = item.get_armor_stats()
            if armor_stats is not None:
                armor += armor_stats.get_armor_amount()
        return armor

    def get_total_reduced_armor(self, level: int):
        armor: int = 0
        for item in self.get_all_equipped_items():
            armor_stats: ArmorStats = item.get_armor_stats()
            if armor_stats is not None:
                reduce_to: float = max(0, 1.0 - (ARMOR_OVERLEVELED_DEBUFF * max(0, item.get_level_requirement() - level)))
                armor += int(armor_stats.get_armor_amount() * reduce_to)
        return armor

    def get_total_armor_str(self, level: int):
        armor: int = self._get_total_armor()
        reduced_armor: int = self.get_total_reduced_armor(level)
        
        if armor != reduced_armor:
            return f"{armor} (-{armor - reduced_armor}) Armor"
        return f"{armor} Armor"

    def get_num_slots_unequipped(self):
        equipment = [
            self._helmet,
            self._amulet,
            self._chest_armor,
            self._gloves,
            self._ring,
            self._leggings,
            self._boots,
            self._main_hand,
            self._off_hand
        ]
        return len(list(filter(lambda item: item is None, equipment)))

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


class ItemEquipButton(discord.ui.Button):
    def __init__(self, exact_item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
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


class UnequipButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Unequip", row=row)
        
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: EquipmentView = self.view
        if interaction.user == view.get_user():
            response = view.unequip_item()
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

        player: Player = self.get_player()
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)

        description = ""
        if equipped_item is not None:
            description += f"──────────\n{equipped_item}\n──────────\n\n"
        description += "Choose an item from your inventory to equip."

        return Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description=description
        )

    def equip_item(self, exact_item_index: int):
        player: Player = self.get_player()
        inventory: Inventory = player.get_inventory()
        equipment: Equipment = player.get_equipment()
        expertise: Expertise = player.get_expertise()

        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        embed = Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description="*Error: Could not equip that item.*\n\nChoose an item from your inventory to equip."
        )
        # The "exact_item_index" here is the index of the item with respect to the entire
        # inventory. This is used instead of an adjusted index here because the items are
        # filtered when displayed to the user, so adjusting based on page size wouldn't work.
        found_index = inventory.item_exists(inventory.get_inventory_slots()[exact_item_index])
        if found_index == exact_item_index:
            item = inventory.remove_item(exact_item_index, 1)
            prev_item = equipment.equip_item_to_slot(self._cur_equip_slot, item)

            if prev_item is not None:
                inventory.add_item(prev_item)

            embed = Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"──────────\n{item}\n──────────\n\nEquipped! You can choose a different item from your inventory to equip or exit."
            )

            expertise.update_stats(equipment.get_total_buffs())
        
        self._get_current_page_buttons()
        return embed

    def unequip_item(self):
        player: Player = self.get_player()
        equipment: Equipment = player.get_equipment()
        inventory: Inventory = player.get_inventory()
        expertise: Expertise = player.get_expertise()

        equipped_item: (Item | None) = equipment.unequip_item_from_slot(self._cur_equip_slot)
        inventory.add_item(equipped_item)

        expertise.update_stats(equipment.get_total_buffs())

        self._get_current_page_buttons()

        return Embed(
            title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
            description = "None equipped. Choose an item from your inventory to equip."
        )

    def display_item_in_slot(self, slot: ClassTag.Equipment):
        self._cur_equip_slot = slot
        return self.enter_equip_for_slot()

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
            exact_item_index: int = filtered_indices[i + (self._page * self._NUM_PER_PAGE)]
            self.add_item(ItemEquipButton(exact_item_index, item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(filtered_items) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)
        if equipped_item is not None:
            self.add_item(UnequipButton(min(4, len(page_slots))))
        self.add_item(SelectSlotExitButton(min(4, len(page_slots))))

    def get_full_equipment_str(self):
        player_equipment: Equipment = self.get_player().get_equipment()
        base_none_equipped_str: str = "──────────\nNone Equipped\n──────────"

        equipment_strs = [
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Helmet))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Helmet) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Gloves))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Gloves) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Amulet))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Amulet) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Ring))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Ring) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.MainHand))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.MainHand) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.ChestArmor))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.ChestArmor) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.OffHand))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.OffHand) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Leggings))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Leggings) is not None else base_none_equipped_str,
            f"──────────\n{str(player_equipment.get_item_in_slot(ClassTag.Equipment.Boots))}\n──────────" if player_equipment.get_item_in_slot(ClassTag.Equipment.Boots) is not None else base_none_equipped_str
        ]

        return "\n\n".join(equipment_strs)

    def get_initial_info(self):
        return Embed(
            title=f"{self._user.display_name}'s Equipment",
            description=f"{self.get_full_equipment_str()}\n\nChoose a slot to see currently equipped item and equip another or unequip it."
        )

    def exit_to_main_menu(self):
        self._cur_equip_slot = None
        self._display_slot_select_buttons()
        return self.get_initial_info()

    def _get_current_equip_page_info(self):
        player: Player = self.get_player()
        equipped_item: (Item | None) = player.get_equipment().get_item_in_slot(self._cur_equip_slot)

        if equipped_item is not None:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"──────────\n{equipped_item}\n──────────\n\nChoose an item from your inventory to equip."
            )
        else:
            return Embed(
                title=f"Equip to {self.get_str_for_slot(self._cur_equip_slot)}",
                description=f"None equipped. Choose an item from your inventory to equip."
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
