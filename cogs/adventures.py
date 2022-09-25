from __future__ import annotations

import jsonpickle
import os
import random
import shutil
import time

from discord import User
from discord.embeds import Embed
from discord.ext import commands, tasks

from bot import BenjaminBowtieBot
from features.dueling import PlayerVsPlayerDuelView
from features.equipment import EquipmentView
from features.expertise import ExpertiseClass, ExpertiseView
from features.inventory import InventoryView
from features.mail import Mail, MailView, MailboxView
from features.market import MarketView
from features.player import Player
from features.stats import StatCategory, StatView
from features.shared.item import Item, LOADED_ITEMS, ItemKey
from features.stories.forest import ForestStory
from features.stories.ocean import OceanStory
from features.stories.story import Story
from features.stories.underworld import UnderworldStory
from games.knucklebones import Knucklebones

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from features.dueling import Dueling
    from features.expertise import Expertise
    from features.inventory import Inventory
    from features.stats import Stats


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

        if self._database[guild_id_str].get("stories") is None:
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
        xp_to_add: int = 0
        xp_class: ExpertiseClass = ExpertiseClass.Fisher

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't fish.")
            return
        
        player_stats: Stats = author_player.get_stats()
        player_xp: Expertise = author_player.get_expertise()

        # E(X) =
        # 0.55 * (2 + 1 + 1) / 3 +
        # 0.2 * (3 + 4 + 3) / 3 +
        # 0.15 * (4 + 5) / 2 +
        # 0.095 * (10 + 8 + 8 + 10) / 3 +
        # 0.0049 * (40 + 50 + 30) / 3 +
        # 0.0001 * 1 =
        # 3.41 every 30 seconds -> 409.2 an hour

        # Luck Effect
        #   1  -> E(X) = 3.45 every 30 seconds -> 414 an hour
        #   10 -> E(X) = 3.85 every 30 seconds -> 462 an hour
        #   20 -> E(X) = 4.29 every 30 seconds -> 514.8 an hour

        LUCK_MOD = 0.005 # Luck adjusts total bias by 0.5% per point
        player_luck: int = author_player.get_expertise().luck
        equipment_luck: int = author_player.get_equipment().get_total_buffs().lck_buff
        total_luck: int = player_luck + equipment_luck
        rand_val = random.choices(
            [0, 1, 2, 3, 4, 5], k=1,
            weights=[
                # Luck Effect:
                #   1  -> 54.5%, 20.125%, 15.125%, 9.625%, 0.5525%, 0.0735%
                #   10 -> 50%, 21.25%, 16.25%, 10.75%, 1.115%, 0.635%
                #   20 -> 45%, 22.5%, 17.5%, 12%, 1.74%, 1.26%
                0.55 - LUCK_MOD * total_luck,
                0.2 + 2 * (LUCK_MOD * total_luck) / 8,
                0.15 + 2 * (LUCK_MOD * total_luck) / 8,
                0.095 + 2 * (LUCK_MOD * total_luck) / 8,
                0.0049 + 1 * (LUCK_MOD * total_luck) / 8,
                0.0001 + 1 * (LUCK_MOD * total_luck) / 8
            ]
        )[0]

        # 55% chance of getting a Common non-fish reward
        if rand_val == 0:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.BasicBoots), 
                LOADED_ITEMS.get_new_item(ItemKey.ClumpOfLeaves), 
                LOADED_ITEMS.get_new_item(ItemKey.Conch)
            ]
            fishing_result = random.choice(items)
            player_stats.fish.common_items_caught += 1
        # 20% chance of getting a Common fish reward
        if rand_val == 1:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Minnow),
                LOADED_ITEMS.get_new_item(ItemKey.Roughy),
                LOADED_ITEMS.get_new_item(ItemKey.Shrimp)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 3
            player_stats.fish.common_fish_caught += 1
        # 15% chance of getting an Uncommon fish reward
        if rand_val == 2:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Oyster),
                LOADED_ITEMS.get_new_item(ItemKey.Pufferfish)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 5
            player_stats.fish.uncommon_fish_caught += 1
        # 9.5% chance of getting a Rare fish reward
        if rand_val == 3:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Squid),
                LOADED_ITEMS.get_new_item(ItemKey.Crab),
                LOADED_ITEMS.get_new_item(ItemKey.Lobster),
                LOADED_ITEMS.get_new_item(ItemKey.Shark)
            ]
            fishing_result = random.choice(items)
            xp_to_add = 8
            player_stats.fish.rare_fish_caught += 1
        # 0.49% chance of getting a Rare non-fish reward
        if rand_val == 4:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.Diamond),
                LOADED_ITEMS.get_new_item(ItemKey.AncientVase),
                LOADED_ITEMS.get_new_item(ItemKey.MysteriousScroll)
            ]
            fishing_result = random.choice(items)
            xp_class = ExpertiseClass.Merchant
            xp_to_add = 8
            player_stats.fish.rare_items_caught += 1
        # 0.01% chance of getting the Epic story reward
        if rand_val == 5:
            items = [LOADED_ITEMS.get_new_item(ItemKey.FishMaybe)]
            fishing_result = random.choice(items)

            story: OceanStory = self._get_story(context.guild.id, Story.Ocean)
            if story.first_to_find_maybe_fish_id == -1:
                story.first_to_find_maybe_fish_id = context.author.id

            xp_to_add = 13
            player_stats.fish.epic_fish_caught += 1
        
        author_player.get_inventory().add_item(fishing_result)
        player_xp.add_xp_to_class(xp_to_add, xp_class)

        description = "It's been added to your b!inventory."
        if xp_to_add > 0:
            description += f"\n\n*(+{xp_to_add} {xp_class} xp)*"

        embed = Embed(
            title=f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}!",
            description=description
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
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't play knucklebones.")
            return

        challenged_player: Player = self._get_player(context.guild.id, user.id)
        challenged_player_dueling: Dueling = challenged_player.get_dueling()
        if challenged_player_dueling.is_in_combat:
            await context.send(f"That person is in a duel and can't play knucklebones.")
            return

        if author_player.get_inventory().get_coins() < amount:
            await context.send(f"You don't have enough coins ({author_player.get_inventory().get_coins()}) to bet that much!")
            return
        if challenged_player.get_inventory().get_coins() < amount:
            await context.send(f"That person doesn't have enough coins ({challenged_player.get_inventory().get_coins()}) to bet that much!")
            return

        embed = Embed(
            title="Welcome to Knucklebones!",
            description=(
                "Players will take alternating turns rolling dice. They will then choose a column in which to place the die result.\n\n"
                "If the opponent has dice of the same value in that same column, those dice are removed from their board.\n\n"
                "Two of the same die in a single column double their value. Three of the same die triple their value.\n\n"
                "When one player fills their board with dice, the game is over. The player with the most points wins.\n\n"
                "The game will begin when the other player accepts the invitation to play."
            )
        )

        await context.send(embed=embed, view=Knucklebones(self._bot, self._database, context.guild.id, context.author, user, amount))

    @commands.command(name="mail", help="Send another player a gift")
    async def mail_handler(self, context: commands.Context, giftee: User=None):
        if giftee is None:
            await context.send("You need to @ a member to use b!mail")
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
        dueling: Dueling = player.get_dueling()
        if dueling.is_in_combat:
            await context.send(f"You're in a duel and can't send mail.")
            return

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

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit the market.")
            return

        embed = Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )
        await context.send(embed=embed, view=MarketView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="mailbox", help="Open mail you've received from others", aliases=["inbox"])
    async def mailbox_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your mailbox.")
            return
        
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

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit the wishing well.")
            return

        author_inv: Inventory = author_player.get_inventory()
        if author_inv.get_coins() == 0:
            await context.send(f"You don't have any coins.")
            return
        author_inv.remove_coins(1)
        
        player_stats: Stats = author_player.get_stats()
        story: UnderworldStory = self._get_story(context.guild.id, Story.Underworld)

        # E(X) = 0.995 * -1 + 0.0021 * 150 = -0.68 every 5 seconds -> -489.6 per hour
        # Luck Effect:
        #   1  -> E(X) = 0.994 * -1 + 0.0021 * 150 -> -488.88 per hour
        #   10 -> E(X) = 0.985 * -1 + 0.00585 * 150 -> -77.4 per hour
        #   20 -> E(X) = 0.975 * -1 + 0.0096 * 150 -> 334.8 per hour

        LUCK_MOD = 0.001 # Luck adjusts total bias by 0.1% per point
        author_luck: int = author_player.get_expertise().luck
        equipment_luck: int = author_player.get_equipment().get_total_buffs().lck_buff
        total_luck: int = author_luck + equipment_luck
        rand_val = random.choices(
            [0, 1, 2, 3], k=1,
            weights=[
                # Luck Effect:
                #   1  -> 99.4%, 0.33%, 0.2475%, 0.0225%
                #   10 -> 98.5%, 0.78%, 0.585%, 0.135%
                #   20 -> 97.5%, 1.28%, 0.96%, 0.26%
                0.9950 - LUCK_MOD * total_luck,
                0.0028 + 4 * (LUCK_MOD * total_luck) / 8,
                0.0021 + 3 * (LUCK_MOD * total_luck) / 8,
                0.0001 + 1 * (LUCK_MOD * total_luck) / 8
            ]
        )[0]

        # 99.5% base chance of getting nothing
        if rand_val == 0:
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and hits the bottom with a resounding clink."
            )
            await context.send(embed=embed)
        # 0.21% base chance of getting 150 coins
        if rand_val == 1:
            author_player.get_inventory().add_coins(150)
            player_stats.wishingwell.coins_received += 150
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and you feel a sense of duplication. One becoming many."
            )
            await context.send(embed=embed)
        # 0.28% base chance of getting a Legendary item
        if rand_val == 2:
            result: Item = story.get_wishing_well_item()

            expertise: Expertise = author_player.get_expertise()
            if result.get_key() == ItemKey.Diamond:
                expertise.add_xp_to_class(8, ExpertiseClass.Merchant)
            else:
                expertise.add_xp_to_class(34, ExpertiseClass.Merchant)

            mail: Mail = Mail("Wishing Well", result, 0, "A piece of the whole.", str(time.time()).split(".")[0], -1)
            author_player.get_mailbox().append(mail)

            player_stats.wishingwell.items_received += 1

            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below. Then, you close your eyes and are surrounded by a gust of wind. Something has arrived where things sent are brought."
            )
            await context.send(embed=embed)
        # 0.01% base chance of stirring something in the world
        if rand_val == 3:
            story_response: Embed = story.get_wishing_well_response(context.author.id, player_stats)
            player_stats.wishingwell.something_stirs += 1

            await context.send(embed=story_response)

        player_stats.wishingwell.coins_tossed += 1

    @commands.command(name="expertise", help="See your level progress and attributes", aliases=["me", "xp"])
    async def expertise_handler(self, context: commands.Context, user: User=None):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        xp_view = None
        if user is None:
            xp_view = ExpertiseView(self._bot, self._database, context.guild.id, context.author)
        else:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            xp_view = ExpertiseView(self._bot, self._database, context.guild.id, user)
        embed = xp_view.get_current_page_info()
        await context.send(embed=embed, view=xp_view)

    @commands.command(name="equipment", help="See your equipment and equip items", aliases=["equip"])
    async def equipment_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't change your equipment.")
            return

        equipment_view = EquipmentView(self._bot, self._database, context.guild.id, context.author)
        embed = equipment_view.get_initial_info()
        await context.send(embed=embed, view=equipment_view)

    @commands.command(name="duel", help="Challenge another player to a duel")
    async def duel_handler(self, context: commands.Context, users: List[User]=None):
        if users is None:
            await context.send("You need to @ a member to use b!duel.")
            return

        if context.author in users:
            await context.send("You can't challenge yourself to a duel.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't challenge a bot to a duel.")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't start another.")
            return

        challenged_players: List[Player] = [self._get_player(context.guild.id, user.id) for user in users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send(f"At least one of those players is already in a duel.")
            return

        pvp_duel = PlayerVsPlayerDuelView(self._bot, self._database, context.guild.id, context.author, users)

        await context.send(embed=pvp_duel.get_info_embed(), view=pvp_duel)

    @commands.command(name="glossary", help="Shows a list of adventure-related words and their definitions")
    async def glossary_handler(self, context: commands.Context):
        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        description = (
            "**Attributes:**\n\n"
            "Constitution: Affects max HP and increases the speed of any health regen\n"
            "Strength: Affects how much damage is dealt with weapons and weapon-based abilities\n"
            "Dexterity: Affects dodge chance and whether you go first when dueling\n"
            "Intelligence: Affects how much damage is done with mana-based abilities, max mana, and increases mana regen\n"
            "Luck: Increases your prowess in matters of chance and acts as a modifier for critical hit chance\n"
            "Memory: Adds additional ability slots\n\n"
            "**Status Effects:**\n\n"
            "Bleeding: Take x% max health as damage at the start of each turn\n"
            "Posioned: Take x% max health as damage at the start of each turn\n"
            "Echoing: Take a fixed amount of damage at the start of each turn\n\n"
            "Fortified: Gain additional Constitution\n"
            "Bolstered: Gain additional Strength\n"
            "Hastened: Gain additional Dexterity\n"
            "Insightful: Gain additional Intelligence\n"
            "Lucky: Gain additional Luck\n\n"
            "Frail: Constitution is reduced\n"
            "Weakened: Strength is reduced\n"
            "Slowed: Dexterity is reduced\n"
            "Enfeebled: Intelligence is reduced\n"
            "Unlucky: Luck is reduced\n\n"
            "Protected: +x% damage reduction (up to 75%)\n"
            "Vulnerable: +x% additional damage taken (up to 25%)\n\n"
            "Faltering: % chance to skip your turn\n"
            "Enraged: Gain additional attributes whenever you take damage\n"
            "Taunted: Forced to attack the caster\n"
            "Convinced: Can't attack the caster\n"
            "Generating: When hit, whoever applied this status gains coins\n"
            "Tarnished: Whenever you gain coins, damage is dealt relative to the amount gained\n"
            "Sanguinated: All abilities use HP instead of Mana\n\n"
            "**Misc:**\n\n"
            "Overleveled: Armor and weapons that have a level requirement higher than your level are 15% less effective per level missing"
        )

        embed = Embed(title="Glossary", description=description)
        await context.send(embed=embed)


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
