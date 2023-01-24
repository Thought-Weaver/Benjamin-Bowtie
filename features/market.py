from __future__ import annotations

import discord

from discord.embeds import Embed
from discord.ext import commands
from features.expertise import Expertise, ExpertiseClass
from features.npcs.abarra import BlacksmithView
from features.npcs.copperbroad import ChefView
from features.npcs.tiatha import DruidView
from features.npcs.viktor import RandomItemMerchantView
from features.npcs.yenna import YennaView
from features.shared.item import Rarity
from features.shared.nextbutton import NextButton
from features.shared.prevbutton import PrevButton
from math import floor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.inventory import Inventory
    from features.player import Player
    from features.stats import Stats
    from features.shared.item import Item

# -----------------------------------------------------------------------------
# MODAL
# -----------------------------------------------------------------------------

class SellModal(discord.ui.Modal):
    def __init__(self, database: dict, guild_id: int, user: discord.User, item_index: int, item: Item, view: MarketView, message_id: int):
        super().__init__(title=f"Sell {item.get_full_name_and_count()}")

        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._item = item
        self._item_index = item_index
        self._view = view
        self._message_id = message_id

        self._count_input: discord.ui.TextInput = discord.ui.TextInput(
            label="Quantity",
            default="1",
            required=True
        )
        self.add_item(self._count_input)

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    async def on_submit(self, interaction: discord.Interaction):
        player: Player = self._get_player(self._user.id)
        inventory: Inventory = player.get_inventory()

        found_index = inventory.item_exists(self._item)
        if found_index != self._item_index:
            await interaction.response.send_message(f"Error: Something about your inventory changed.")
            return
            
        if not self._count_input.value.isnumeric() or int(self._count_input.value) <= 0:
            await interaction.response.send_message(f"Error: You must sell a positive number of that item.")
            return

        if int(self._count_input.value) > self._item.get_count():
            await interaction.response.send_message(f"Error: You can't sell {int(self._count_input.value)} of that item, you only have {self._item.get_count()}.")
            return

        amount_to_sell: int = int(self._count_input.value)
        inventory.remove_item(self._item_index, amount_to_sell)
        item_value: int = self._item.get_value()
        item_rarity: Rarity = self._item.get_rarity()
        total_amount: int = item_value * amount_to_sell
        inventory.add_coins(total_amount)

        player_stats: Stats = player.get_stats()
        player_stats.market.items_sold += amount_to_sell
        player_stats.market.coins_made += item_value * amount_to_sell

        player_xp: Expertise = player.get_expertise()
        base_xp: int = 0
        if item_rarity == Rarity.Uncommon:
            base_xp = 1
        if item_rarity == Rarity.Rare:
            base_xp = 2
        if item_rarity == Rarity.Epic:
            base_xp = 3
        if item_rarity == Rarity.Legendary:
            base_xp = 5
        if item_rarity == Rarity.Artifact:
            base_xp = 8

        xp_to_add: int = amount_to_sell * base_xp
        xp_to_add = player_xp.add_xp_to_class(xp_to_add, ExpertiseClass.Merchant, player.get_equipment())
    
        amount_str: str = ""
        if total_amount == 1:
            amount_str = "1 coin"
        else:
            amount_str = f"{total_amount} coins"

        description = f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}.\n\n*Sold {amount_to_sell} {self._item.get_full_name()} for {amount_str}!*"
        if xp_to_add > 0:
            description += f" *(+{xp_to_add} Merchant xp)*"

        embed = Embed(
            title="Selling at the Market",
            description=description
        )

        await self._view.refresh(self._message_id, embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Error: Something has gone terribly wrong.")

# -----------------------------------------------------------------------------
# MARKET VIEW
# -----------------------------------------------------------------------------

class InventorySellButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_name_and_count()} [{item.get_value_str()} each]", row=row, emoji=item.get_icon())
        self._item = item
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view

        if view.get_user() == interaction.user:
            await interaction.response.send_modal(SellModal(
                view.get_database(),
                view.get_guild_id(),
                view.get_user(),
                self._item_index,
                self._item,
                view,
                interaction.message.id)
            )


class MarketSellButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Sell", row=row)

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


class YennaButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Visit Yenna", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            yenna_view: YennaView = YennaView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = yenna_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=yenna_view)


class BlacksmithButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Visit Abarra", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            blacksmith_view: BlacksmithView = BlacksmithView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = blacksmith_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=blacksmith_view)


class ChefButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Visit Copperbroad", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            blacksmith_view: ChefView = ChefView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = blacksmith_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=blacksmith_view)


class RandomItemMerchantButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Visit Viktor", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            random_item_merchant_view: RandomItemMerchantView = RandomItemMerchantView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = random_item_merchant_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=random_item_merchant_view)


class CompanionMerchantButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.secondary, label="Visit Tiatha", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            companion_merchant_view: DruidView = DruidView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_user())
            embed = companion_merchant_view.get_initial_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=companion_merchant_view)


class MarketView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, user: discord.User, context: commands.Context):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._context = context

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
            self.add_item(InventorySellButton(i + (self._page * self._NUM_PER_PAGE), item, i))
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
        self.add_item(YennaButton(0))
        self.add_item(BlacksmithButton(1))
        self.add_item(ChefButton(1))
        self.add_item(CompanionMerchantButton(1))
        self.add_item(RandomItemMerchantButton(2))
        self.add_item(MarketSellButton(3))

    def enter_sell_market(self):
        self._get_current_page_buttons()
        
        player: Player = self._get_player()
        inventory = player.get_inventory()

        return Embed(
            title="Selling at the Market",
            description=f"Choose an item from your inventory to sell. You have {inventory.get_coins_str()}."
        )
    
    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )

    async def refresh(self, message_id: int, embed: Embed):
        self._get_current_page_buttons()
        message: discord.Message = await self._context.fetch_message(message_id)
        await message.edit(view=self, embed=embed)

    def get_bot(self):
        return self._bot

    def get_user(self):
        return self._user

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id
