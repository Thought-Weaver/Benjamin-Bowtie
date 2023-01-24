from __future__ import annotations
from uuid import uuid4

import discord

from discord import Embed
from strenum import StrEnum
from features.companions.companion import BlueFlitterwingButterflyCompanion, Companion, FleetfootRabbitCompanion, SunbaskTurtleCompanion, TanglewebSpiderCompanion, VerdantSlithererCompanion, WanderboundRavenCompanion
from features.npcs.npc import NPCRoles
from features.shared.item import LOADED_ITEMS, Item, ItemKey
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.companions.player_companions import PlayerCompanions
    from features.inventory import Inventory
    from features.player import Player

# -----------------------------------------------------------------------------
# NPC VIEW
# -----------------------------------------------------------------------------

class Intent(StrEnum):
    Wares = "Wares"
    Companions = "Companions"


class EnterWaresButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Wares", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DruidView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_wares()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class EnterCompanionsButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="Browse Companions", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DruidView = self.view

        if view.get_user() == interaction.user:
            response = view.enter_companions()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ExitButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.red, label="Back", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DruidView = self.view

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
        
        view: DruidView = self.view
        if interaction.user == view.get_user():
            response = view.select_wares_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class CompanionsDisplayButton(discord.ui.Button):
    def __init__(self, companion: Companion, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{companion.get_name()}", row=row, emoji=companion.get_icon())
        
        self._companion = companion

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DruidView = self.view
        if interaction.user == view.get_user():
            response = view.select_companion(self._companion)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ConfirmButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: DruidView = self.view
        if interaction.user == view.get_user():
            response = view.confirm_using_intent()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class DruidView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user

        self._druid: DruidView = database[str(guild_id)]["npcs"][NPCRoles.CompanionMerchant]

        self._wares: List[Item] = [
            LOADED_ITEMS.get_new_item(ItemKey.Grub)
        ]
        self._selected_item: (Item | None) = None
        self._selected_item_index: int = -1

        self._companions: List[Companion] = [
            BlueFlitterwingButterflyCompanion(),
            FleetfootRabbitCompanion(),
            SunbaskTurtleCompanion(),
            TanglewebSpiderCompanion(),
            VerdantSlithererCompanion(),
            WanderboundRavenCompanion()
        ]
        self._selected_companion: (Companion | None) = None

        self._intent: (Intent | None) = None

        self._page = 0
        self._NUM_PER_PAGE = 4

        self._COST_ADJUST = 1.5 # 50% price increase from base when purchasing items

        self.show_initial_buttons()
        
    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def get_initial_embed(self):
        # TODO: Design the grove and description
        return Embed(
            title="",
            description=(
                ""
            )
        )

    def show_initial_buttons(self):
        self.clear_items()
        self.add_item(EnterWaresButton(0))
        self.add_item(EnterCompanionsButton(1))

    def get_embed_for_intent(self):
        player: Player = self._get_player()
        if self._intent == Intent.Wares:
            return Embed(
                title="Browse Wares",
                description=(
                    "\"Not much on me, but maybe one of your companions will like something I have!\"\n\n"
                    f"You have {player.get_inventory().get_coins_str()}."
                )
            )
        if self._intent == Intent.Companions:
            return Embed(
                title="Browse Companions",
                description=(
                    "\"Let's see if any of them take a liking to you!\"\n\n"
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

        actual_cost: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Wares",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{self._selected_item}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
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
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_item(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        if self._selected_item is not None and self._wares[self._selected_item_index] == self._selected_item:
            actual_value: int = int(self._selected_item.get_value() * self._COST_ADJUST) + 1
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

    def display_companion_info(self):
        player: Player = self._get_player()
        if self._selected_companion is None:
            self._get_companions_page_buttons()
            
            return Embed(
                title="Browse Companions",
                description=(
                    f"You have {player.get_inventory().get_coins_str()}.\n\n"
                    "Navigate through available companions using the Prev and Next buttons.\n\n"
                    "*Error: Something about that companion changed or it's no longer available.*"
                )
            )

        actual_cost: int = int(self._selected_companion.get_value() * self._COST_ADJUST) + 1
        actual_cost_str: str = f"{actual_cost} coin" if actual_cost == 1 else f"{actual_cost} coins"
        return Embed(
            title="Browse Companions",
            description=(
                f"You have {player.get_inventory().get_coins_str()}.\n\n"
                f"᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n{str(self._selected_companion)}\n\n**Price: {actual_cost_str}**\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n"
                "Navigate through available companions using the Prev and Next buttons."
            )
        )

    def select_companion(self, companion: Companion):
        self._selected_companion = companion

        self._get_companions_page_buttons()
        return self.display_companion_info()

    def _get_companions_page_buttons(self):
        self.clear_items()
        
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        companions: PlayerCompanions = player.get_companions()
        all_slots = list(filter(lambda c: c not in companions.companions.keys(), self._companions))

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, companion in enumerate(page_slots):
            self.add_item(CompanionsDisplayButton(companion, i))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        
        if self._selected_companion is not None:
            actual_value: int = int(self._selected_companion.get_value() * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                self.add_item(ConfirmButton(min(4, len(page_slots))))
        self.add_item(ExitButton(min(4, len(page_slots))))

    def _purchase_companion(self):
        player: Player = self._get_player()
        inventory: Inventory = player.get_inventory()
        companions: PlayerCompanions = player.get_companions()

        if self._selected_companion is not None:
            actual_value: int = int(self._selected_companion.get_value() * self._COST_ADJUST) + 1
            if inventory.get_coins() >= actual_value:
                inventory.remove_coins(actual_value)
                companions.companions[self._selected_companion.get_key()] = self._selected_companion.__class__() # type: ignore
                self._get_companions_page_buttons()

                return Embed(
                    title="Browse Companions",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available companions using the Prev and Next buttons.\n\n"
                        f"*You purchased {self._selected_companion.get_icon_and_name()}!*"
                    )
                )
            else:
                self._get_companions_page_buttons()

                return Embed(
                    title="Browse Companions",
                    description=(
                        f"You have {inventory.get_coins_str()}.\n\n"
                        "Navigate through available companions using the Prev and Next buttons.\n\n"
                        f"*Error: You don't have enough coins to acquire it!*"
                    )
                )

        self._get_companions_page_buttons()
        return Embed(
            title="Browse Companions",
            description=(
                f"You have {inventory.get_coins_str()}.\n\n"
                "Navigate through available companions using the Prev and Next buttons.\n\n"
                "*Error: Something about that companion changed or it's no longer available.*"
            )
        )

    def enter_companions(self):
        self._intent = Intent.Companions
        self._get_companions_page_buttons()
        return self.get_embed_for_intent()

    def confirm_using_intent(self):
        if self._intent == Intent.Wares:
            result = self._purchase_item()

            self._get_wares_page_buttons()

            return result
        if self._intent == Intent.Companions:
            result = self._purchase_companion()

            self._selected_companion = None
            self._get_companions_page_buttons()

            return result
        
        return self.get_initial_embed()

    def next_page(self):
        self._page += 1

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_companion = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Companions:
            self._get_companions_page_buttons()

        return self.get_embed_for_intent()

    def prev_page(self):
        self._page = max(0, self._page - 1)

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_companion = None

        if self._intent == Intent.Wares:
            self._get_wares_page_buttons()
        if self._intent == Intent.Companions:
            self._get_companions_page_buttons()

        return self.get_embed_for_intent()

    def return_to_main_menu(self):
        self._intent = None
        self._page = 0

        self._selected_item = None
        self._selected_item_index = -1
        self._selected_companion = None

        self.show_initial_buttons()
        return self.get_initial_embed()

    def get_user(self):
        return self._user
