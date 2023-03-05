from __future__ import annotations

import discord
import features.stories.forest.forest as forest
import random

from features.shared.enums import ForestSection, OceanSection, UnderworldSection
from features.stories.story import MYSTERY_COMBAT_BASE_PROB, MYSTERY_COMBAT_PROB_INCREASE, MYSTERY_ROOM_PROB, MYSTERY_SHOPKEEP_BASE_PROB, MYSTERY_SHOPKEEP_PROB_INCREASE, MYSTERY_TREASURE_BASE_PROB, MYSTERY_TREASURE_PROB_INCREASE, REST_ROOM_PROB, SHOPKEEP_ROOM_PROB, Story

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from bot import BenjaminBowtieBot

# -----------------------------------------------------------------------------
# DUNGEON RUN VARIABLES
# -----------------------------------------------------------------------------

class DungeonRun():
    def __init__(self, dungeon_type: Story, rooms_until_boss: int, section: ForestSection | OceanSection | UnderworldSection):
        self.dungeon_type = dungeon_type
        self.rooms_until_boss = rooms_until_boss
        self.section = section
        
        self.num_mystery_without_combat: int = 0
        self.num_mystery_without_treasure: int = 0
        self.num_mystery_without_shopkeep: int = 0

        # Mostly for stats, tracked across the entire run
        self.rooms_explored: int = 0
        self.combat_encounters: int = 0
        self.treasure_rooms_encountered: int = 0
        self.shopkeeps_encountered: int = 0
        self.events_encountered: int = 0
        self.rests_taken: int = 0
        self.bosses_defeated: int = 0

# -----------------------------------------------------------------------------
# ROOM SELECTION VIEW
# -----------------------------------------------------------------------------

class RoomButton(discord.ui.Button):
    def __init__(self, icon: str, next_view: discord.ui.View):
        super().__init__(style=discord.ButtonStyle.green, emoji=icon)

        self._next_view = next_view

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: RoomSelectionView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(embed=view.get_initial_embed(), content="Error: You aren't the group leader and can't select the next room!", view=view)
            return
        
        initial_info: discord.Embed = self._next_view.get_initial_embed() # type: ignore

        await interaction.response.edit_message(embed=initial_info, view=self._next_view, content=None)


class RoomSelectionView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run

        self.setup_rooms()

    def setup_rooms(self):
        if self._dungeon_run.rooms_until_boss == 0:
            room = forest.ForestStory.generate_rest_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
            self.add_item(RoomButton("\uD83D\uDD25", room))
            return
        
        num_rooms: int = random.randint(2, 3)

        for _ in range(num_rooms):
            room_rand_gen = random.random()
            if room_rand_gen < SHOPKEEP_ROOM_PROB:
                icon = "\uD83E\uDE99"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_shopkeep_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room))

            elif room_rand_gen < REST_ROOM_PROB:
                icon = "\uD83D\uDD25"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_rest_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room))

            elif room_rand_gen < MYSTERY_ROOM_PROB:
                icon = "\u2753"

                mystery_room_rand_gen = random.random()

                if mystery_room_rand_gen < MYSTERY_TREASURE_BASE_PROB + MYSTERY_TREASURE_PROB_INCREASE * self._dungeon_run.num_mystery_without_treasure:
                    self._dungeon_run.num_mystery_without_treasure = 0
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_treasure_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room))
                elif mystery_room_rand_gen < MYSTERY_SHOPKEEP_BASE_PROB + MYSTERY_SHOPKEEP_PROB_INCREASE * self._dungeon_run.num_mystery_without_shopkeep:
                    self._dungeon_run.num_mystery_without_shopkeep = 0
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_treasure += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_shopkeep_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room))
                elif mystery_room_rand_gen < MYSTERY_COMBAT_BASE_PROB + MYSTERY_COMBAT_PROB_INCREASE * self._dungeon_run.num_mystery_without_combat:
                    self._dungeon_run.num_mystery_without_combat = 0
                    self._dungeon_run.num_mystery_without_treasure += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_combat_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room))
                else:
                    self._dungeon_run.num_mystery_without_combat += 1
                    self._dungeon_run.num_mystery_without_treasure += 1
                    self._dungeon_run.num_mystery_without_shopkeep += 1

                    if self._dungeon_run.dungeon_type == Story.Forest:
                        room = forest.ForestStory.generate_event_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                        self.add_item(RoomButton(icon, room))
            else:
                icon = "\u2694\uFE0F"

                if self._dungeon_run.dungeon_type == Story.Forest:
                    room = forest.ForestStory.generate_combat_room(self._bot, self._database, self._guild_id, self._users, self._dungeon_run)
                    self.add_item(RoomButton(icon, room))

    def get_initial_embed(self):
        return discord.Embed(title="The Path", description=f"The path before you splits into multiple. Which will you take?")

    def get_group_leader(self):
        return self._group_leader
