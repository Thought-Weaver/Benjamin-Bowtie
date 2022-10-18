from __future__ import annotations

import discord

from discord import Embed
from features.dueling import Dueling
from features.equipment import Equipment
from features.expertise import Expertise, ExpertiseClass
from features.npcs.npc import NPC, NPCRoles
from features.shared.ability import BoundToGetLuckyIII, CounterstrikeIII, EvadeIII, HeavySlamII, PiercingStrikeIII, PressTheAdvantageI, ScarArmorII, SecondWindIII, WhirlwindIII
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from strenum import StrEnum

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"


class EnterWaresButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=0)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view

        if view.get_user() == interaction.user:
            response = view.return_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class WaresDisplayButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()}", row=row, emoji=item.get_icon())
        
        self._item_index = item_index
        self._item = item

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: BlacksmithView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class BlacksmithView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._blacksmith: BlacksmithView = database[str(guild_id)]["npcs"][NPCRoles.Blacksmith]
        self._wares: List[Item] = [
            LOADED_ITEMS.get_new_item(ItemKey.BasicDagger),
            LOADED_ITEMS.get_new_item(ItemKey.BasicSword)
        ]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        return Embed(
            title="Abarra's Smithy",
            description=(
                "Nearby the village market stands an unassuming hut, the home of one Abarra, the local blacksmith. Outside at his forge, you can hear him hammering away at the metal, honing his practiced craft.\n\n"
                "The heat increases drastically as you approach him, and all around you can see scattered the various pieces (plenty of horseshoes you note) he's been making.\n\n"
                "He looks up from his work for a moment to look at you, \"Hm? Hm.\" Then nods with his head towards a small selection of inventory items that he's been crafting for hopeful adventurers such as yourself."
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton())

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Hm.\" He nods to the various pieces of armor and weapons.\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        return self.get_initial_embed()

    def display_item_info(self):
        player: Player = self._get_player()
        if self._selected_item is None or not (0 <= self._selected_item_index < len(self._wares) and self._wares[self._selected_item_index] == self._selected_item):
            self._get_wares_page_buttons()
            
            return Embed(
                title="Browse Wares",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available wares using the Prev and Next buttons.\n\n"
                    "*Error: Something about that item changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_item.get_value() * self._COST_ADJUST)
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"──────────\n{self._selected_item}\n\n**Price: {actual_cost_str}**\n──────────\n\n"
                "Navigate through available wares using the Prev and Next buttons."
            )
        )

    def select_wares_item(self, index: int, item: Item):
        self._selected_item = item
        self._selected_item_index = index

        self._get_wares_page_buttons()
        return self.display_item_info()

    def _get_wares_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        all_slots = self._wares

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(WaresDisplayButton(i + (self._page * self._NUM_PER_PAGE), item, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_item is not None:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST)
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        if self._selected_item is not None and self._wares[self._selected_item_index] == self._selected_item:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST)
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                inventory.add_item(LOADED_ITEMS.get_new_item(self._selected_item.get_key()))
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*You purchased 1 {self._selected_item.get_full_name()}!*"
                    )
                )
            else:
                self._get_wares_page_buttons()

                return Embed(
                    title="Browse Wares",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available wares using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to buy that!*"
                    )
                )

        self._get_wares_page_buttons()
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available wares using the Prev and Next buttons.\n\n"
                "*Error: Something about that item changed or it's no longer available.*"
            )
        )

    def enter_wares(self):
        self._intent = Intent.Wares
        self._get_wares_page_buttons()
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._selected_item = None
            self._selected_item_index = -1
            self._get_wares_page_buttons()

            return result
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        self._selected_item = None
        self._selected_item_index = -1

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()

        self._selected_item = None
        self._selected_item_index = -1

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_user(self):
        return self._user

# -----------------------------------------------------------------------------
# NPC CLASS
# -----------------------------------------------------------------------------

class Blacksmith(NPC):
    def __init__(self):
        super().__init__("Abarra", NPCRoles.Blacksmith)

        # Inventory Setup
        self._restock_items = []
        self._restock_coins = 5000

        self._inventory.add_coins(self._restock_coins)
        for item in self._restock_items:
            self._inventory.add_item(item)
        
        # Expertise Setup
        self._expertise.add_xp_to_class(1000, ExpertiseClass.Fisher) # Level 5
        self._expertise.add_xp_to_class(3976, ExpertiseClass.Merchant) # Level 15
        self._expertise.add_xp_to_class(7000, ExpertiseClass.Guardian) # Level 25
        
        self._expertise.points_to_spend = 0
        
        self._expertise.constitution = 20
        self._expertise.intelligence = 0
        self._expertise.dexterity = 0
        self._expertise.strength = 16
        self._expertise.luck = 0
        self._expertise.memory = 9

        # Equipment Setup
        # TODO: Add items when they've been created
        # self._equipment.equip_item_to_slot(ClassTag.Equipment.Ring, None)

        self._expertise.update_stats(self._equipment.get_total_buffs())

        # Dueling Setup
        self._dueling.abilities = [
            WhirlwindIII(), SecondWindIII(), PiercingStrikeIII(),
            ScarArmorII(), CounterstrikeIII(), PressTheAdvantageI(),
            EvadeIII(), HeavySlamII(), BoundToGetLuckyIII()
        ]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        # TODO: Make each of these setup portions a private function in the class so I don't have
        # to duplicate everything between init and setstate. 
        self._name = state.get("_name", "Abarra")
        self._role = state.get("_role", NPCRoles.Blacksmith)
        
        self._inventory: Inventory | None = state.get("_inventory")
        if self._inventory is None:
            self._inventory = Inventory()

            self._restock_items = []
            self._restock_coins = 5000

            self._inventory.add_coins(self._restock_coins)
            for item in self._restock_items:
                self._inventory.add_item(item)

        self._equipment: Inventory | None = state.get("_equipment")
        if self._equipment is None:
            self._equipment = Equipment()

        self._expertise: Expertise | None = state.get("_expertise")
        if self._expertise is None:
            self._expertise = Expertise()

            self._expertise.add_xp_to_class(1000, ExpertiseClass.Fisher) # Level 5
            self._expertise.add_xp_to_class(3976, ExpertiseClass.Merchant) # Level 15
            self._expertise.add_xp_to_class(7000, ExpertiseClass.Guardian) # Level 25
            
            self._expertise.points_to_spend = 0
            
            self._expertise.constitution = 20
            self._expertise.intelligence = 0
            self._expertise.dexterity = 0
            self._expertise.strength = 16
            self._expertise.luck = 0
            self._expertise.memory = 9

            self._expertise.update_stats(self._equipment.get_total_buffs())

        self._dueling: Dueling | None = state.get("_dueling")
        if self._dueling is None:
            self._dueling = Dueling()

            self._dueling.abilities = [
                WhirlwindIII(), SecondWindIII(), PiercingStrikeIII(),
                ScarArmorII(), CounterstrikeIII(), PressTheAdvantageI(),
                EvadeIII(), HeavySlamII(), BoundToGetLuckyIII()
            ]
