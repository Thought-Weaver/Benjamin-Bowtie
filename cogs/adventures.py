from __future__ import annotations

import datetime
import jsonpickle
import os
import random
import shutil
import time

from discord import User
from discord.embeds import Embed
from discord.ext import commands, tasks

from bot import BenjaminBowtieBot
from features.companions.companion import BlueFlitterwingButterflyCompanion, ShadowfootRaccoonCompanion, TidewaterCrabCompanion
from features.companions.player_companions import PlayerCompanionsView
from features.settings import SettingsView
from features.stories.dream.dream import DreamStory
from features.views.dueling_view import CompanionBattleView, GroupPlayerVsPlayerDuelView, PlayerVsPlayerOrNPCDuelView
from features.equipment import EquipmentView
from features.expertise import ExpertiseClass, ExpertiseView
from features.house.alchemy import AlchemyChamberView
from features.house.garden import GardenView
from features.house.kitchen import KitchenView
from features.house.storage import StorageView
from features.house.study import StudyView
from features.house.workshop import WorkshopView
from features.house.house import HouseView
from features.inventory import InventoryView
from features.mail import Mail, MailView, MailboxView
from features.market import MarketView
from features.npcs.abarra import Blacksmith
from features.npcs.copperbroad import Chef
from features.npcs.galos import Galos
from features.npcs.mrbones import Difficulty, MrBones
from features.npcs.npc import NPCRoles
from features.npcs.tiatha import Druid
from features.npcs.viktor import RandomItemMerchant
from features.npcs.yenna import Yenna
from features.player import Player
from features.stats import StatCategory, StatView
from features.shared.enums import ClassTag, CompanionKey, ForestSection, OceanSection, UnderworldSection
from features.shared.item import Item, LOADED_ITEMS, ItemKey, Rarity
from features.stories.forest.forest import ForestDungeonEntranceView, ForestStory
from features.stories.ocean.ocean import OceanDungeonEntranceView, OceanStory
from features.stories.story import Story
from features.stories.underworld.underworld import UnderworldDungeonEntranceView, UnderworldStory
from features.trainers import TrainerView
from games.knucklebones import Knucklebones

from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING:
    from features.dueling import Dueling
    from features.expertise import Expertise
    from features.inventory import Inventory
    from features.npcs.npc import NPC
    from features.shared.ability import Ability
    from features.stats import Stats

class Adventures(commands.Cog):
    def __init__(self, bot: BenjaminBowtieBot):
        self._bot = bot
        
        file_data = open("./adventuresdb.json", "r").read()
        self._database: dict = jsonpickle.decode(file_data) if os.path.isfile("./adventuresdb.json") else {}

        self._database_npc_and_story_setup()
        self.tick.start()

    def _database_npc_and_story_setup(self, specific_guild_id_str: str | None=None):
        def create_stories_and_npcs(guild_id_str: str):
            if self._database[guild_id_str].get("stories") is None:
                self._database[guild_id_str]["stories"] = {}
            if self._database[guild_id_str]["stories"].get(Story.Forest) is None:
                self._database[guild_id_str]["stories"][Story.Forest] = ForestStory()
            if self._database[guild_id_str]["stories"].get(Story.Ocean) is None:
                self._database[guild_id_str]["stories"][Story.Ocean] = OceanStory()
            if self._database[guild_id_str]["stories"].get(Story.Underworld) is None:
                self._database[guild_id_str]["stories"][Story.Underworld] = UnderworldStory()
            if self._database[guild_id_str]["stories"].get(Story.Dream) is None:
                self._database[guild_id_str]["stories"][Story.Dream] = DreamStory()

            if self._database[guild_id_str].get("npcs") is None:
                self._database[guild_id_str]["npcs"] = {}
            if self._database[guild_id_str]["npcs"].get(NPCRoles.FortuneTeller) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.FortuneTeller] = Yenna()
            if self._database[guild_id_str]["npcs"].get(NPCRoles.Blacksmith) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.Blacksmith] = Blacksmith()
            if self._database[guild_id_str]["npcs"].get(NPCRoles.KnucklebonesPatron) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.KnucklebonesPatron] = MrBones()
            if self._database[guild_id_str]["npcs"].get(NPCRoles.Chef) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.Chef] = Chef()
            if self._database[guild_id_str]["npcs"].get(NPCRoles.RandomItemMerchant) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.RandomItemMerchant] = RandomItemMerchant()
            if self._database[guild_id_str]["npcs"].get(NPCRoles.CompanionMerchant) is None:
                self._database[guild_id_str]["npcs"][NPCRoles.CompanionMerchant] = Druid()
        
        def validate_user_ids(guild_id_str: str):
            if self._database[guild_id_str].get("members") is None:
                self._database[guild_id_str]["members"] = {}
            for user_id in self._database[guild_id_str]["members"].keys():
                player: Player = self._database[guild_id_str]["members"][user_id]
                if player.get_id() is None or player.get_id() == "":
                    player.set_id(str(user_id))

        if specific_guild_id_str is not None:
            create_stories_and_npcs(specific_guild_id_str)
            validate_user_ids(specific_guild_id_str)
        else:
            for guild_id_str in self._database.keys():
                create_stories_and_npcs(guild_id_str)
                validate_user_ids(guild_id_str)

    def _check_member_and_guild_existence(self, guild_id: int, user_id: int):
        guild_id_str: str = str(guild_id)
        user_id_str: str = str(user_id)

        if self._database.get(guild_id_str) is None:
            self._database[guild_id_str] = {}
            self._database[guild_id_str]["members"] = {}
            self._database_npc_and_story_setup(guild_id_str)
        
        if self._database[guild_id_str]["members"].get(user_id_str) is None:
            self._database[guild_id_str]["members"][user_id_str] = Player(user_id_str)

    def _get_player(self, guild_id: int, user_id: int) -> Player:
        return self._database[str(guild_id)]["members"][str(user_id)]

    def _get_story(self, guild_id: int, story_key: Story):
        return self._database[str(guild_id)]["stories"][story_key]

    def _map_name_to_new_npc(self, users: commands.Greedy[User | str]):
        mapped: List[User | NPC] = []
        for user in users:
            if isinstance(user, str):
                if user.lower() == "yenna":
                    mapped.append(Yenna())
                elif user.lower() == "mrbones":
                    mapped.append(MrBones())
                elif user.lower() == "abarra":
                    mapped.append(Blacksmith())
                elif user.lower() == "viktor":
                    mapped.append(RandomItemMerchant())
                elif user.lower() == "copperbroad":
                    mapped.append(Chef())
                elif user.lower() == "galos":
                    mapped.append(Galos())
            else:
                mapped.append(user)
        return mapped

    @tasks.loop(time=[datetime.time(hour=i) for i in range(24)])
    async def tick(self):
        for guild_id in self._database.keys():
            guild_id_str = str(guild_id)
            for user_id in self._database[guild_id_str].get("members", {}).keys():
                player: Player = self._get_player(guild_id, user_id)
                await player.tick(self._bot)
                
                if not player.get_dueling().is_in_combat:
                    player.get_dueling().decrement_all_ability_cds()
                    player.get_dueling().decrement_statuses_time_remaining()

            for npc_id in self._database[guild_id_str].get("npcs", {}).keys():
                if npc_id == NPCRoles.RandomItemMerchant:
                    npc: RandomItemMerchant = self._database[guild_id_str]["npcs"][npc_id]
                    npc.tick()
 
        await self.save_database()

    async def save_database(self):
        if os.path.isfile("./adventuresdb.json"):
            shutil.copy("adventuresdb.json", "adventuresdbbackup.json")
        
        frozen = jsonpickle.encode(self._database, make_refs=False)
        with open("adventuresdb.json", "w") as file:
            file.write(frozen)
    
    @commands.is_owner()
    @commands.command(name="saveadventures", help="Saves the adventures database", hidden=True)
    async def save_adventures_handler(self, context: commands.Context):
        await self.save_database()
        await context.send("The adventures database has been saved!")

    @commands.is_owner()
    @commands.command(name="endduel", help="Ends combat for specific members", hidden=True)
    async def end_duel_handler(self, context: commands.Context, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        if users is None:
            await context.send("You need to @ a member to use b!endduel.")
            return

        players: List[Player] = []
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            players.append(self._get_player(context.guild.id, user.id))

        for player in players:
            player_dueling = player.get_dueling()
            player_expertise = player.get_expertise()
            
            if player_dueling.is_in_combat:
                player_dueling.status_effects = []
                player_dueling.is_in_combat = False
                player_dueling.reset_ability_cds()

                player_expertise.update_stats(player.get_combined_attributes())
                player_expertise.hp = player_expertise.max_hp
                player_expertise.mana = player_expertise.max_mana

                companions = player.get_companions()
                if companions.current_companion is not None:
                    companion_ability = companions.companions[companions.current_companion].get_dueling_ability(effect_category=None)
                    
                    if companion_ability is not None:
                        for ability in player.get_dueling().abilities:
                            if ability.__class__ == companion_ability.__class__:
                                player.get_dueling().abilities.remove(ability)
                                break
                
                player.get_stats().dueling.duels_fought += 1
                player.get_stats().dueling.duels_tied += 1
        await context.send("The duel has been ended for those players.")

    @commands.is_owner()
    @commands.command(name="enddungeonrun", help="Ends dungeon run for specific members", hidden=True)
    async def end_dungeon_run_handler(self, context: commands.Context, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        if users is None:
            await context.send("You need to @ a member to use b!enddungeonrun.")
            return

        players: List[Player] = []
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            players.append(self._get_player(context.guild.id, user.id))

        if any(player.get_dueling().is_in_combat for player in players):
            for player in players:
                player_dueling = player.get_dueling()
                player_expertise = player.get_expertise()
                
                if player_dueling.is_in_combat:
                    player_dueling.status_effects = []
                    player_dueling.is_in_combat = False
                    player_dueling.reset_ability_cds()

                    player_expertise.update_stats(player.get_combined_attributes())
                    player_expertise.hp = player_expertise.max_hp
                    player_expertise.mana = player_expertise.max_mana

                    companions = player.get_companions()
                    if companions.current_companion is not None:
                        companion_ability = companions.companions[companions.current_companion].get_dueling_ability(effect_category=None)
                        
                        if isinstance(companion_ability, Ability):
                            try:
                                player.get_dueling().abilities.remove(companion_ability)
                            except:
                                pass
                    
                    player.get_stats().dueling.duels_fought += 1
                    player.get_stats().dueling.duels_tied += 1

        for player in players:
            player.get_dungeon_run().in_dungeon_run = False
            player.get_dungeon_run().in_rest_area = False

        await context.send("The dungeon run has been ended for those players.")

    @commands.is_owner()
    @commands.command(name="giveitem", help="Gives an item to a player", hidden=True)
    async def give_item_handler(self, context: commands.Context, user: User, item_key: ItemKey):
        assert(context.guild is not None)

        try:
            item: Item = LOADED_ITEMS.get_new_item(item_key)
            player: Player = self._get_player(context.guild.id, user.id)
            player.get_inventory().add_item(item)

            await context.send(f"{item.get_full_name()} has been added to {user.display_name}'s inventory!")
        except Exception as e:
            await context.send(f"Failed to add that item to the {user.display_name}'s inventory! Error: {e}")

    @commands.command(name="fish", help="Begins a fishing minigame to catch fish and mysterious items", aliases=["ghoti"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fish_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        rand_val = random.random()
        
        fishing_result: Item | None = None
        xp_to_add: int = 0
        xp_class: ExpertiseClass = ExpertiseClass.Fisher

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't fish.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't fish.")
            return

        player_stats: Stats = author_player.get_stats()
        player_xp: Expertise = author_player.get_expertise()

        # E(X) =
        # 0.55 * (2 + 1 + 1) / 3 +
        # 0.2 * (3 + 4 + 3) / 3 +
        # 0.15 * (4 + 5) / 2 +
        # 0.095 * (10 + 8 + 8 + 10) / 3 +
        # 0.0049 * (40 + 30) / 2 +
        # 0.0001 * 1 =
        # 3.41 every 30 seconds -> 409.2 an hour

        # TODO: Redo earnings analysis with luck later

        LUCK_MOD = 0.005 # Luck adjusts total bias by 0.5% per point
        total_luck: int = min(author_player.get_combined_attributes().luck, 100)
        rand_val = random.choices(
            [0, 1, 2, 3, 4, 5], k=1,
            weights=[
                # Luck Effect:
                #   1  -> 54.5%, 20.1875%, 15.125%, 9.5938%, 0.5525%, 0.04125%
                #   10 -> 50%, 21.875%, 16.25%, 10.4375%, 1.115%, 0.3225%
                #   20 -> 45%, 23.75%, 17.5%, 11.375%, 1.74%, 0.635%
                #   50 -> 30%, 29.375%, 21.25%, 14.1875%, 3.615%, 1.5725%
                0.55 - LUCK_MOD * total_luck,
                0.2 + 6 * (LUCK_MOD * total_luck) / 16,
                0.15 + 4 * (LUCK_MOD * total_luck) / 16,
                0.095 + 3 * (LUCK_MOD * total_luck) / 16,
                0.0049 + 2 * (LUCK_MOD * total_luck) / 16,
                0.0001 + 1 * (LUCK_MOD * total_luck) / 16
            ]
        )[0]

        # 55% chance of getting a Common non-fish reward
        if rand_val == 0:
            items = [
                LOADED_ITEMS.get_new_item(ItemKey.TatteredBoot), 
                LOADED_ITEMS.get_new_item(ItemKey.ClumpOfLeaves), 
                LOADED_ITEMS.get_new_item(ItemKey.Conch),
                LOADED_ITEMS.get_new_item(ItemKey.Stranglekelp)
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
        
        companion_result_str: str = ""
        if fishing_result is not None and fishing_result.get_key() == ItemKey.Crab and random.random() < 0.1 + (LUCK_MOD * total_luck) / 10:
            companions = author_player.get_companions()
            if CompanionKey.TidewaterCrab not in companions.companions.keys():
                companions.companions[CompanionKey.TidewaterCrab] = TidewaterCrabCompanion()
                companions.companions[CompanionKey.TidewaterCrab].set_id(author_player.get_id())
                companion_result_str += "\n\nThis crab seems particularly friendly towards you! It's been added as a companion in b!companions."

                author_player.get_stats().companions.companions_found += 1

        author_player.get_inventory().add_item(fishing_result)
        final_xp = player_xp.add_xp_to_class(xp_to_add, xp_class, author_player.get_equipment())

        description = "It's been added to your b!inventory."
        if final_xp > 0:
            description += f"\n\n*(+{final_xp} {xp_class} xp)*"
        description += companion_result_str

        embed = Embed(
            title=f"You caught {fishing_result.get_full_name()} worth {fishing_result.get_value_str()}!",
            description=description
        )
        await context.send(embed=embed)

    @commands.command(name="knucklebones", help="Face another player in a game of knucklebones")
    async def knucklebones_handler(self, context: commands.Context, user: Union[User, str, None]=None, amount: int=0):
        assert(context.guild is not None)

        if user is None:
            await context.send("You need to @ a member to use b!knucklebones.")
            return

        if user == context.author:
            await context.send("You can't challenge yourself to a game of knucklebones.")
            return
            
        if isinstance(user, User) and user.bot:
            await context.send("You can't challenge a bot to knucklebones (but Benjamin Bowtie might learn how to play one day!)")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        if isinstance(user, User):
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

        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't play knucklebones.")
            return

        challenged_player: Player | NPC = MrBones()
        challenged_player_name = "Someone"
        use_luck = True
        description = (
            "Players will take alternating turns rolling dice. They will then choose a column in which to place the die result.\n\n"
            "If the opponent has dice of the same value in that same column, those dice are removed from their board.\n\n"
            "Two of the same die in a single column double their value. Three of the same die triple their value.\n\n"
            "When one player fills their board with dice, the game is over. The player with the most points wins."
        )
        # By default, this is the author to account for when they play against a bot
        accepting_id: int = context.author.id
        other_id: int = -1
        difficulty: Difficulty | None = None
        
        if isinstance(user, User):
            challenged_player = self._get_player(context.guild.id, user.id)
            challenged_player_name = user.display_name
            challenged_player_dueling: Dueling = challenged_player.get_dueling()
            if challenged_player_dueling.is_in_combat:
                await context.send(f"That person is in a duel and can't play knucklebones.")
                return

            if challenged_player.get_inventory().get_coins() < amount:
                await context.send(f"That person doesn't have enough coins ({challenged_player.get_inventory().get_coins()}) to bet that much!")
                return

            description += "\n\nThe game will begin when the other player accepts the invitation to play."
            accepting_id = user.id
            other_id = context.author.id

        if isinstance(user, str):
            user_lower = user.lower()
            if isinstance(user, str) and user_lower != "mrbones" and user_lower != "easy" and user_lower != "medium" and user_lower != "hard":
                await context.send("You have to choose Easy, Medium, or Hard.")
                return
            
            if amount != 0:
                await context.send("You can't bet coins when playing against an NPC.")
                return

            # This is being done to give players who want to face a bot a chance to re-read the rules
            description += "\n\nThe game will begin when you confirm your intent to play."

            if user_lower == "mrbones":
                challenged_player_name = "Mr. Bones"
                difficulty = Difficulty.MrBones
                description += (
                    "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n*You enter the back room of the Crown & Anchor Tavern and the light fades to a dim glow. There, waiting in the darkness, is a figure dressed richly in a vest and suit that gleam almost tyrian. Winding shapes that branch and twist up the undershirt in black seem to be moving of their own accord.*\n\n"
                    "*In a raspy voice, it utters, \"I... am... Mr... Bones...\" and a hand that looks startlingly skeletal beckons you to play. You could swear there's a smile hidden in those shadows.*"
                )
            elif user_lower == "easy":
                challenged_player_name = "Tavern Tim (Easy)"
                difficulty = Difficulty.Easy
                use_luck = False
                description += (
                    "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n*The Crown & Anchor Tavern is bustling this evening and, as always, good ol' \"Tavern\" Tim sits at the bar playing Knucklebones with his friends. You suspect, based on his reputation, that he's losing, but he certainly doesn't seem to mind.*\n\n"
                    "\"Awright, how urr ye? Wanna speil a gam or twa haha!\""
                )
            elif user_lower == "medium":
                challenged_player_name = "Alleus (Medium)"
                difficulty = Difficulty.Medium
                use_luck = False
                description += (
                    "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n*It's an average night in the tavern, with people drinking, eating, and celebrating the end of a hard day's labors. Talking with Quinan at a table is her father, Alleus, who you know to be a retired spice trader renowned for travelling the world.*\n\n"
                    "\"A challenger approaches! And I'm never one to turn down a good game. Let's play.\""
                )
            elif user_lower == "hard":
                challenged_player_name = "Yenna (Hard)"
                difficulty = Difficulty.Hard
                use_luck = False
                description += (
                    "\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n*It's a quieter night than most in the tavern this evening. Waiting at a table in the corner of the bar, you can see Yenna. She doesn't have a drink, but is enjoying a nice meal -- something special based on the look of it prepared by Quinan. She makes eye contact with you as you enter and holds up a set of dice made of bone.*"
                )

        if author_player.get_inventory().get_coins() < amount:
            await context.send(f"You don't have enough coins ({author_player.get_inventory().get_coins()}) to bet that much!")
            return

        embed = Embed(title="Welcome to Knucklebones!", description=description)

        await context.send(embed=embed, view=Knucklebones(self._bot, self._database, context.guild.id, author_player, challenged_player, context.author.display_name, challenged_player_name, accepting_id, other_id, amount, use_luck, difficulty))

    @commands.command(name="mail", help="Send another player a gift")
    async def mail_handler(self, context: commands.Context, giftee: User=None):
        assert(context.guild is not None)

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

        if player.get_dungeon_run().in_dungeon_run and not player.get_dungeon_run().in_rest_area:
            await context.send(f"You're on an adventure and haven't reached a rest area, so you can't send mail.")
            return

        coins_str = player.get_inventory().get_coins_str()
        embed = Embed(
            title=f"{context.author.display_name}'s Inventory",
            description=f"You have {coins_str}.\n\nChoose an item to mail to {giftee.display_name}!"
        )
        await context.send(embed=embed, view=MailView(self._bot, self._database, giftee, context))

    @commands.command(name="inventory", help="Check your inventory", aliases=["inv"])
    async def inventory_handler(self, context: commands.Context):
        assert(context.guild is not None)

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
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit the market.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit the market.")
            return

        embed = Embed(
            title="Welcome to the Market!",
            description="Select an action below to get started."
        )
        await context.send(embed=embed, view=MarketView(self._bot, self._database, context.guild.id, context.author, context))

    @commands.command(name="mailbox", help="Open mail you've received from others", aliases=["inbox"], hidden=True)
    async def mailbox_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your mailbox.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run and not author_player.get_dungeon_run().in_rest_area:
            await context.send(f"You're on an adventure and haven't reached a rest area, so you can't visit your mailbox.")
            return
        
        embed = Embed(
            title=f"{context.author.display_name}'s Mailbox",
            description=f"Navigate through your mail using the Prev and Next buttons."
        )
        await context.send(embed=embed, view=MailboxView(self._bot, self._database, context.guild.id, context.author))

    @commands.command(name="stats", help="See your stats")
    async def stats_handler(self, context: commands.Context, user: User | None=None, stat_category_name:StatCategory | None=None):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        display_user = context.author
        if user is not None:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            display_user = user

        stat_view = StatView(self._bot, self._database, context.guild.id, context.author, display_user, stat_category_name)
        embed = stat_view.get_current_page_info()
        await context.send(embed=embed, view=stat_view)

    @commands.command(name="wishingwell", help="Toss a coin into the wishing well", aliases=["ww"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wishing_well_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit the wishing well.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit the wishing well.")
            return

        author_inv: Inventory = author_player.get_inventory()
        if author_inv.get_coins() == 0:
            await context.send(f"You don't have any coins.")
            return
        author_inv.remove_coins(1)
        
        player_stats: Stats = author_player.get_stats()
        story: UnderworldStory = self._get_story(context.guild.id, Story.Underworld)

        # TODO: Need to redo this analysis with all the new gemstone possibilities
        # E(X) = 0.995 * -1 + 0.0021 * 100 = -0.68 every 5 seconds -> -489.6 per hour
        # Luck Effect:
        #   1  -> E(X) = 0.994 * -1 + 0.0021 * 125 -> -527 per hour
        #   10 -> E(X) = 0.985 * -1 + 0.00585 * 125 -> -183 per hour
        #   20 -> E(X) = 0.975 * -1 + 0.0096 * 125 -> 162 per hour
        #   50 -> E(X) = 0.945 * -1 + 0.0115 * 125 -> 355 per hour

        LUCK_MOD = 0.001 # Luck adjusts total bias by 0.1% per point
        total_luck: int = min(author_player.get_combined_attributes().luck, 100)
        rand_val = random.choices(
            [0, 1, 2, 3], k=1,
            weights=[
                # Luck Effect:
                #   1  -> 99.4%, 0.33%, 0.2475%, 0.0225%
                #   10 -> 98.5%, 0.78%, 0.585%, 0.135%
                #   20 -> 97.5%, 1.28%, 0.96%, 0.26%
                #   50 -> 94.5%, 2.78%, 1.15%, 0.32%
                0.9950 - LUCK_MOD * total_luck,
                0.0028 + 4 * (LUCK_MOD * total_luck) / 8,
                0.0021 + 3 * (LUCK_MOD * total_luck) / 8,
                0.0001 + 1 * (LUCK_MOD * total_luck) / 8
            ]
        )[0]

        # 99.5% base chance of getting nothing
        if rand_val == 0:
            companion_result_str: str = ""
            if random.random() < 0.004 + (LUCK_MOD * total_luck) / 10:
                companions = author_player.get_companions()
                if CompanionKey.ShadowfootRaccoon not in companions.companions.keys():
                    companions.companions[CompanionKey.ShadowfootRaccoon] = ShadowfootRaccoonCompanion()
                    companions.companions[CompanionKey.ShadowfootRaccoon].set_id(author_player.get_id())
                    companion_result_str += "\n\nBut just a moment later, there's a sound of shuffling and metal hitting metal, followed by a distinct scurrying and scrabbling up a cobblestone wall -- as out pops the head of a raccoon clutching your coin! Spotting you, it freezes, but seems to recognize that you might be the source of the money which has so often been tossed into the depths of the well. Curious, it approaches you and seems to want to follow! A new companion has been added to b!companions."

                    author_player.get_stats().companions.companions_found += 1

            embed = Embed(
                title="You toss the coin in...",
                description=f"It plummets into the darkness below and hits the bottom with a resounding clink.{companion_result_str}"
            )

            await context.send(embed=embed)
        # 0.21% base chance of getting 150 coins
        if rand_val == 1:
            author_player.get_inventory().add_coins(125)
            player_stats.wishingwell.coins_received += 125
            embed = Embed(
                title="You toss the coin in...",
                description="It plummets into the darkness below and you feel a sense of duplication. One becoming many."
            )
            await context.send(embed=embed)
        # 0.28% base chance of getting a gemstone or Artifact gear
        if rand_val == 2:
            result: Item = story.get_wishing_well_item()

            xp_to_add: int = 0
            expertise: Expertise = author_player.get_expertise()
            if ClassTag.Valuable.Gemstone in result.get_class_tags():
                if result.get_rarity() == Rarity.Common:
                    xp_to_add = 3
                if result.get_rarity() == Rarity.Uncommon:
                    xp_to_add = 5
                if result.get_rarity() == Rarity.Rare:
                    xp_to_add = 8
                if result.get_rarity() == Rarity.Epic:
                    xp_to_add = 13
                if result.get_rarity() == Rarity.Legendary:
                    xp_to_add = 21
                xp_to_add = expertise.add_xp_to_class(xp_to_add, ExpertiseClass.Merchant, author_player.get_equipment())
            else:
                xp_to_add = 34
                xp_to_add = expertise.add_xp_to_class(xp_to_add, ExpertiseClass.Merchant, author_player.get_equipment())

            xp_str: str = ""
            if xp_to_add > 0:
                xp_str += f"\n\n*(+{xp_to_add} {ExpertiseClass.Merchant} xp)*"

            mail: Mail = Mail("Wishing Well", result, 0, "A piece of the whole.", str(time.time()).split(".")[0], -1)
            author_player.get_mailbox().append(mail)

            player_stats.wishingwell.items_received += 1

            embed = Embed(
                title="You toss the coin in...",
                description=f"It plummets into the darkness below. Then, you close your eyes and are surrounded by a gust of wind. Something has arrived where things sent are brought.{xp_str}"
            )
            await context.send(embed=embed)
        # 0.01% base chance of stirring something in the world
        if rand_val == 3:
            story_response: Embed = story.get_wishing_well_response(context.author.id, player_stats)
            player_stats.wishingwell.something_stirs += 1

            await context.send(embed=story_response)

        player_stats.wishingwell.coins_tossed += 1

    @commands.command(name="expertise", help="See your level progress and attributes", aliases=["me", "xp"])
    async def expertise_handler(self, context: commands.Context, user: User | None=None):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        display_user = context.author
        if user is not None:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            display_user = user

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()

        xp_view = ExpertiseView(self._bot, self._database, context.guild.id, display_user, not author_dueling.is_in_combat and display_user == context.author)
        embed = xp_view.get_current_page_info()
        await context.send(embed=embed, view=xp_view)

    @commands.command(name="equipment", help="See your equipment and equip items", aliases=["equip"])
    async def equipment_handler(self, context: commands.Context, user: User | None=None):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        display_user = context.author
        if user is not None:
            self._check_member_and_guild_existence(context.guild.id, user.id)
            display_user = user

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()

        if author_player.get_dungeon_run().in_dungeon_run and not author_player.get_dungeon_run().in_rest_area:
            await context.send(f"You're on an adventure and haven't reached a rest area where you can change your equipment.")
            return

        equipment_view = EquipmentView(self._bot, self._database, context.guild.id, display_user, not author_dueling.is_in_combat and display_user == context.author)
        embed = equipment_view.get_initial_info()
        await context.send(embed=embed, view=equipment_view)

    @commands.command(name="duel", help="Challenge another player or NPC to a duel")
    async def duel_handler(self, context: commands.Context, users: commands.Greedy[User | str]=None):
        assert(context.guild is not None)

        if users is None:
            await context.send("You need to @ a member to use b!duel.")
            return

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times in a single duel.")
            return

        if context.author in users:
            await context.send("You can't challenge yourself to a duel.")
            return
            
        if any((isinstance(user, User) and user.bot) for user in users):
            await context.send("You can't challenge a bot to a duel.")
            return

        if len(users) != len(set(users)):
            await context.send("You can't challenge a player more than once in a single duel.")
            return

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            if isinstance(user, User):
                self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send("You're in a duel and can't start another.")
            return

        # Rather than using the existing NPCs (since multiple duels can happen at once), a player-started duel should
        # use a new copy of the NPC.
        mapped_users = self._map_name_to_new_npc(users)

        if len(mapped_users) == 0:
            await context.send("That NPC name wasn't valid.")
            return

        challenged_players: List[Player | NPC] = [(self._get_player(context.guild.id, user.id) if isinstance(user, User) else user) for user in mapped_users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send("At least one of those players is already in a duel.")
            return
        
        if any(isinstance(player, Player) and player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure and can't enter a duel.")
            return

        if any(player.get_expertise().hp != player.get_expertise().max_hp for player in challenged_players) or author_player.get_expertise().hp != author_player.get_expertise().max_hp:
            await context.send("At least one of those players isn't at full health.")
            return

        pvp_duel = PlayerVsPlayerOrNPCDuelView(self._bot, self._database, context.guild.id, context.author, mapped_users)

        await context.send(embed=pvp_duel.get_info_embed(), view=pvp_duel)

    @commands.command(name="glossary", help="Shows a list of adventure-related words and their definitions")
    async def glossary_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        description = (
            "__Attributes:__\n\n"
            "**Constitution:** Affects max HP\n"
            "**Strength:** Affects how much damage is dealt with weapons and weapon-based abilities\n"
            "**Dexterity:** Affects dodge chance and whether you go first when dueling\n"
            "**Intelligence:** Affects how much damage is done with mana-based abilities and your max mana\n"
            "**Luck:** Increases your prowess in matters of chance and acts as a modifier for critical hit chance\n"
            "**Memory:** Adds additional ability slots, one per point of memory\n\n"
            "__Status Effects:__\n\n"
            "**Bleeding:** Take x% max health as damage at the start of each turn\n"
            "**Poisoned:** Take x% max health as damage at the start of each turn\n"
            "**Echoing:** Take a fixed amount of damage at the start of each turn\n\n"
            "**Fortified:** Gain additional Constitution\n"
            "**Bolstered:** Gain additional Strength\n"
            "**Hastened:** Gain additional Dexterity\n"
            "**Insightful:** Gain additional Intelligence\n"
            "**Lucky:** Gain additional Luck\n"
            "**Retentive:** Gain additional Memory\n\n"
            "**Frail:** Constitution is reduced\n"
            "**Weakened:** Strength is reduced\n"
            "**Slowed:** Dexterity is reduced\n"
            "**Drained:** Intelligence is reduced\n"
            "**Unlucky:** Luck is reduced\n"
            "**Forgetful:** Memory is reduced\n\n"
            "**Protected:** +x% damage reduction (up to 75%)\n"
            "**Vulnerable:** +x% additional damage taken (up to 50%)\n"
            "**Empowered:** Deal x% additional damage\n"
            "**Diminished:** Deal x% less damage\n\n"
            "**Faltering:** x% chance to skip your turn\n"
            "**Enraged:** Gain additional attributes whenever you take damage\n"
            "**Taunted:** Forced to attack the caster\n"
            "**Convinced:** Can't attack the caster\n"
            "**Generating:** Whenever you attack, generate coins\n"
            "**Tarnished:** Whenever you gain coins, damage is dealt relative to the amount gained\n"
            "**Sanguinated:** All abilities use HP instead of Mana\n\n"
            "**Eureka:** Potions used are more powerful\n"
            "**Absorbing:** Poison damage heals\n"
            "**Regenerating:** Restore x% max health at the start of each turn\n"
            "**Reforming:** Restore x% max armor at the start of each turn\n"
            "**Acervophilic:** You can only use items this turn\n\n"
            "**Charmed:** Your enemies are your allies and vice versa; if a player skips their turn, they take 50% of their max health as damage\n"
            "**Atrophied:** You can't attack\n"
            "**Sleeping:** Your turn will be skipped (this status is removed upon taking damage)\n"
            "**Decaying:** Healing effects are x% less effective\n"
            "**Undying:** You can't be reduced below 1 HP\n"
            "**Enfeebled:** You can't use abilities\n"
            "**Reflecting:** You reflect x% damage back to the attacker when damaged\n"
            "**Patient:** You gain +x damage on your next attack, which also consumes the buff\n"
            "**Reverberating:** Using the same ability that caused this status on the target deals x% more damage\n"
            "**Confused:** Your health, mana, and armor are hidden\n\n"
            "__General:__\n\n"
            "**HP:** Your health points; when these reach 0, you die\n"
            "**Mana:** A resource used for casting certain abilities during duels\n"
            "**Armor:** Items with Armor provide a temporary buffer in combat before taking damage to your health\n"
            "**Overleveled:** Armor and weapons that have a level requirement higher than your level are 15% less effective per level difference\n"
            "**Critical Hit:** A critical hit (crit) randomly occurs based on your Luck and deals 150% weapon or ability damage\n"
            "**Cooldown:** A cooldown (CD) is how many turns until you can use the ability again during a duel"
        )

        embed = Embed(title="Glossary", description=description)
        await context.send(embed=embed)

    @commands.command(name="train", help="Visit trainers to acquire new abilities and equip them", aliases=["abilities"])
    async def train_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit the trainers or change your abilities.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run and not author_player.get_dungeon_run().in_rest_area:
            await context.send(f"You're on an adventure and aren't at a rest area where you can change your abilities.")
            return

        equipment_view = TrainerView(self._bot, self._database, context.guild.id, context.author, change_abilities_only=author_player.get_dungeon_run().in_rest_area)
        embed = equipment_view.get_initial_info()
        await context.send(embed=embed, view=equipment_view)

    @commands.command(name="groupduel", help="Gather players to choose teams for a duel")
    async def group_duel_handler(self, context: commands.Context, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        if users is None:
            await context.send("You need to @ a member to use b!groupduel.")
            return

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times in a single duel.")
            return

        if context.author in users:
            await context.send("You can't challenge yourself to a duel.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't challenge a bot to a duel.")
            return
        
        if len(users) != len(set(users)):
            await context.send("You can't challenge a player more than once in a single duel.")
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
        
        if any(player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure and can't enter a duel.")
            return

        if any(player.get_expertise().hp != player.get_expertise().max_hp for player in challenged_players) or author_player.get_expertise().hp != author_player.get_expertise().max_hp:
            await context.send("At least one of those players isn't at full health.")
            return

        pvp_duel = GroupPlayerVsPlayerDuelView(self._bot, self._database, context.guild.id, [context.author, *users])

        await context.send(embed=pvp_duel.get_info_embed(), view=pvp_duel)

    @commands.command(name="tutorial", help="Explains the basics of how to get started!")
    async def tutorial_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        description = (
            "Benjamin Bowtie is a collaborative text-based RPG game bot that you can play alongside your friends in any server. You are a hopeful adventurer in a small village, performing various tasks to make yourself some money and explore what secrets the village has to offer. Beware, for some things are better left unknown...\n\n"
            "You can send the bot commands which will do various different things by sending b![some command here]. Here are some and how they tie together:\n\n"
            "**Need Coins?**\n\n To acquire coins (the in-game currency), you can b!fish to get a random fish/item that gets added to your b!inventory. You can visit the b!market to sell the fish/items and make coins -- or keep them to craft and cook other items later!\n\n"
            "When you have enough coins, you can buy a b!house and begin upgrading it to add rooms for crafting, potion-making, enchanting, gardening, and more!\n\n"
            "**Level Up!**\n\nAs you b!fish and participate in other activities, you'll earn XP for the game's different classes (Fisher, Merchant, Guardian, and Alchemist) depending on the nature of the activity. XP contributes to your level in each of these classes. You can check your progress using b!xp.\n\n"
            "Whenever you level up, you gain attribute points. These can be spent on Constitution, Strength, Intelligence, Dexterity, Luck, or Memory. For more on what each attribute does, check out b!glossary. In addition, as you level up classes, you can exchange coins for new abilities using b!train.\n\n"
            "**Fun With (Against?) Friends**\n\nThese abilities and certain items can be used in combat between players and against NPCs. If you want to challenge another player to a duel, use b!duel @user1 @user2 ... or b!groupduel @user1 @user2 ...\n\n"
            "You can also send items, coins, and messages to other players using b!mail @user -- a useful system for trading and potentially acquiring rare items you both lack.\n\n"
            "Last, but most certainly not least, you can challenge other players to a friendly game of knucklebones with b!knucklebones @otherplayer. Optionally, you can add a bet on who will win by doing b!knucklebones @otherplayer [insert amount of coins to bet here].\n\n"
            "There's much more to do and even more yet to come! So have fun, join the adventure, and explore this little evolving world together."
        ) 

        embed = Embed(title="Welcome, Adventurer!", description=description)
        await context.send(embed=embed)

    @commands.command(name="house", help="Visit your house in the village", aliases=["home"])
    async def house_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your house.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your house.")
            return
        
        house_view: HouseView = HouseView(self._bot, self._database, context.guild.id, context.author, context)
        await context.send(embed=house_view.get_initial_embed(), view=house_view)

    @commands.command(name="garden", help="Visit your home's garden", hidden=True)
    async def garden_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your garden.")
            return

        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your garden.")
            return

        companion_result_str: str = ""
        if random.random() < 0.01 + (0.01 * author_player.get_combined_attributes().luck) / 10:
            companions = author_player.get_companions()
            if CompanionKey.BlueFlitterwingButterfly not in companions.companions.keys():
                companions.companions[CompanionKey.BlueFlitterwingButterfly] = BlueFlitterwingButterflyCompanion()
                companions.companions[CompanionKey.BlueFlitterwingButterfly].set_id(author_player.get_id())
                companion_result_str += "\n\nIn your garden, flittering about the plants, you can see a lovely blue butterfly which comes to rest on your hand. A new companions has been added in b!companions."

                author_player.get_stats().companions.companions_found += 1

        view = GardenView(self._bot, self._database, context.guild.id, context.author, None)
        embed = view.get_embed_for_intent(companion_result_str)
        await context.send(embed=embed, view=view)

    @commands.command(name="study", help="Enter your home's study", hidden=True)
    async def study_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your study.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your study.")
            return
        
        view = StudyView(self._bot, self._database, context.guild.id, context.author, None)
        embed = view.get_embed_for_intent()
        await context.send(embed=embed, view=view)

    @commands.command(name="workshop", help="Enter your home's workshop", hidden=True)
    async def workshop_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your workshop.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your workshop.")
            return
        
        view = WorkshopView(self._bot, self._database, context.guild.id, context.author, None)
        embed = view.get_embed_for_intent()
        await context.send(embed=embed, view=view)

    @commands.command(name="alchemychamber", help="Enter your home's alchemy chamber", aliases=["alchemy"], hidden=True)
    async def alchemy_chamber_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your alchemy chamber.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your alchemy chamber.")
            return
        
        view = AlchemyChamberView(self._bot, self._database, context.guild.id, context.author, None)
        embed = view.get_embed_for_intent()
        await context.send(embed=embed, view=view)

    @commands.command(name="kitchen", help="Enter your home's kitchen", hidden=True)
    async def kitchen_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your kitchen.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your kitchen.")
            return
        
        view = KitchenView(self._bot, self._database, context.guild.id, context.author, None)
        embed = view.get_embed_for_intent()
        await context.send(embed=embed, view=view)

    @commands.command(name="storage", help="Enter your home's storage", hidden=True)
    async def storage_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your storage.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run:
            await context.send(f"You're on an adventure and can't visit your storage.")
            return
        
        view = StorageView(self._bot, self._database, context.guild.id, context.author, None, context)
        embed = view.get_embed_for_intent()
        await context.send(embed=embed, view=view)

    @commands.command(name="companions", help="See your acquired companions and interact with them", aliases=["pets"])
    async def companions_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        
        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't visit your companions.")
            return
        
        if author_player.get_dungeon_run().in_dungeon_run and not author_player.get_dungeon_run().in_rest_area:
            await context.send(f"You're on an adventure and haven't reached a rest area where you can visit your companions.")
            return
        
        companions_view = PlayerCompanionsView(self._bot, self._database, context.guild.id, context.author, context)
        embed = companions_view.get_initial_embed()
        await context.send(embed=embed, view=companions_view)

    @commands.command(name="companionbattle", help="Gather players to choose teams for a companion battle", aliases=["petbattle"])
    async def companion_battle_handler(self, context: commands.Context, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        if users is None:
            await context.send("You need to @ a member to use b!companionbattle.")
            return

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times in a single companion battle.")
            return

        if context.author in users:
            await context.send("You can't challenge yourself to a companion battle.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't challenge a bot to a companion battle.")
            return
        
        if len(users) != len(set(users)):
            await context.send("You can't challenge a player more than once in a single companion battle.")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't start a companion battle.")
            return

        challenged_players: List[Player] = [self._get_player(context.guild.id, user.id) for user in users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send(f"At least one of those players is in a duel.")
            return
        
        if any(player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure.")
            return

        if any(player.get_companions().current_companion is None for player in [self._get_player(context.guild.id, context.author.id), *challenged_players]):
            await context.send(f"At least one of those players (or yourself) doesn't have a chosen companion.")
            return

        companion_battle = CompanionBattleView(self._bot, self._database, context.guild.id, [context.author, *users])

        await context.send(embed=companion_battle.get_info_embed(), view=companion_battle)

    @commands.command(name="forest", help="Gather players to enter the mysterious forest")
    async def forest_handler(self, context: commands.Context, section: ForestSection | None, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        users = [] if users is None else users

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times for an adventure.")
            return

        if context.author in users:
            await context.send("You're automatically the group leader for the adventure and don't need to include yourself.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't bring a bot on an adventure.")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't start an adventure.")
            return

        challenged_players: List[Player] = [self._get_player(context.guild.id, user.id) for user in users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send(f"At least one of those players is in a duel.")
            return
        
        if any(player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure.")
            return

        if any(player.get_expertise().hp != player.get_expertise().max_hp for player in challenged_players) or author_player.get_expertise().hp != author_player.get_expertise().max_hp:
            await context.send("At least one of those players isn't at full health.")
            return
        
        if section is not None:
            if any(player.get_dungeon_run().forest_best_act < section for player in [author_player, *challenged_players]):
                await context.send(f"At least one of those players has not reached that section of the forest before.")
                return

        forest = ForestDungeonEntranceView(self._bot, self._database, context.guild.id, [context.author, *users], section)

        await context.send(embed=forest.get_initial_embed(), view=forest)

    @commands.command(name="ocean", help="Gather players to enter the depths of the ocean")
    async def ocean_handler(self, context: commands.Context, section: OceanSection | None, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        users = [] if users is None else users

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times for an adventure.")
            return

        if context.author in users:
            await context.send("You're automatically the group leader for the adventure and don't need to include yourself.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't bring a bot on an adventure.")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't start an adventure.")
            return

        challenged_players: List[Player] = [self._get_player(context.guild.id, user.id) for user in users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send(f"At least one of those players is in a duel.")
            return
        
        if any(player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure.")
            return

        if any(player.get_expertise().hp != player.get_expertise().max_hp for player in challenged_players) or author_player.get_expertise().hp != author_player.get_expertise().max_hp:
            await context.send("At least one of those players isn't at full health.")
            return
        
        if section is not None:
            if any(player.get_dungeon_run().ocean_best_act < section for player in [author_player, *challenged_players]):
                await context.send(f"At least one of those players has not reached that section of the ocean before.")
                return

        ocean = OceanDungeonEntranceView(self._bot, self._database, context.guild.id, [context.author, *users], section)

        await context.send(embed=ocean.get_initial_embed(), view=ocean)

    @commands.command(name="underworld", help="Gather players to enter the sunless underworld")
    async def underworld_handler(self, context: commands.Context, section: UnderworldSection | None, users: commands.Greedy[User]=None):
        assert(context.guild is not None)

        users = [] if users is None else users

        if len(set(users)) != len(users):
            await context.send("You can't @ another player multiple times for an adventure.")
            return

        if context.author in users:
            await context.send("You're automatically the group leader for the adventure and don't need to include yourself.")
            return
            
        if any(user.bot for user in users):
            await context.send("You can't bring a bot on an adventure.")
            return
            
        self._check_member_and_guild_existence(context.guild.id, context.author.id)
        for user in users:
            self._check_member_and_guild_existence(context.guild.id, user.id)

        author_player: Player = self._get_player(context.guild.id, context.author.id)
        author_dueling: Dueling = author_player.get_dueling()
        if author_dueling.is_in_combat:
            await context.send(f"You're in a duel and can't start an adventure.")
            return

        challenged_players: List[Player] = [self._get_player(context.guild.id, user.id) for user in users]
        if any(player.get_dueling().is_in_combat for player in challenged_players):
            await context.send(f"At least one of those players is in a duel.")
            return
        
        if any(player.get_dungeon_run().in_dungeon_run for player in [author_player, *challenged_players]):
            await context.send(f"At least one of those players is on an adventure.")
            return

        if any(player.get_expertise().hp != player.get_expertise().max_hp for player in challenged_players) or author_player.get_expertise().hp != author_player.get_expertise().max_hp:
            await context.send("At least one of those players isn't at full health.")
            return
        
        if section is not None:
            if any(player.get_dungeon_run().underworld_best_act < section for player in [author_player, *challenged_players]):
                await context.send(f"At least one of those players has not reached that section of the underworld before.")
                return

        underworld = UnderworldDungeonEntranceView(self._bot, context, self._database, context.guild.id, [context.author, *users], section)

        await context.send(embed=underworld.get_initial_embed(), view=underworld)

    @commands.command(name="settings", help="Adjust your gameplay settings")
    async def settings_handler(self, context: commands.Context):
        assert(context.guild is not None)

        self._check_member_and_guild_existence(context.guild.id, context.author.id)

        settings_view = SettingsView(self._bot, self._database, context.guild.id, context.author)

        await context.send(embed=settings_view.get_initial_embed(), view=settings_view)


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Adventures(bot))
