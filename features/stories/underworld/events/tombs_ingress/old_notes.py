from __future__ import annotations

import discord
import random

from bot import BenjaminBowtieBot
from discord.embeds import Embed
from features.player import Player
from features.stories.dungeon_run import DungeonRun
from features.stories.underworld_room_selection import UnderworldRoomSelectionView

from typing import List


class ContinueButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label="Continue")

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        view: OldNotesView = self.view

        if interaction.user.id != view.get_group_leader().id:
            await interaction.response.edit_message(content="You aren't the group leader and can't continue to the next room.")
            return

        for user in view.get_users():
            await user.send(content=view.found_scrap)

        room_selection_view = UnderworldRoomSelectionView(view.get_bot(), view.get_database(), view.get_guild_id(), view.get_users(), view.get_dungeon_run())
        initial_info: Embed = room_selection_view.get_initial_embed()

        await interaction.response.edit_message(embed=initial_info, view=room_selection_view, content=None)


class OldNotesView(discord.ui.View):
    def __init__(self, bot: BenjaminBowtieBot, database: dict, guild_id: int, users: List[discord.User], dungeon_run: DungeonRun):
        super().__init__(timeout=None)

        self._bot = bot
        self._database = database
        self._guild_id = guild_id
        self._users = users
        self._group_leader = users[0]
        self._dungeon_run = dungeon_run
        
        self._scraps = [
            "Legends spoke of a falling star, which had marked the world several kilometers from here. Time had covered the crater and time had brought many rumors to our doorstep. But the sudden appearance of a wishing well in the middle of an empty forest gave us all concern.",
            "We suspect it to be a servant of some form in service to one of the things from the Dark Between the Stars. Clearly it’s won some reverence from those who live here, though whether by overwhelming their minds or some other tactic I cannot say.",
            "This city is a display of opulence, perhaps transported between here and the surface by wielders of arcana? People from all walks of life have made this place their home and seem to live in relative harmony -- were it not for the dangerous rituals we've heard mentioned.",
            "The mists seem to be a natural occurrence of the caves -- perhaps this location was chosen specifically for this property? They also interact with mana in a way I've never seen before in any phenomenon; they're almost like a mirror or conduit, the full extent of which is unclear to me."
        ]
        self.found_scrap = random.choice(self._scraps)

        self._display_initial_buttons()

    def _get_player(self, user_id: int) -> Player:
        return self._database[str(self._guild_id)]["members"][str(user_id)]

    def get_initial_embed(self):
        return Embed(title="Old Notes", description=f"Along the path, you find a section of an old journal, worn and weathered but still intact. There's no name you can glean, but the writing is in the common tongue...")

    def _display_initial_buttons(self):
        self.clear_items()
        self.add_item(ContinueButton())

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
