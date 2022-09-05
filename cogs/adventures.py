import jsonpickle
import os
import random
import shutil

from discord import User
from discord.embeds import Embed
from discord.ext import commands, tasks

from bot import BenjaminBowtieBot
from features.inventory import Item, InventoryView
from features.mail import MailView, MailboxView
from features.market import MarketView
from features.player import Player
from features.stats import StatView, Stats
from games.knucklebones import Knucklebones


class Adventures(commands.Cog):
    def __init__(self, bot: BenjaminBowtieBot):
        self._bot = bot
        
        file_data = open("./adventuresdb.json", "r").read()
        self._database: dict = jsonpickle.decode(file_data) if os.path.isfile("./adventuresdb.json") else {}
        
        self.save_database.start()

    def _check_member_and_guild_existence(self, guild_id: int, user_id: int):
        guild_id_str: str = str(guild_id)
        user_id_str: str = str(user_id)

        if self._database.get(guild_id_str) is None:
            self._database[guild_id_str] = {}
            self._database[guild_id_str]["members"] = {}
        
        if self._database[guild_id_str]["members"].get(user_id_str) is None:
            self._database[guild_id_str]["members"][user_id_str] = Player()

    def _get_player(self, guild_id: int, user_id: int) -> Player:
        return self._database[str(guild_id)]["members"][str(user_id)]

    @tasks.loop(hour=1)
    async def save_database(self):
        if os.path.isfile("./adventuresdb.json"):
            shutil.copy("adventuresdb.json", "adventuresdbbackup.json")
        
        frozen = jsonpickle.encode(self._database)
        with open("adventuresdb.json", "w") as file:
            file.write(frozen)
    
    @commands.is_owner()
    @commands.command(name="saveadventures", help="Saves the adventures database")
    async def save_adventures_handler(self, context: commands.Context):
        await self.save_database()
        await context.send("The adventures database has been saved!")

    @commands.command(name="fish", help="Begins a fishing minigame to catch fish and mysterious items")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fish_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()
        fishing_result:Item = None

        author_player: Player = self._database[str(context.guild.id)]["members"][str(context.author.id)]
        player_stats: Stats = author_player.get_stats()

        # 55% chance of getting a Tier 4 reward
        if 0.0 <= rand_val < 0.55:
            items = [Item("🥾", "Boot", 2), Item("🍂", "Clump of Leaves", 1), Item("🐚", "Conch", 1)]
            fishing_result = random.choice(items)
            player_stats.fish.tier_4_caught += 1
        # 20% chance of getting a Tier 3 reward
        if 0.55 < rand_val < 0.75:
            items = [Item("🐟", "Minnow", 3), Item("🐠", "Roughy", 4), Item("🦐", "Shrimp", 3)]
            fishing_result = random.choice(items)
            player_stats.fish.tier_3_caught += 1
        # 15% chance of getting a Tier 2 reward
        if 0.75 < rand_val < 0.9:
            items = [Item("🦪", "Oyster", 4), Item("🐡", "Pufferfish", 5)]
            fishing_result = random.choice(items)
            player_stats.fish.tier_2_caught += 1
        # 9% chance of getting a Tier 1 reward
        if 0.9 < rand_val < 0.99:
            items = [Item("🦑", "Squid", 10), Item("🦀", "Crab", 8), Item("🦞", "Lobster", 8), Item("🦈", "Shark", 10)]
            fishing_result = random.choice(items)
            player_stats.fish.tier_1_caught += 1
        # 1% chance of getting a Tier 0 reward
        if 0.99 < rand_val <= 1.0:
            items = [Item("🏺", "Ancient Vase", 40), Item("💎", "Diamond", 50), Item("📜", "Mysterious Scroll", 30)]
            fishing_result = random.choice(items)
            player_stats.fish.tier_0_caught += 1
        
        # E(X) = 
        # 0.55 * (2 + 1 + 1) / 3 + 
        # 0.2 * (3 + 4 + 3) / 3 + 
        # 0.15 * (4 + 5) / 2 + 
        # 0.09 * (10 + 8 + 8) / 3 + 
        # 0.01 * (25 + 50) / 2 = 
        # 3.23 every 30 seconds -> 387.6 an hour
        
        author_player.get_inventory().add_item(fishing_result)

        embed = Embed(
            title=f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}!",
            description="It's been added to your b!inventory"
        )
        await context.send(embed=embed)

    @commands.command(name="knucklebones", help="Face another player in a game of knucklebones")
    async def knucklebones_handler(self, context: commands.Context, user: User=None, amount: int=0):
        if user is None:
            await context.send("You need to @ a member to use b!knucklebones.")
            return

        if user == context.author:
            await context.send("You can't challenge yourself to a game of knucklebones.")
            return
            
        if user.bot:
            await context.send("You can't challenge a bot to knucklebones (but Benjamin Bowtie might learn how to play one day!)")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        self._check_member_and_guild_existence(context.guild.id, user.id)

        if amount < 0:
            await context.send(f"You have to bet a non-negative number of coins!")
            return

        # I don't think I need to keep track of the games in the database, since each message
        # will update itself as buttons are pressed becoming a self-contained game. So long as (1)
        # we check that the players pressing the buttons are valid which should happen naturally
        # based on turn checks; (2) when paying out we check that the player has the money to do
        # so, else the winner gets whatever's left that the other can pay.
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        challenged_player: Player = self._get_player(context.guild.id, user.id)
        if author_player.get_inventory().get_coins() < amount:
            await context.send(f"You don't have enough coins ({author_player.get_inventory().get_coins()}) to bet that much!")
            return
        if challenged_player.get_inventory().get_coins() < amount:
            await context.send(f"That person doesn't have enough coins ({challenged_player.get_inventory().get_coins()}) to bet that much!")
            return

        embed = Embed(
            title="Welcome to Knucklebones!",
            description="Players will take alternating turns rolling dice. They will then choose a column in which to place the die result.\n\n" \
            "If the opponent has dice of the same value in that same column, those dice are removed from their board.\n\n" \
            "Two of the same die in a single column double their value. Three of the same die triple their value.\n\n" \
            "When one player fills their board with dice, the game is over. The player with the most points wins.\n\n" \
            "The game will begin when the other player accepts the invitation to play."
        )

        await context.send(embed=embed, view=Knucklebones(self._bot, self._database, context.guild.id, context.author, user, amount))

    @commands.command(name="mail", help="Send another player a gift")
    async def mail_handler(self, context: commands.Context, giftee: User=None):
        if giftee is None:
            await context.send("You need to @ a member to use !mail")
            return
        
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        self._check_member_and_guild_existence(context.guild.id, giftee.id)
        # The process will be:
        # (1) The user gets to select an item (as a button) from their inventory
        #     There will be 5 items in a row (4 rows of that), along with a 
        #     prev and next button to navigate on the final row
        # (2) Upon clicking a button, a modal will pop up asking how many to send and
        #     an optional message to send
        player: Player = self._get_player(context.guild.id, context.author.id)
        coins_str = player.get_inventory().get_coins_str()
        embed = Embed(
            title=f"{context.author.display_name}'s Inventory",
            description=f"You have {coins_str}.\n\nChoose an item to mail to {giftee.display_name}!"
        )
        await context.send(embed=embed, view=MailView(self._bot, self._database, giftee, context))

    @commands.command(name="inventory", help="Check your inventory", aliases=["inv"])
    async def inventory_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        player: Player = self._get_player(context.guild.id, context.author.id)
        coins_str = player.get_inventory().get_coins_str()
        embed = Embed(
            title=f"{context.author.display_name}'s Inventory",
            description=f"You have {coins_str}.\n\nNavigate through your items using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=InventoryView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="market", help="Sell and buy items at the marketplace", aliases=["marketplace"])
    async def market_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )
        await context.send(embed=embed, view=MarketView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="mailbox", help="Open mail you've received from others", aliases=["inbox"])
    async def mailbox_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        embed = Embed(
            title=f"{context.author.display_name}'s Mailbox",
            description=f"Navigate through your mail using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=MailboxView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="stats", help="See your stats")
    async def stats_handler(self, context: commands.Context, stat_category_name:str=None):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        stat_view = StatView(self._bot, self._database, context.guild.id, context.author, stat_category_name)
        embed = stat_view.get_current_page_info()
        await context.send(embed=embed, view=stat_view)


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
