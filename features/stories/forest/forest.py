import discord
import random

import features.companions.companion

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.npcs.mysterious_merchant import MysteriousMerchantView
from features.player import Player
from features.shared.enums import CompanionKey, ForestSection
from features.stories.dungeon_run import DungeonRun, RoomSelectionView
from features.stories.forest.treasure.quiet_grove_treasure import QuietGroveTreasureRoomView
from features.stories.forest.treasure.screaming_copse_treasure import ScreamingCopseTreasureRoomView
from features.stories.forest.treasure.whispering_woods_treasure import WhisperingWoodsTreasureRoomView
from features.stories.story import Story

from typing import List

# -----------------------------------------------------------------------------
# FOREST REST VIEW
# -----------------------------------------------------------------------------

class ForestRestButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(style=discord.ButtonStyle.blurple, label="Rest", row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestRestView = self.view
        if interaction.user not in view.rested_users:
            response = view.rest(interaction.user)
            await interaction.response.edit_message(content=None, embed=response, view=view)


class ForestRestView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        # Each player can only get one rest per rest room
        self.rested_users: List[discord.User] = []
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self, additional_info: str=""):
        return Embed(title="A Warm Bonfire", description=f"You all gather around a fire and rest for a moment among the trees.{additional_info}")

    def _display_initial_buttons(self):
        self.clear_items()

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def rest(self, user: discord.User):
        player = self._get_player(user.id)
        player_expertise = player.get_expertise()
        player_dueling = player.get_dueling()

        player_dueling.status_effects = []
        player_expertise.heal(int(player_expertise.max_hp / 2))
        player_expertise.restore_mana(int(player_expertise.max_mana / 2))

        companion_result_str: str = ""
        if random.random() < 0.0002:
            companions = player.get_companions()
            if random.random() < 0.5:
                if CompanionKey.VoidseenCat not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenCat] = features.companions.companion.VoidseenCatCompanion()
                    companions.companions[CompanionKey.VoidseenCat].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small cat, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It purrs and calms you, driving away the fear you felt from the dreams."

                    player.get_stats().companions.companions_found += 1
            else:
                if CompanionKey.VoidseenPup not in companions.companions.keys():
                    companions.companions[CompanionKey.VoidseenPup] = features.companions.companion.VoidseenPupCompanion()
                    companions.companions[CompanionKey.VoidseenPup].set_id(player.get_id())
                    companion_result_str += "\n\nIn your sleep, amid nightmares that seem far too real, you awake with a start to find something curled up beside your feet. A small pup, fur dark as the night, with beautiful eyes shimmering white with shards of color dancing in the irises. It looks up at you, one ear floppy the other pointed straight up, then nuzzles you with its nose. Your newfound companion brings a profound sense of calm, driving away the terrifying dreams."

                    player.get_stats().companions.companions_found += 1

        self.rested_users.append(user)

        return self.get_initial_embed(companion_result_str)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_group_leader(self):
        return self._group_leader

    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# FOREST DUNGEON ENTRANCE VIEW
# -----------------------------------------------------------------------------

class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Start")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestDungeonEntranceView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't start this adventure!", view=view)
            return
        
        if view.any_in_duels_currently():
            await interaction.response.edit_message(embed=None, view=None, content="At least one person is in a duel. You cannot start this adventure.")
            return
        
        room_select_view: RoomSelectionView = RoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_select_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_select_view, content=None)


class ForestDungeonEntranceView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User]):
        super().__init__(timeout=900)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = DungeonRun(Story.Forest, 20, ForestSection.QuietGrove)
        
        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="The Forest", description=f"Standing before the entrance to the old woods, your party stares down the path into the seemingly endless expanse of trees.\n\nYour group leader is {self._group_leader.display_name}. When your party is ready, you may enter the forest.")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(StartButton())

    def any_in_duels_currently(self):
        return any(self._get_player(user.id).get_dueling().is_in_combat for user in self._users)

    def get_bot(self):
        return self._bot

    def get_users(self):
        return self._users

    def get_database(self):
        return self._database

    def get_guild_id(self):
        return self._guild_id

    def get_group_leader(self):
        return self._group_leader

    def get_dungeon_run(self):
        return self._dungeon_run

# -----------------------------------------------------------------------------
# FOREST STORY CLASS
# -----------------------------------------------------------------------------

class ForestStory():
    def __init__(self):
        pass

    @staticmethod
    def generate_shopkeep_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return MysteriousMerchantView(bot, database, guild_id, users)

    @staticmethod
    def generate_rest_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return ForestRestView(bot, database, guild_id, users, dungeon_run)
    
    @staticmethod
    def generate_treasure_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        if dungeon_run.section == ForestSection.ScreamingCopse:
            return ScreamingCopseTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        elif dungeon_run.section == ForestSection.WhisperingWoods:
            return WhisperingWoodsTreasureRoomView(bot, database, guild_id, users, dungeon_run)
        else:
            return QuietGroveTreasureRoomView(bot, database, guild_id, users, dungeon_run)

    @staticmethod
    def generate_combat_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return discord.ui.View()

    @staticmethod
    def generate_event_room(bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        return discord.ui.View()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        pass
