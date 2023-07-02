from __future__ import annotations

import discord
import features.stories.forest.forest as forest
import random

from features.shared.enums import RoomType
from features.stories.dungeon_run import DungeonRun
from features.stories.story import MYSTERY_COMBAT_BASE_PROB, MYSTERY_COMBAT_PROB_INCREASE, MYSTERY_ROOM_PROB, MYSTERY_SHOPKEEP_BASE_PROB, MYSTERY_SHOPKEEP_PROB_INCREASE, MYSTERY_TREASURE_BASE_PROB, MYSTERY_TREASURE_PROB_INCREASE, REST_ROOM_PROB, SHOPKEEP_ROOM_PROB, Story

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot
    from features.player import Player

# -----------------------------------------------------------------------------
# ROOM SELECTION VIEW
# -----------------------------------------------------------------------------

class RoomButton(discord.ui.Button):
    def __init__(self, icon: str, next_view: discord.ui.View, room_type: RoomType):
        super().__init__(style=discord.ButtonStyle.secondary, emoji=icon)

        self._next_view = next_view
        self._room_type = room_type

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: ForestRoomSelectionView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't select the next room!", view=view)
            return
    
        if self._room_type == RoomType.Combat:
            view.get_dungeon_run().combat_encounters += 1
        elif self._room_type == RoomType.Shopkeep:
            view.get_dungeon_run().shopkeeps_encountered += 1

            for player in view.get_players():
                player.get_dungeon_run().in_rest_area = True
        elif self._room_type == RoomType.Treasure:
            view.get_dungeon_run().treasure_rooms_encountered += 1
        elif self._room_type == RoomType.Event:
            view.get_dungeon_run().events_encountered += 1
        elif self._room_type == RoomType.Rest:
            view.get_dungeon_run().rests_taken += 1

            for player in view.get_players():
                player.get_dungeon_run().in_rest_area = True
        
        view.get_dungeon_run().rooms_explored += 1
        view.get_dungeon_run().rooms_until_boss -= 1

        initial_info: discord.Embed = self._next_view.get_initial_embed() # type: ignore

        await interaction.response.edit_message(embed=initial_info, view=self._next_view, content=None)


class ForestRoomSelectionView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.setup_forest_rooms()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def setup_forest_rooms(self):
        if self._dungeon_run.rooms_until_boss == -1:
            room = forest.ForestStory.generate_boss_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
            self.add_item(RoomButton("\u2620\uFE0F", room, RoomType.Boss))
            return

        if self._dungeon_run.rooms_until_boss == 0:
            room = forest.ForestStory.generate_rest_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
            self.add_item(RoomButton("\uD83D\uDD25", room, RoomType.Rest))
            return
        
        num_rooms: int = random.randint(2, 3)

        for _ in range(num_rooms):
            room_rand_gen = random.random()
            if room_rand_gen < SHOPKEEP_ROOM_PROB:
                icon = "\uD83E\uDE99"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_shopkeep_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room, RoomType.Shopkeep))

            elif room_rand_gen < REST_ROOM_PROB:
                icon = "\uD83D\uDD25"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_rest_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room, RoomType.Rest))

            elif room_rand_gen < MYSTERY_ROOM_PROB:
                icon = "\u2753"

                mystery_room_rand_gen = random.random()

                if mystery_room_rand_gen < MYSTERY_TREASURE_BASE_PROB + MYSTERY_TREASURE_PROB_INCREASE * self._dungeon_run.num_mystery_without_treasure:
                    self._dungeon_run.num_mystery_without_treasure = 0
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_treasure_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room, RoomType.Treasure))
                elif mystery_room_rand_gen < MYSTERY_SHOPKEEP_BASE_PROB + MYSTERY_SHOPKEEP_PROB_INCREASE * self._dungeon_run.num_mystery_without_shopkeep:
                    self._dungeon_run.num_mystery_without_shopkeep = 0
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_treasure += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_shopkeep_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room, RoomType.Shopkeep))
                elif mystery_room_rand_gen < MYSTERY_COMBAT_BASE_PROB + MYSTERY_COMBAT_PROB_INCREASE * self._dungeon_run.num_mystery_without_combat:
                    self._dungeon_run.num_mystery_without_combat = 0
                    self._dungeon_run.num_mystery_without_treasure += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_combat_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room, RoomType.Combat))
                else:
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_treasure += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_event_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room, RoomType.Event))
            else:
                icon = "\u2694\uFE0F"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_combat_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room, RoomType.Combat))

    def get_initial_embed(self):
        return discord.Embed(title="The Path", description=f"The path before you splits into multiple. Which will you take?")

    def get_group_leader(self):
        return self._group_leader
    
    def get_dungeon_run(self):
        return self._dungeon_run
    
    def get_players(self):
        return [self._get_player(user.id) for user in self._users]
