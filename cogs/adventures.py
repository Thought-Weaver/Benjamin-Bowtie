from discord import embeds, User
from discord.ext import commands
from enum import Enum
from bot import BenjaminBowtieBot
from typing import List

from games.knucklebones import Knucklebones


class Item():
    def __init__(self, name: str, value: int, count=1, is_unique=False):
        self._name = name
        self._value = value
        self._count = count
        self._is_unique = is_unique

    def remove_amount(self, amount: int):
        if amount <= self._count:
            result = Item(self._name, self._value, amount, self._is_unique)
            self._count -= amount
            return result
        return None

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

    def get_count(self):
        return self._count

    def get_is_unique(self):
        return self._is_unique

    def __eq__(self, obj):
        if not isinstance(obj, Item):
            return False
        
        if self._is_unique or obj.get_is_unique():
            return False
        
        if self._name == obj.get_name() and self._value == obj.get_value():
            return True

        return False


class Inventory():
    def __init__(self):
        self._inventory_slots: List[Item] = []
        self._coins: int = 0

    def _organize_inventory_slots(self):
        new_slots: List[Item] = []
        for i in range(len(self._inventory_slots)):
            for j in range(i + 1, len(self._inventory_slots)):
                item: Item = self._inventory_slots[i]
                other_item: Item = self._inventory_slots[j]

                if item == other_item:
                    new_slots.append(Item(item.get_name(), item.get_value(), item.get_count() + other_item.get_count()))
                else:
                    if item.get_count() != 0:
                        new_slots.append(item)
                    if other_item.get_count() != 0:
                        new_slots.append(other_item)
        self._inventory_slots = new_slots

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

    def search_by_name(self, name: str):
        for i, item in enumerate(self._inventory_slots):
            if item.get_name() == name:
                return i
        return -1

    def get_inventory_slots(self):
        return self._inventory_slots

    def get_coins(self):
        return self._coins


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
    async def fish_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)

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

    @commands.command(name="mail", help="Send another player a gift from your !inv")
    async def mail_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        # The process will be:
        # (1) The user gets to select an item (as a button) from their inventory
        #     There will be 5 items in a row (4 rows of that), along with a 
        #     prev and next button to navigate on the final row
        # (2) On clicking a button, a modal will pop up asking how many to send and
        #     an optional message to send
        # https://github.com/Rapptz/discord.py/blob/master/examples/modals/basic.py


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
