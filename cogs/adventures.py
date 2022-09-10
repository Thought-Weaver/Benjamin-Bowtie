import jsonpickle
import os
import random
import shutil
import time

from discord import User
from discord.embeds import Embed
from discord.ext import commands, tasks

from bot import BenjaminBowtieBot
from features.inventory import InventoryView
from features.mail import Mail, MailView, MailboxView
from features.market import MarketView
from features.player import Player
from features.stats import StatCategory, StatView, Stats
from features.shared.item import Item, LOADED_ITEMS, ItemKey
from features.stories.forest import ForestStory
from features.stories.ocean import OceanStory
from features.stories.story import Story
from features.stories.underworld import UnderworldStory
from games.knucklebones import Knucklebones

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.inventory import Inventory


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

        if self._database.get("stories") is None:
            self._database[guild_id_str]["stories"] = {}
            self._database[guild_id_str]["stories"][Story.Forest] = ForestStory()
            self._database[guild_id_str]["stories"][Story.Ocean] = OceanStory()
            self._database[guild_id_str]["stories"][Story.Underworld] = UnderworldStory()
        
        if self._database[guild_id_str]["members"].get(user_id_str) is None:
            self._database[guild_id_str]["members"][user_id_str] = Player()

    def _get_player(self, guild_id: int, user_id: int) -> Player:
        return self._database[str(guild_id)]["members"][str(user_id)]

    def _get_story(self, guild_id: int, story_key: Story):
        return self._database[str(guild_id)]["stories"][story_key]

    @tasks.loop(hours=1)
    async def save_database(self):
        if os.path.isfile("./adventuresdb.json"):
            shutil.copy("adventuresdb.json", "adventuresdbbackup.json")
        
        frozen = jsonpickle.encode(self._database)
        with open("adventuresdb.json", "w") as file:
            file.write(frozen)
    
    @commands.is_owner()
    @commands.command(name="saveadventures", help="Saves the adventures database", hidden=True)
    async def save_adventures_handler(self, context: commands.Context):
        await self.save_database()
        await context.send("The adventures database has been saved!")

    @commands.command(name="fish", help="Begins a fishing minigame to catch fish and mysterious items")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fish_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()
        fishing_result: Item = None

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        player_stats: Stats = author_player.get_stats()

        # 55% chance of getting a Common non-fish reward
        if 0.0 <= rand_val < 0.55:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.BasicBoots), 
                LOADED_ITEMS.get_new_item(ItemKey.ClumpOfLeaves), 
                LOADED_ITEMS.get_new_item(ItemKey.Conch)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.common_items_caught += 1
        # 20% chance of getting a Common fish reward
        if 0.55 <= rand_val < 0.75:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Minnow),
                LOADED_ITEMS.get_new_item(ItemKey.Roughy),
                LOADED_ITEMS.get_new_item(ItemKey.Shrimp)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.common_fish_caught += 1
        # 15% chance of getting an Uncommon fish reward
        if 0.75 <= rand_val < 0.9:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Oyster),
                LOADED_ITEMS.get_new_item(ItemKey.Pufferfish)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.uncommon_fish_caught += 1
        # 9.5% chance of getting a Rare fish reward
        if 0.9 <= rand_val < 0.995:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Squid),
                LOADED_ITEMS.get_new_item(ItemKey.Crab),
                LOADED_ITEMS.get_new_item(ItemKey.Lobster),
                LOADED_ITEMS.get_new_item(ItemKey.Shark)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.rare_fish_caught += 1
        # 0.49% chance of getting a Rare non-fish reward
        if 0.995 <= rand_val < 0.9999:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Diamond),
                LOADED_ITEMS.get_new_item(ItemKey.AncientVase),
                LOADED_ITEMS.get_new_item(ItemKey.MysteriousScroll)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.rare_items_caught += 1
        # 0.01% chance of getting the Epic story reward
        if 0.9999 <= rand_val <= 1.0:
            items = [LOADED_ITEMS.get_new_item(ItemKey.FishMaybe)]
            fishing_result = random.choice(items)
            player_stats.fish.epic_fish_caught += 1
        
        # E(X) =
        # 0.55 * (2 + 1 + 1) / 3 +
        # 0.2 * (3 + 4 + 3) / 3 +
        # 0.15 * (4 + 5) / 2 +
        # 0.095 * (10 + 8 + 8 + 10) / 3 +
        # 0.0049 * (40 + 50 + 30) / 3 +
        # 0.0001 * 1 =
        # 3.41 every 30 seconds -> 409.2 an hour
        
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
    async def stats_handler(self, context: commands.Context, stat_category_name:StatCategory=None):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        stat_view = StatView(self._bot, self._database, context.guild.id, context.author, stat_category_name)
        embed = stat_view.get_current_page_info()
        await context.send(embed=embed, view=stat_view)

    @commands.command(name="wishingwell", help="Toss a coin into the wishing well", aliases=["ww"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wishing_well_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_inv: Inventory = author_player.get_inventory()
        if author_inv.get_coins() == 0:
            await context.send(f"You don't have any coins.")
            return
        author_inv.remove_coins(1)
        player_stats: Stats = author_player.get_stats()

        # E(X) = 0.995 * -1 + 0.0021 * 500 = 0.055 every 5 seconds -> 39.6 per hour

        # 99.5% chance of getting nothing
        if 0.0 <= rand_val < 0.995:
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and hits the bottom with a resounding clink."
            )
            await context.send(embed=embed)
        # 0.21% chance of getting 500 coins
        if 0.995 <= rand_val < 0.9971:
            author_player.get_inventory().add_coins(500)
            player_stats.wishingwell.coins_received += 500
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and you feel a sense of duplication. One becoming many."
            )
            await context.send(embed=embed)
        # 0.28% chance of getting an Epic item
        if 0.9971 <= rand_val < 0.9999:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Diamond),
                LOADED_ITEMS.get_new_item(ItemKey.AncientVase),
                LOADED_ITEMS.get_new_item(ItemKey.MysteriousScroll)
            ]
            result: Item = random.choice(items)
            mail: Mail = Mail("Wishing Well", result, 0, "Not a gift. A trade.", str(time.time()).split(".")[0], -1)
            author_player.get_mailbox().append(mail)
            player_stats.wishingwell.items_received += 1
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below. Then, you close your eyes and are surrounded by a gust of wind. You suddenly find yourself standing in front of your mailbox."
            )
            await context.send(embed=embed)
        # 0.01% chance of stirring something in the world
        if 0.9999 <= rand_val <= 1:
            story: UnderworldStory = self._get_story(context.guild.id, Story.Underworld)

            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and hits the bottom with a resounding clink."
            )
            if story.something_stirs == 0:
                embed = Embed(
                    title="You toss the coin in...",
                    description="It plummets into the darkness below." \
                        "Down, down it goes -- past the bottom of the well, through rock and flowing fire into deeper darkness still, down into a place the living believe only superstition.\n\n" \
                        "Somewhere deep in the sunless underworld... something stirs."
                )
            elif player_stats.wishingwell.something_stirs == 0:
                embed = Embed(
                    title="You toss the coin in...",
                    description="It plummets into the darkness below." \
                        "The coin of someone else, yes, but it too slips beyond the material into the shadows. There is no sound to you above; it is simply gone in a haunting silence.\n\n" \
                        "Somewhere deep in the sunless underworld... something stirs."
                )
            else:
                embed = Embed(
                    title="You toss the coin in...",
                    description="It plummets into the darkness below." \
                        "You've come again. And your coin, like the other before it, descends descends descends. The darkness grabs it close, pulling the coin quickly towards its inevitable destination.\n\n" \
                        "Somewhere deep in the sunless underworld... something stirs."
                )
            
            story.something_stirs += 1
            player_stats.wishingwell.something_stirs += 1

            await context.send(embed=embed)

        player_stats.wishingwell.coins_tossed += 1


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
