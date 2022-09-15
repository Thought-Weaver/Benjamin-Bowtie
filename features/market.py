from __future__ import annotations
from math import floor

import discord

from discord.embeds import Embed
from features.expertise import Expertise, ExpertiseClass
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player
    from features.stats import Stats
    from features.shared.item import Item


class InventorySellButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()} [{item.get_value_str()} each]", row=item_index)
        self._item = item
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view

        if view.get_user() == interaction.user:
            response = view.sell_item(self._item_index, self._item)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketSellButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Sell")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            response = view.enter_sell_market()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketExitButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.red, label="Exit", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 4
        
        self._display_initial_buttons()

    def _get_player(self) -> Player:
        return self._database[str(self._guild_id)]["members"][str(self._user.id)]

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._get_player()
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventorySellButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(4, len(page_slots))))
        if len(all_slots) - self._NUM_PER_PAGE * (self._page + 1) > 0:
            self.add_item(NextButton(min(4, len(page_slots))))
        self.add_item(MarketExitButton(min(4, len(page_slots))))
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

        player: Player = self._get_player()
        inventory = player.get_inventory()

        return Embed(
            title="Selling at the Market",
            description=f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}."
        )

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

        player: Player = self._get_player()
        inventory = player.get_inventory()

        return Embed(
            title="Selling at the Market",
            description=f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}."
        )

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(MarketSellButton())

    def enter_sell_market(self):
        self._get_current_page_buttons()
        
        player: Player = self._get_player()
        inventory = player.get_inventory()

        return Embed(
            title="Selling at the Market",
            description=f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}."
        )

    def sell_item(self, item_index: int, item: Item):
        # TODO: Rather than selling one at a time, create a modal that'll let you choose
        # how many to sell!
        player: Player = self._get_player()
        inventory = player.get_inventory()

        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        embed = Embed(
            title="Selling at the Market",
            description=f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}.\n\n*Error: That item couldn't be sold.*"
        )
        adjusted_index = item_index + (self._page * self._NUM_PER_PAGE)
        found_index = inventory.item_exists(item)
        if found_index == adjusted_index:
            inventory.remove_item(adjusted_index, 1)
            item_value: int = item.get_value()
            inventory.add_coins(item_value)

            player_stats: Stats = player.get_stats()
            player_stats.market.items_sold += 1
            player_stats.market.coins_made += item_value

            player_xp: Expertise = player.get_expertise()
            xp_to_add: int = floor(item_value / 4)
            player_xp.add_xp_to_class(xp_to_add, ExpertiseClass.Merchant)
        
            description = f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}.\n\n*Sold 1 {item.get_full_name()} for {item.get_value_str()}!*"
            if xp_to_add > 0:
                description += f" *(+{xp_to_add} Merchant xp)*"

            embed = Embed(
                title="Selling at the Market",
                description=description
            )
        
        self._get_current_page_buttons()
        return embed
    
    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )

    def get_user(self):
        return self._user