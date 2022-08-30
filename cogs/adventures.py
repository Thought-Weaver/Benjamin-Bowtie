from math import ceil
import discord
from discord import embeds, User
from discord.ext import commands
from enum import Enum
from bot import BenjaminBowtieBot
from typing import List

from games.knucklebones import Knucklebones

import random

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


class Inventory():
    def __init__(self):
        self._inventory_slots: List[Item] = []
        self._coins: int = 0

    def _organize_inventory_slots(self):
        if len(self._inventory_slots) < 2:
            return
        
        item_set: List[Item] = []
        for item in self._inventory_slots:
            exists = False
            for item_in_set in item_set:
                if item_in_set == item:
                    exists = True
                    break
            if not exists:
                item_set.append(Item(item.get_icon(), item.get_name(), item.get_value(), 0, item.get_is_unique()))

        for item in item_set:
            for other_item in self._inventory_slots:
                if item == other_item:
                    item.add_amount(other_item.get_count())

        self._inventory_slots = sorted(item_set, key=lambda item: item.get_name())

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
        self._inventory_slots.append(item)
        self._organize_inventory_slots()

    def remove_item(self, slot_index: int, count=1):
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


class InventoryButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=int(item_index / 5))
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        await interaction.response.defer()


class MarketSellButton(discord.ui.Button):
    def __init__(self, item_index: int, item: Item):
        super().__init__(style=discord.ButtonStyle.secondary, label=f"{item.get_full_name_and_count()}", row=int(item_index / 5))
        self._item = item
        self._item_index = item_index

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view

        if view.get_user() == interaction.user:
            await view.sell_item(self._item_index, self._item)


# Could abstract into a generic button with some callback in the parent view?
class NextButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Next", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: InventoryView = self.view
        if interaction.user == view.get_user():
            view.next_page()


class PrevButton(discord.ui.Button):
    def __init__(self, row: int):
        super().__init__(style=discord.ButtonStyle.blurple, label="Prev", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: InventoryView = self.view
        if interaction.user == view.get_user():
            view.prev_page()


class InventoryView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User):
        super().__init__()

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 20

        self._get_current_page_buttons()

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(5, ceil(len(page_slots) / 5))))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(min(5, ceil(len(page_slots) / 5))))
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

    def get_user(self):
        return self._user


class MarketSellButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Sell")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            view.enter_sell_market()


class MarketExitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Exit")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: MarketView = self.view
        if interaction.user == view.get_user():
            response = view.exit_to_main_menu()
            await interaction.response.edit_message(content=None, embed=response, view=view)


class MarketView(discord.ui.View):
    def __init__(self, bot: commands.Bot, database: dict, guild_id: int, user: User):
        super().__init__()

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._user = user
        self._page = 0

        self._NUM_PER_PAGE = 20
        
        self._display_initial_buttons()

    def _get_current_page_buttons(self):
        self.clear_items()
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        all_slots = player.get_inventory().get_inventory_slots()

        page_slots = all_slots[self._page * self._NUM_PER_PAGE:min(len(all_slots), (self._page + 1) * self._NUM_PER_PAGE)]
        for i, item in enumerate(page_slots):
            self.add_item(InventoryButton(i, item))
        if self._page != 0:
            self.add_item(PrevButton(min(5, ceil(len(page_slots) / 5))))
        if len(page_slots) == self._NUM_PER_PAGE:
            self.add_item(NextButton(min(5, ceil(len(page_slots) / 5))))
        
    def next_page(self):
        self._page += 1
        self._get_current_page_buttons()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        self._get_current_page_buttons()

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(MarketSellButton())

    def enter_sell_market(self):
        self.clear_items()
        self._get_current_page_buttons()
        self.add_item(MarketExitButton())

    def sell_item(self, item_index: int, item: Item):
        # TODO: Rather than selling one at a time, create a modal that'll let you choose
        # how many to sell!
        player: Player = self._database[self._guild_id]["members"][self._user.id]
        inventory = player.get_inventory()
        # Need to check that the item still exists since there are async operations
        # that can happen with different views.
        found_index = inventory.item_exists(item)
        if found_index == item_index:
            inventory.remove_item(item_index, 1)
            inventory.add_coins(item.get_count() * item.get_value())
        return embeds.Embed(
            title="Selling at the Market",
            description="Choose an item from your inventory to sell!"
        )

    def exit_to_main_menu(self):
        self._display_initial_buttons()
        return embeds.Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )

    def get_user(self):
        return self._user


# If I need to change something, always change the enum key
# never the value, since I use the values to store data.
class ExpertiseCategoryNames(Enum):
    Fishing = "Fishing"


class Expertise():
    def __init__(self):
        self._xp: int = 0
        self._level: int = 0

    # Could be positive or negative, regardless don't go below 0.
    def add_xp(self, value: int):
        self._xp = max(0, self._xp + value)

    def get_xp(self):
        return self._xp

    def get_level(self):
        return self._level

    def get_xp_remaining_to_next_level(self):
        # TODO: Figure out good function here based on XP awarded
        # for tasks. Probably something linear?
        return self._level * 25


class Mail():
    def __init__(self, sender_name: str, item: Item, message: str, send_date: str):
        self._sender_name = sender_name
        self._item = item
        self._message = message
        self._send_date = send_date

    def get_sender_name(self):
        return self._sender_name

    def get_item(self):
        return self._item

    def get_message(self):
        return self._message

    def get_send_date(self):
        return self._send_date


class Player():
    def __init__(self):
        self._inventory = Inventory()
        self._expertise: dict[str, Expertise] = {item.value: Expertise() for item in ExpertiseCategoryNames}
        self._mailbox: List[Mail] = []

    def get_inventory(self):
        return self._inventory

    def get_expertise(self):
        return self._expertise
    
    def get_mailbox(self):
        return self._mailbox


class Adventures(commands.Cog):
    def __init__(self, bot: BenjaminBowtieBot):
        self._bot = bot
        self._database: dict = bot.database

    def _check_member_and_guild_existence(self, guild_id: int, user_id: int):
        if self._database.get(guild_id) is None:
            self._database[guild_id] = {}
            self._database[guild_id]["members"] = {}
        
        if self._database[guild_id]["members"].get(user_id) is None:
            self._database[guild_id]["members"][user_id] = Player()

    @commands.command(name="fish", help="Begins a fishing minigame to catch fish and mysterious items")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fish_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()
        fishing_result:Item = None

        # 55% chance of getting something worthless
        if 0.0 <= rand_val < 0.55:
            items = [Item("🥾", "Boot", 2), Item("🍂", "Clump of Leaves", 1), Item("🐚", "Conch", 1)]
            fishing_result = random.choice(items)
        # 20% chance of getting a Tier 3 reward
        if 0.55 < rand_val < 0.75:
            items = [Item("🐟", "Minnow", 3), Item("🐠", "Roughy", 4), Item("🦐", "Shrimp", 3)]
            fishing_result = random.choice(items)
        # 15% chance of getting a Tier 2 reward
        if 0.75 < rand_val < 0.9:
            items = [Item("🦪", "Oyster", 4), Item("🐡", "Pufferfish", 5)]
            fishing_result = random.choice(items)
        # 9% chance of getting a Tier 1 reward
        if 0.9 < rand_val < 0.99:
            items = [Item("🦑", "Squid", 10), Item("🦀", "Crab", 8), Item("🦞", "Lobster", 8)]
            fishing_result = random.choice(items)
        # 1% chance of getting a Tier 0 reward
        if 0.99 < rand_val <= 1.0:
            items = [Item("🏺", "Ancient Vase", 25), Item("💎", "Diamond", 50)]
            fishing_result = random.choice(items)
        
        # E(X) = 
        # 0.55 * (2 + 1 + 1) / 3 + 
        # 0.2 * (3 + 4 + 3) / 3 + 
        # 0.15 * (4 + 5) / 2 + 
        # 0.09 * (10 + 8 + 8) / 3 + 
        # 0.01 * (25 + 50) / 2 = 
        # 3.23 every 30 seconds -> 387.6 an hour
        
        author_player: Player = self._database[context.guild.id]["members"][context.author.id]
        author_player.get_inventory().add_item(fishing_result)

        embed = embeds.Embed(
            title=f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}!",
            description="It's been added to your !inventory"
        )
        await context.send(embed=embed)

    @commands.command(name="knucklebones", help="Face another player in a game of knucklebones")
    async def knucklebones_handler(self, context: commands.Context, user: User, amount: int):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        self._check_member_and_guild_existence(context.guild.id, user.id)

        # I don't think I need to keep track of the games in the database, since each message
        # will update itself as buttons are pressed becoming a self-contained game. So long as (1)
        # we check that the players pressing the buttons are valid which should happen naturally
        # based on turn checks; (2) when paying out we check that the player has the money to do
        # so, else the winner gets whatever's left that the other can pay.
        author_player: Player = self._database[context.guild.id]["members"][context.author.id] 
        challenged_player: Player = self._database[context.guild.id]["members"][user.id]
        if author_player.get_inventory().get_coins() < amount:
            await context.send(f"You don't have enough coins ({author_player.get_inventory().get_coins()}) to bet that much!")
            return
        if challenged_player.get_inventory().get_coins() < amount:
            await context.send(f"That person doesn't have enough coins ({challenged_player.get_inventory().get_coins()}) to bet that much!")
            return

        embed = embeds.Embed(
            title="Welcome to Knucklebones!",
            description=
            """Players will take alternating turns rolling dice. They will then choose a column in which to place the die result.

            If the opponent has dice of the same value in that same column, those dice are removed from their board.

            Two of the same die in a single column double their value. Three of the same die triple their value.

            When one player fills their board with dice, the game is over. The player with the most points wins.
            
            The game will begin when the other player accepts the invitation to play."""
        )

        await context.send(embed=embed, view=Knucklebones(self._bot, self._database, context.guild.id, context.author, user, amount))

    # @commands.command(name="mail", help="Send another player a gift from your !inv")
    # async def mail_handler(self, context: commands.Context):
        # self._check_member_and_guild_existence(context.guild.id, context.author.id)
        # The process will be:
        # (1) The user gets to select an item (as a button) from their inventory
        #     There will be 5 items in a row (4 rows of that), along with a 
        #     prev and next button to navigate on the final row
        # (2) On clicking a button, a modal will pop up asking how many to send and
        #     an optional message to send
        # https://github.com/Rapptz/discord.py/blob/master/examples/modals/basic.py

    @commands.command(name="inventory", help="Check your inventory", aliases= ["inv"])
    async def inventory_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = embeds.Embed(
            title=f"{context.author.display_name}'s Inventory",
            description="Navigate through your items using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=InventoryView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="market", help="Sell and buy items at the marketplace")
    async def mail_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = embeds.Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )
        await context.send(embed=embed, view=MarketView(self._bot, self._database, context.guild.id, context.author))


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
