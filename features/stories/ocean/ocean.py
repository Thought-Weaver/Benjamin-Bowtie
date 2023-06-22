from __future__ import annotations

import discord

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun

from typing import List

# -----------------------------------------------------------------------------
# OCEAN DEFEAT VIEW
# -----------------------------------------------------------------------------

class OceanDefeatView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def _generate_run_info(self):
        info_str: str = (
            f"Rooms Explored: {self._dungeon_run.rooms_explored}\n\n"
            f"Combat Encounters: {self._dungeon_run.combat_encounters}\n"
            f"Treasure Rooms Found: {self._dungeon_run.treasure_rooms_encountered}\n"
            f"Shopkeeps Met: {self._dungeon_run.shopkeeps_encountered}\n"
            f"Events Encountered: {self._dungeon_run.events_encountered}\n\n"
            f"Rests Taken: {self._dungeon_run.rests_taken}\n"
            f"Bosses Defeated: {self._dungeon_run.bosses_defeated}"
        )
        return info_str

    def _update_player_stats(self):
        for user in self._users:
            player = self._get_player(user.id)
            ps = player.get_stats().dungeon_runs

            ps.ocean_rooms_explored += self._dungeon_run.rooms_explored
            ps.ocean_combat_encounters += self._dungeon_run.combat_encounters
            ps.ocean_treasure_rooms_encountered += self._dungeon_run.treasure_rooms_encountered
            ps.ocean_shopkeeps_encountered += self._dungeon_run.shopkeeps_encountered
            ps.ocean_events_encountered += self._dungeon_run.events_encountered
            ps.ocean_rests_taken += self._dungeon_run.rests_taken
            ps.ocean_bosses_defeated += self._dungeon_run.bosses_defeated
            ps.ocean_adventures_played += 1

    def get_initial_embed(self):
        post_run_info_str: str = self._generate_run_info()
        
        self._update_player_stats()
        
        return Embed(title="To the Surface", description=f"With your party defeated, you all flee the ocean barely alive.\n\n᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆\n\n{post_run_info_str}")

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
# OCEAN STORY CLASS
# -----------------------------------------------------------------------------

class OceanStory():
    def __init__(self):
        self.first_to_find_maybe_fish_id: int = -1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state: dict):
        self.first_to_find_maybe_fish_id = state.get("first_to_find_maybe_fish_id", -1)
